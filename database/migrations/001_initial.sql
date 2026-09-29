CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS territories (
  id BIGSERIAL PRIMARY KEY,
  kato VARCHAR(12) UNIQUE NOT NULL,
  parent_kato VARCHAR(12),
  name_ru TEXT NOT NULL,
  name_kk TEXT NOT NULL,
  admin_level SMALLINT NOT NULL CHECK (admin_level BETWEEN 0 AND 5),
  admin_type TEXT NOT NULL,
  geometry geometry(MultiPolygon, 4326),
  centroid geometry(Point, 4326),
  area_km2 DOUBLE PRECISION,
  geometry_source TEXT NOT NULL DEFAULT 'geokz',
  geometry_valid_at DATE,
  kato_version TEXT NOT NULL,
  valid_from DATE,
  valid_to DATE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS ix_territories_kato ON territories(kato);
CREATE INDEX IF NOT EXISTS ix_territories_parent ON territories(parent_kato);
CREATE INDEX IF NOT EXISTS ix_territories_geometry ON territories USING GIST(geometry);
CREATE INDEX IF NOT EXISTS ix_territories_name_ru ON territories USING GIN(name_ru gin_trgm_ops);

CREATE TABLE IF NOT EXISTS indicators (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name_ru TEXT NOT NULL,
  name_kk TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  unit TEXT NOT NULL,
  periodicity TEXT NOT NULL,
  source_url TEXT NOT NULL,
  source_format TEXT NOT NULL,
  aggregation_type TEXT NOT NULL,
  normalization_allowed JSONB NOT NULL DEFAULT '["absolute"]',
  formula JSONB,
  territorial_levels SMALLINT[] NOT NULL DEFAULT '{1}'
);

CREATE TABLE IF NOT EXISTS indicator_values (
  id BIGSERIAL PRIMARY KEY,
  territory_id BIGINT NOT NULL REFERENCES territories(id),
  indicator_id BIGINT NOT NULL REFERENCES indicators(id),
  period TEXT NOT NULL,
  year SMALLINT NOT NULL,
  month SMALLINT,
  quarter SMALLINT,
  value NUMERIC,
  unit TEXT NOT NULL,
  source_url TEXT NOT NULL,
  source_updated_at TIMESTAMPTZ,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  quality_flag TEXT NOT NULL DEFAULT 'ok',
  boundary_valid_at DATE,
  UNIQUE(territory_id, indicator_id, period)
);
CREATE INDEX IF NOT EXISTS ix_values_territory ON indicator_values(territory_id);
CREATE INDEX IF NOT EXISTS ix_values_indicator ON indicator_values(indicator_id);
CREATE INDEX IF NOT EXISTS ix_values_period ON indicator_values(period);
CREATE INDEX IF NOT EXISTS ix_values_lookup ON indicator_values(indicator_id, year, territory_id);

CREATE TABLE IF NOT EXISTS data_quality_issues (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  territory TEXT,
  indicator TEXT,
  period TEXT,
  issue_type TEXT NOT NULL,
  message TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('info','warning','error')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
  id BIGSERIAL PRIMARY KEY,
  source_url TEXT NOT NULL,
  source_checksum TEXT NOT NULL,
  raw_path TEXT NOT NULL,
  source_updated_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  status TEXT NOT NULL,
  rows_read INTEGER NOT NULL DEFAULT 0,
  rows_loaded INTEGER NOT NULL DEFAULT 0,
  report JSONB NOT NULL DEFAULT '{}'
);
