from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from etl.normalization.text import normalize_name, parse_number
from etl.sources.registry import CATEGORY_NAMES, SOURCES, csv_url

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/stat"
PROCESSED = ROOT / "data/processed/stat"
PUBLIC = ROOT / "apps/frontend/public/data"
REPORTS = ROOT / "data/reports"
CATALOG_PATH = ROOT / "data/catalog/stat_gov_kz_sources.json"
# Deterministic for unchanged official releases, so scheduled update jobs do not
# create commits solely because the clock changed.
GENERATED = max(s["updated"] for s in SOURCES) + "T00:00:00+00:00"


def territory_key(name: str) -> str:
    lower = (name or "").casefold().strip()
    kind = "region" if "область" in lower else "city" if lower.startswith("г.") else "territory"
    return f"{kind}:{normalize_name(name)}"


def period_label(period: str, dat: str) -> str:
    period = str(period)
    if "кварт" in str(dat).casefold() or "(кв" in str(dat).casefold():
        month = int(period[4:6]); return f"{period[:4]}-Q{max(1, math.ceil(month / 3))}"
    if "месяц" in str(dat).casefold():
        return f"{period[:4]}-{period[4:6]}"
    return period[:4]


def clean_value(raw: object, plausible_max: float, divisor: float = 1) -> float | None:
    value = parse_number(raw)
    if value is None: return None
    # BNS CSV serialization may append decimal zero groups (e.g. 5332.7 as
    # 5 332 700 000). Remove only groups of exactly 1000 above a documented
    # source-unit ceiling; original raw text remains preserved.
    while abs(value) > plausible_max and value and abs(value / 1000) >= 0.001:
        value /= 1000
    value /= divisor
    return round(value, 4)


def current_regions() -> tuple[pd.DataFrame, dict[str, str]]:
    kato = pd.read_csv(ROOT / "data/processed/kato.csv", dtype=str).fillna("")
    regions = kato[kato.admin_level.astype(int).eq(1)].copy()
    lookup = {territory_key(r.name_ru): r.kato for r in regions.itertuples()}
    lookup["city:нур султан"] = "710000000"
    return regions, lookup


def parse_source(source: dict, lookup: dict[str, str]) -> tuple[pd.DataFrame, list[dict]]:
    path = RAW / source["file"]
    raw = pd.read_csv(path, sep="\t", dtype=str)
    territory_col = next(c for c in raw.columns if c.startswith("КАТО(") and not c.startswith("L"))
    data = raw.copy()
    for column, expected in source.get("filters", {}).items():
        data = data[data[column].fillna("").str.casefold().eq(expected.casefold())]
    data["normalized_name"] = data[territory_col].fillna("").map(normalize_name)
    data["match_key"] = data[territory_col].fillna("").map(territory_key)
    data["kato"] = data.match_key.map(lookup)
    report = []
    for name, group in data.groupby(territory_col, dropna=False):
        kato = group.kato.dropna().iloc[0] if group.kato.notna().any() else ""
        report.append({
            "source_name": str(name or ""), "normalized_name": normalize_name(str(name or "")),
            "matched_kato": kato, "matched_name": "", "method": "normalized_name_and_admin_type" if kato else "none",
            "confidence": "1.0" if kato else "0", "status": "confirmed" if kato else "unmatched",
            "indicator": source["indicator"],
        })
    data = data[data.kato.notna()].copy()
    data["period"] = [period_label(p, d) for p, d in zip(data.PERIOD, data.DAT)]
    data["value"] = data.VAL.map(lambda x: clean_value(x, source["plausible_max"], source.get("output_divisor", 1)))
    data = data[data.value.notna()][["kato", "period", "value"]]
    # Duplicates after aggregate filters indicate an unsafe source selection.
    dup = data.duplicated(["kato", "period"], keep=False)
    if dup.any():
        examples = data[dup].head(5).to_dict("records")
        raise ValueError(f"{source['indicator']}: duplicate region/period rows: {examples}")
    return data.sort_values(["period", "kato"]), report


