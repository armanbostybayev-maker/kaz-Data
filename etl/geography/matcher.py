from pathlib import Path
import csv
import json
import pandas as pd
import geopandas as gpd
from etl.normalization.text import normalize_name


def match_geometry(shape_path: Path, kato_csv: Path, output: Path, report: Path, level: int) -> dict[str, int]:
    geo = gpd.read_file(shape_path).to_crs(4326)
    kato = pd.read_csv(kato_csv, dtype={"kato": str, "parent_kato": str}).fillna("")
    kato = kato[kato.admin_level == level].copy()
    kato["key"] = kato.name_ru.map(normalize_name)
    by_name = kato.groupby("key").apply(lambda x: x.to_dict("records"), include_groups=False).to_dict()
    features, reviews = [], []
    counts = {"matched":0,"unmatched_geometry":0,"unmatched_kato":0,"ambiguous":0,"renamed":0,"split":0,"merged":0,"new_territory":0,"obsolete_geometry":0}
    matched_codes = set()
    for _, row in geo.iterrows():
        name_fields = [f"ADM{level}_RU", f"ADM{level}_KK", f"ADM{level}_EN"]
        source_name = next((str(row[f]) for f in name_fields if f in row and pd.notna(row[f]) and row[f]), "")
        source_kato = str(row.get("KATO", "")).split(".")[0]
        exact_code = kato[kato.kato.eq(source_kato)].to_dict("records")
        candidates = exact_code or by_name.get(normalize_name(source_name), [])
        if level == 2 and not exact_code and len(candidates) > 1:
            parent = str(row.get("ADM1_PCODE", "")).removeprefix("KZ").ljust(9, "0")
            candidates = [c for c in candidates if c["parent_kato"] == parent]
        status = "matched" if len(candidates)==1 else "ambiguous" if candidates else "unmatched_geometry"
        counts[status] += 1
        if status != "matched":
            reviews.append({"status":status,"source_name":source_name,"source_id":row.get(f"ADM{level}_PCODE",source_kato),"candidates":"|".join(c["kato"] for c in candidates),"decision":"review_required"})
            continue
        item=candidates[0]; matched_codes.add(item["kato"])
        reviews.append({"status":"matched","source_name":source_name,"source_id":row.get(f"ADM{level}_PCODE",source_kato),"candidates":item["kato"],"decision":"exact_code" if exact_code else "exact_normalized_name_parent"})
        features.append({"type":"Feature","id":item["kato"],"properties":{k:item[k] for k in ["kato","parent_kato","name_ru","name_kk","admin_level","admin_type","kato_version"]},"geometry":row.geometry.__geo_interface__})
    missing = kato[~kato.kato.isin(matched_codes)]
    counts["unmatched_kato"] = len(missing)
    reviews += [{"status":"unmatched_kato","source_name":"","source_id":"","candidates":r.kato,"decision":"review_required"} for r in missing.itertuples()]
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False),encoding="utf-8")
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w",encoding="utf-8-sig",newline="") as h:
        w=csv.DictWriter(h,fieldnames=["status","source_name","source_id","candidates","decision"]);w.writeheader();w.writerows(reviews)
    return counts
