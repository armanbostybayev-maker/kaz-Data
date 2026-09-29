import json
import os
from pathlib import Path
import pandas as pd
import psycopg


def _dsn() -> str | None:
    value = os.getenv("DATABASE_URL")
    if not value: return None
    return value.replace("postgresql+asyncpg://", "postgresql://")


def load_territories(paths: list[Path]) -> int:
    dsn = _dsn()
    if not dsn: return 0
    loaded = 0
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        for path in paths:
            for feature in json.loads(path.read_text(encoding="utf-8"))["features"]:
                p, geometry = feature["properties"], json.dumps(feature["geometry"])
                cur.execute("""INSERT INTO territories
                  (kato,parent_kato,name_ru,name_kk,admin_level,admin_type,geometry,centroid,area_km2,geometry_source,geometry_valid_at,kato_version,valid_from,is_active)
                  VALUES (%s,NULLIF(%s,''),%s,%s,%s,%s,ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)),
                  ST_Centroid(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)),ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326),6933))/1000000,
                  'geokz','2024-01-01',%s,'2024-01-01',true)
                  ON CONFLICT(kato) DO UPDATE SET name_ru=EXCLUDED.name_ru,name_kk=EXCLUDED.name_kk,parent_kato=EXCLUDED.parent_kato,
                  geometry=EXCLUDED.geometry,centroid=EXCLUDED.centroid,area_km2=EXCLUDED.area_km2,kato_version=EXCLUDED.kato_version""",
                  (p["kato"],p.get("parent_kato"),p["name_ru"],p["name_kk"],p["admin_level"],p["admin_type"],geometry,geometry,geometry,p["kato_version"]))
                loaded += 1
        conn.commit()
    return loaded


def load_values(path: Path) -> int:
    dsn = _dsn()
    if not dsn: return 0
    data = pd.read_csv(path, dtype={"kato":str,"period":str})
    loaded = 0
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        for row in data.itertuples(index=False):
            cur.execute("""INSERT INTO indicator_values
              (territory_id,indicator_id,period,year,value,unit,source_url,source_updated_at,quality_flag,boundary_valid_at)
              SELECT t.id,i.id,%s,%s,%s,%s,%s,'2026-08-11','ok','2024-01-01' FROM territories t,indicators i
              WHERE t.kato=%s AND i.slug=%s ON CONFLICT(territory_id,indicator_id,period) DO UPDATE
              SET value=EXCLUDED.value,unit=EXCLUDED.unit,source_url=EXCLUDED.source_url,loaded_at=now()""",
              (row.period,int(row.year),None if pd.isna(row.value) else float(row.value),row.unit,row.source_url,row.kato,row.indicator))
            loaded += cur.rowcount
        conn.commit()
    return loaded