def payload(source: dict, data: pd.DataFrame, *, derived=False, formula=None, inputs=None) -> dict:
    values = {}
    for period, rows in data.groupby("period"):
        values[str(period)] = {str(r.kato): r.value for r in rows.itertuples()}
    return {
        "indicator": source["indicator"], "unit": source["unit"],
        "source_name": "Бюро национальной статистики Республики Казахстан",
        "source_page": source["page"], "source_download": csv_url(source["element"]) if source.get("element") else None,
        "source_updated_at": source.get("updated"), "etl_generated_at": GENERATED,
        "periodicity": "quarter" if any("-Q" in p for p in values) else "month" if any(len(p) == 7 for p in values) else "year",
        "territorial_level": "region", "available_levels": ["region"],
        "territorial_reference_date": "current KATO 2026-09-18; historical boundaries are not redistributed",
        "geometry_reference_date": "2024-01", "derived": derived,
        **({"formula": formula, "inputs": inputs} if derived else {}),
        "periods": sorted(values), "values": values,
    }


def write_payload(source: dict, data: pd.DataFrame, **kwargs) -> dict:
    out = payload(source, data, **kwargs)
    path = PUBLIC / source["category"] / f"{source['indicator']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    PROCESSED.mkdir(parents=True, exist_ok=True)
    data.to_csv(PROCESSED / f"{source['indicator']}.csv", index=False, encoding="utf-8-sig")
    return out


def derive(base: dict[str, tuple[dict, pd.DataFrame]], regions: pd.DataFrame) -> list[tuple[dict, pd.DataFrame, dict]]:
    pop_source, pop = base["population"]
    derived = []
    change = pop.copy(); change["value"] = change.groupby("kato").value.pct_change(fill_method=None) * 100
    change = change[change.value.notna()]
    derived.append((dict(pop_source, indicator="population_change_pct", name_ru="Изменение численности населения", name_kk="Халық санының өзгеруі", unit="%"), change, {"formula":"(population[t] / population[t-1] - 1) × 100", "inputs":["population"]}))
    geo = json.loads((ROOT / "data/processed/territories_adm1.geojson").read_text(encoding="utf-8"))
    areas = {str(f["properties"]["kato"]): f["properties"].get("area_km2") for f in geo["features"]}
    density = pop.copy(); density["value"] = [round(v / areas.get(str(k), math.nan), 3) if areas.get(str(k)) else None for k, v in zip(density.kato, density.value)]
    density = density[density.value.notna()]
    derived.append((dict(pop_source, indicator="population_density", name_ru="Плотность населения", name_kk="Халық тығыздығы", unit="чел./км²"), density, {"formula":"population / area_km2", "inputs":["population", "territory_geometry_area"]}))
    if "fixed_capital_investment" in base:
        inv_source, inv = base["fixed_capital_investment"]
        merged = inv.merge(pop, on=["kato", "period"], suffixes=("_inv", "_pop"))
        per = merged[["kato", "period"]].copy(); per["value"] = (merged.value_inv * 1_000_000_000 / merged.value_pop).round(2)
        derived.append((dict(inv_source, indicator="fixed_capital_investment_per_capita", name_ru="Инвестиции в основной капитал на душу населения", name_kk="Жан басына шаққандағы негізгі капиталға инвестициялар", unit="₸/чел."), per, {"formula":"fixed_capital_investment / population", "inputs":["fixed_capital_investment", "population"]}))
    return derived


def run(categories: set[str] | None = None) -> dict:
    regions, lookup = current_regions()
    selected = [s for s in SOURCES if categories is None or s["category"] in categories]
    base, matches, outputs = {}, [], []
    for source in selected:
        data, report = parse_source(source, lookup); matches.extend(report); base[source["indicator"]] = (source, data)
        outputs.append((source, write_payload(source, data)))
    if categories is None or "demography" in categories or "investment" in categories:
        required = {s["indicator"] for s in SOURCES if s["indicator"] in {"population", "fixed_capital_investment"}}
        for source in SOURCES:
            if source["indicator"] in required and source["indicator"] not in base:
                data, report = parse_source(source, lookup); base[source["indicator"]] = (source, data); matches.extend(report)
        for source, data, meta in derive(base, regions):
            if categories is None or source["category"] in categories:
                outputs.append((source, write_payload(source, data, derived=True, **meta)))
    write_reports(outputs, matches, regions)
    write_catalog(outputs)
    return {"indicators": len(outputs), "categories": sorted({s["category"] for s, _ in outputs}), "values": sum(sum(len(v) for v in p["values"].values()) for _, p in outputs)}


