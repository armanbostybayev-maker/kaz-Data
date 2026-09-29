import json
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.db import get_db

router = APIRouter(prefix="/api")


def rows(result):
    return [dict(row._mapping) for row in result]


@router.get("/territories")
async def territories(
    level: int | None = Query(None, alias="territory_level"),
    parent_kato: str | None = None,
    search: str | None = None,
    limit: int = Query(500, le=2000),
    db: AsyncSession = Depends(get_db),
):
    query = """SELECT kato,parent_kato,name_ru,name_kk,admin_level,admin_type,area_km2,
               ST_X(centroid) lon, ST_Y(centroid) lat
               FROM territories WHERE is_active"""
    params = {"limit": limit}
    if level is not None:
        query += " AND admin_level=:level"; params["level"] = level
    if parent_kato:
        query += " AND parent_kato=:parent"; params["parent"] = parent_kato
    if search:
        query += " AND (name_ru ILIKE :search OR name_kk ILIKE :search OR kato LIKE :prefix)"
        params |= {"search": f"%{search}%", "prefix": f"{search}%"}
    query += " ORDER BY name_ru LIMIT :limit"
    return rows(await db.execute(text(query), params))


@router.get("/territories/{kato}")
async def territory(kato: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""SELECT kato,parent_kato,name_ru,name_kk,admin_level,admin_type,
      area_km2,geometry_source,geometry_valid_at,kato_version,ST_AsGeoJSON(geometry)::json geometry
      FROM territories WHERE kato=:kato"""), {"kato": kato})
    row = result.mappings().first()
    if not row:
        raise HTTPException(404, "Territory not found")
    return dict(row)


@router.get("/territories/{kato}/children")
async def children(kato: str, db: AsyncSession = Depends(get_db)):
    return await territories(parent_kato=kato, db=db)


@router.get("/indicators")
async def indicators(category: str | None = None, db: AsyncSession = Depends(get_db)):
    q = "SELECT slug,name_ru,name_kk,category,description,unit,periodicity,source_url,normalization_allowed,formula,territorial_levels FROM indicators"
    params = {}
    if category: q += " WHERE category=:category"; params["category"] = category
    q += " ORDER BY category,name_ru"
    return rows(await db.execute(text(q), params))


@router.get("/indicators/{slug}")
async def indicator(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM indicators WHERE slug=:slug"), {"slug": slug})
    row = result.mappings().first()
    if not row: raise HTTPException(404, "Indicator not found")
    return dict(row)


@router.get("/data")
async def data(indicator: str, year: int, territory_level: int | None = None,
               parent_kato: str | None = None, db: AsyncSession = Depends(get_db)):
    q = """SELECT t.kato,t.name_ru,t.name_kk,t.admin_level,v.period,v.value,v.unit,v.quality_flag,
      i.source_url,v.source_updated_at FROM indicator_values v JOIN territories t ON t.id=v.territory_id
      JOIN indicators i ON i.id=v.indicator_id WHERE i.slug=:indicator AND v.year=:year"""
    p = {"indicator": indicator, "year": year}
    if territory_level is not None: q += " AND t.admin_level=:level"; p["level"] = territory_level
    if parent_kato: q += " AND t.parent_kato=:parent"; p["parent"] = parent_kato
    return rows(await db.execute(text(q), p))


@router.get("/data/timeseries")
async def timeseries(indicator: str, kato: str, db: AsyncSession = Depends(get_db)):
    q = """SELECT v.period,v.year,v.month,v.quarter,v.value,v.unit,v.quality_flag
      FROM indicator_values v JOIN territories t ON t.id=v.territory_id
      JOIN indicators i ON i.id=v.indicator_id WHERE i.slug=:indicator AND t.kato=:kato ORDER BY v.period"""
    return rows(await db.execute(text(q), {"indicator": indicator, "kato": kato}))


@router.get("/data/compare")
async def compare(indicator: str, year: int, kato: list[str] = Query(...), db: AsyncSession = Depends(get_db)):
    q = """SELECT t.kato,t.name_ru,v.value,v.unit,RANK() OVER(ORDER BY v.value DESC NULLS LAST) rank
      FROM indicator_values v JOIN territories t ON t.id=v.territory_id JOIN indicators i ON i.id=v.indicator_id
      WHERE i.slug=:indicator AND v.year=:year AND t.kato=ANY(:katos)"""
    return rows(await db.execute(text(q), {"indicator": indicator, "year": year, "katos": kato}))


@router.get("/map/{indicator}")
async def map_data(indicator: str, year: int, territory_level: int = 1,
                   parent_kato: str | None = None, db: AsyncSession = Depends(get_db)):
    q = """SELECT json_build_object('type','FeatureCollection','features',COALESCE(json_agg(json_build_object(
      'type','Feature','id',t.kato,'geometry',ST_AsGeoJSON(ST_SimplifyPreserveTopology(t.geometry,0.002))::json,
      'properties',json_build_object('kato',t.kato,'name_ru',t.name_ru,'name_kk',t.name_kk,'value',v.value,'unit',i.unit))), '[]')) payload
      FROM territories t CROSS JOIN indicators i LEFT JOIN indicator_values v ON v.territory_id=t.id AND v.indicator_id=i.id AND v.year=:year
      WHERE i.slug=:indicator AND t.admin_level=:level"""
    p = {"indicator": indicator, "year": year, "level": territory_level}
    if parent_kato: q += " AND t.parent_kato=:parent"; p["parent"] = parent_kato
    result = await db.execute(text(q), p)
    return result.scalar_one()


@router.get("/tiles/{z}/{x}/{y}.pbf")
async def tile(z: int, x: int, y: int, indicator: str, year: int, db: AsyncSession = Depends(get_db)):
    q = text("""WITH bounds AS (SELECT ST_TileEnvelope(:z,:x,:y) geom), mvt AS (
      SELECT t.kato,t.name_ru,v.value,ST_AsMVTGeom(ST_Transform(t.geometry,3857),bounds.geom,4096,64,true) geom
      FROM territories t CROSS JOIN bounds JOIN indicators i ON i.slug=:indicator
      LEFT JOIN indicator_values v ON v.territory_id=t.id AND v.indicator_id=i.id AND v.year=:year
      WHERE ST_Intersects(ST_Transform(t.geometry,3857),bounds.geom)) SELECT ST_AsMVT(mvt,'territories',4096,'geom') FROM mvt""")
    payload = (await db.execute(q, {"z":z,"x":x,"y":y,"indicator":indicator,"year":year})).scalar() or b""
    return Response(payload, media_type="application/vnd.mapbox-vector-tile", headers={"Cache-Control":"public,max-age=3600"})


@router.get("/meta/years")
async def years(indicator: str | None = None, db: AsyncSession = Depends(get_db)):
    q = "SELECT DISTINCT v.year FROM indicator_values v"
    p = {}
    if indicator: q += " JOIN indicators i ON i.id=v.indicator_id WHERE i.slug=:indicator"; p["indicator"] = indicator
    q += " ORDER BY year DESC"
    return [r[0] for r in await db.execute(text(q), p)]


@router.get("/meta/categories")
async def categories(db: AsyncSession = Depends(get_db)):
    return [r[0] for r in await db.execute(text("SELECT DISTINCT category FROM indicators ORDER BY category"))]


@router.get("/meta/sources")
async def sources(db: AsyncSession = Depends(get_db)):
    return rows(await db.execute(text("SELECT DISTINCT source_url,source_format FROM indicators ORDER BY source_url")))

