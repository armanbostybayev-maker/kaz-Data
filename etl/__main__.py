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
    if category!="demography": print(json.dumps({"category":category,"status":"adapter_not_configured","loaded":0})); return
    from etl.sources.demography.population import parse
    from etl.validation.rules import validate_values
    if not KATO_CSV.exists(): kato()
    data,unmatched=parse(ROOT/"data/raw/stat/demography/population_yearly_2026-08-11.csv",KATO_CSV)
    data.to_csv(ROOT/"data/processed/population.csv",index=False,encoding="utf-8-sig")
    unmatched.to_csv(ROOT/"data/reports/population_unmatched.csv",index=False,encoding="utf-8-sig")
    validate_values(data).to_csv(ROOT/"data/reports/data_quality_issues.csv",index=False,encoding="utf-8-sig")
    from etl.load import load_values
    db_rows = load_values(ROOT/"data/processed/population.csv")
    print(json.dumps({"normalized":len(data),"database_rows":db_rows,"unmatched":len(unmatched)},ensure_ascii=False))


def main():
    p=argparse.ArgumentParser(prog="python -m etl"); sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("kato");sub.add_parser("geography");sub.add_parser("validate");sub.add_parser("status");sub.add_parser("all")
    s=sub.add_parser("stat");s.add_argument("--category",required=True)
    a=p.parse_args()
    if a.command=="kato": kato()
    elif a.command=="geography": geography()
    elif a.command=="stat": stat(a.category)
    elif a.command=="all": kato(); geography(); stat("demography")
    elif a.command=="validate": stat("demography")
    else: print(json.dumps({"kato_raw":KATO_RAW.exists(),"kato_processed":KATO_CSV.exists()}))

if __name__=="__main__":main()