def write_reports(outputs, matches, regions):
    REPORTS.mkdir(parents=True, exist_ok=True)
    names = dict(zip(regions.kato, regions.name_ru))
    for row in matches: row["matched_name"] = names.get(row["matched_kato"], "")
    fields = ["indicator", "source_name", "normalized_name", "matched_kato", "matched_name", "method", "confidence", "status"]
    with (REPORTS / "statistics_kato_match.csv").open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields); w.writeheader(); w.writerows(matches)
    coverage = []
    expected = len(regions)
    for source, data in outputs:
        for period, values in data["values"].items():
            loaded = len(values); pct = round(loaded / expected * 100, 1)
            coverage.append({"indicator":source["indicator"], "level":"region", "period":period,
                "expected_territories":expected, "loaded_territories":loaded, "matched":loaded,
                "unmatched":expected-loaded, "coverage_pct":pct, "status":"ok" if pct == 100 else "partial"})
    with (REPORTS / "indicator_coverage.csv").open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=coverage[0].keys()); w.writeheader(); w.writerows(coverage)
    (PUBLIC / "coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def write_catalog(outputs):
    categories = []
    for category, label in CATEGORY_NAMES.items():
        indicators = []
        for source, data in outputs:
            if source["category"] != category: continue
            indicators.append({"id":source["indicator"], "slug":source["indicator"], "name_ru":source["name_ru"], "name_kk":source["name_kk"],
                "description":source["name_ru"], "category":category, "unit":data["unit"], "available_levels":["region"],
                "periodicity":data["periodicity"], "available_periods":data["periods"], "source":"Бюро национальной статистики РК",
                "source_url":data["source_page"], "data_path":f"{category}/{source['indicator']}.json", "updated_at":data["source_updated_at"],
                "derived":data["derived"], "diverging":bool(source.get("diverging")), "formula":data.get("formula"), "inputs":data.get("inputs")})
        if indicators: categories.append({"id":category, "name_ru":label, "indicators":indicators})
    catalog = {"generated_at":GENERATED, "categories":categories}
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    source_catalog = []
    for source in SOURCES:
        path = PUBLIC / source["category"] / f"{source['indicator']}.json"
        periods = json.loads(path.read_text(encoding="utf-8"))["periods"] if path.exists() else []
        source_catalog.append({"indicator":source["indicator"], "name_ru":source["name_ru"], "category":source["category"],
            "source_page":source["page"], "download_url":csv_url(source["element"]), "format":"csv", "territorial_level":["region"],
            "periodicity":"quarter" if any("-Q" in p for p in periods) else "year", "first_period":periods[0] if periods else None,
            "last_period":periods[-1] if periods else None, "last_checked":GENERATED[:10], "status":"active" if periods else "unavailable"})
    CATALOG_PATH.write_text(json.dumps(source_catalog, ensure_ascii=False, indent=2), encoding="utf-8")


def validate() -> dict:
    catalog = json.loads((PUBLIC / "catalog.json").read_text(encoding="utf-8"))
    errors = []
    for category in catalog["categories"]:
        for indicator in category["indicators"]:
            data = json.loads((PUBLIC / indicator["data_path"]).read_text(encoding="utf-8"))
            if not data["periods"]: errors.append(f"{indicator['id']}: no periods")
            if set(data["periods"]) != set(data["values"]): errors.append(f"{indicator['id']}: period/value mismatch")
            if any(v is None for values in data["values"].values() for v in values.values()): errors.append(f"{indicator['id']}: null serialized")
    if errors: raise ValueError("; ".join(errors))
    return {"status":"ok", "indicators":sum(len(c["indicators"]) for c in catalog["categories"]), "errors":0}
