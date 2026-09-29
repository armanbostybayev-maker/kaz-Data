# Архитектура

Поток данных: официальный источник → versioned raw → adapter/parser → normalized staging → KATO matching → validation → PostGIS → FastAPI → MapLibre/графики. Redis предназначен для кэша metadata, territory tree, map queries, timeseries и MVT; cache key обязан включать source/update version.

Frontend никогда не получает весь adm2 при каждом изменении. Области доступны как упрощённый GeoJSON, детальные уровни — через `/api/tiles/{z}/{x}/{y}.pbf`. API stateless, контейнеры frontend/backend масштабируются независимо.

Граница привязана к `valid_from`/`valid_to` и `boundary_valid_at` значения. Это не позволяет молча сравнивать ряды на несовместимых границах.

