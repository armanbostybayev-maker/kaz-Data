import argparse, csv, json
from pathlib import Path
from etl.kato.parser import parse_kato, write_csv

ROOT=Path(__file__).resolve().parents[1]
KATO_RAW=ROOT/"data/raw/kato/KATO_2026-09-18.xlsx"
KATO_CSV=ROOT/"data/processed/kato.csv"


def kato():
    rows=parse_kato(KATO_RAW); write_csv(rows,KATO_CSV); print(json.dumps({"rows":len(rows),"output":str(KATO_CSV)},ensure_ascii=False))


def geography():
    from etl.geography.matcher import match_geometry
    if not KATO_CSV.exists(): kato()
    total={}
    for level,name in [(1,"adm1"),(2,"adm2")]:
        shp=ROOT/f"data/raw/geokz/2024-01/kaz_admbnda_{name}_2024.shp"
        counts=match_geometry(shp,KATO_CSV,ROOT/f"data/processed/territories_{name}.geojson",ROOT/f"data/reports/kato_geometry_match_{name}.csv",level)
        total[name]=counts
    combined = ROOT/"data/reports/kato_geometry_match.csv"
    with combined.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.DictWriter(target,fieldnames=["level","status","source_name","source_id","candidates","decision"]); writer.writeheader()
        for level,name in [(1,"adm1"),(2,"adm2")]:
            with (ROOT/f"data/reports/kato_geometry_match_{name}.csv").open(encoding="utf-8-sig",newline="") as source:
                for row in csv.DictReader(source): writer.writerow({"level":level,**row})
    (ROOT/"data/reports/kato_geometry_match.json").write_text(json.dumps(total,ensure_ascii=False,indent=2),encoding="utf-8")
    from etl.load import load_territories
    total["database_rows"] = load_territories([ROOT/"data/processed/territories_adm1.geojson", ROOT/"data/processed/territories_adm2.geojson"])
    print(json.dumps(total,ensure_ascii=False))


def stat(category:str):
    from etl.pipeline import run
    if not KATO_CSV.exists(): kato()
    if not (ROOT/"data/processed/territories_adm1.geojson").exists(): geography()
    print(json.dumps(run({category}),ensure_ascii=False))


def main():
    p=argparse.ArgumentParser(prog="python -m etl"); sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("kato");sub.add_parser("geography");sub.add_parser("validate");sub.add_parser("status");sub.add_parser("all");sub.add_parser("catalog");sub.add_parser("download")
    for name in ["demography","labor","income","economy","industry","investment","construction"]: sub.add_parser(name)
    s=sub.add_parser("stat");s.add_argument("--category",required=True)
    a=p.parse_args()
    if a.command=="kato": kato()
    elif a.command=="geography": geography()
    elif a.command=="stat": stat(a.category)
    elif a.command=="all":
        from etl.pipeline import run
        kato(); geography(); print(json.dumps(run(),ensure_ascii=False))
    elif a.command=="validate":
        from etl.pipeline import validate
        print(json.dumps(validate(),ensure_ascii=False))
    elif a.command=="catalog":
        from etl.pipeline import run
        print(json.dumps(run(),ensure_ascii=False))
    elif a.command=="download":
        from etl.download import download_all
        print(json.dumps(download_all(),ensure_ascii=False))
    elif a.command in ["demography","labor","income","economy","industry","investment","construction"]: stat(a.command)
    else: print(json.dumps({"kato_raw":KATO_RAW.exists(),"kato_processed":KATO_CSV.exists()}))

if __name__=="__main__":main()
