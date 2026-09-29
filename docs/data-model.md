# Модель данных

`territories` хранит КАТО, двуязычное имя, иерархию, тип, актуальность и temporal PostGIS geometry. `indicators` — единица, периодичность, агрегация, допустимые нормализации, территориальные уровни и формула. `indicator_values` — tidy/long row на `(territory, indicator, period)`; `NULL` означает отсутствие, `0` — измеренное нулевое значение.

`data_quality_issues` сохраняет нарушения без удаления исходной строки. `ingestion_runs` фиксирует checksum, raw path, даты, статус и counts. Индексы покрывают КАТО, parent, names, spatial geometry и основной data lookup.

