"""Build the immutable data bundle consumed by the GitHub Pages frontend."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PUBLIC = ROOT / "apps" / "frontend" / "public" / "data"


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for source, target in [
        ("territories_adm1.geojson", "territories-adm1.geojson"),
        ("territories_adm2.geojson", "territories-adm2.geojson"),
    ]:
        shutil.copyfile(PROCESSED / source, PUBLIC / target)

    with (PROCESSED / "population.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    payload = [
        {
            **row,
            "year": int(row["year"]),
            "value": float(row["value"]) if row["value"] else None,
            "quality_flag": "ok",
        }
        for row in rows
    ]
    (PUBLIC / "population.json").write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    indicators = [{
        "slug": "population",
        "name_ru": "Численность населения",
        "name_kk": "Халық саны",
        "category": "demography",
        "description": "Численность населения на начало периода",
        "unit": "человек",
        "periodicity": "annual",
        "source_url": "https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/",
        "normalization_allowed": ["absolute", "change_pct", "per_km2"],
    }]
    (PUBLIC / "indicators.json").write_text(
        json.dumps(indicators, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    print(json.dumps({"territories": [20, 205], "values": len(payload), "output": str(PUBLIC)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

