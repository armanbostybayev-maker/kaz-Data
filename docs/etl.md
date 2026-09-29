# ETL

Каждый adapter отвечает за один официальный набор и реализует download/version check, raw persistence, parse, numeric normalization, period extraction, exact KATO/name match, validation и ingestion report. Downloader должен использовать ETag/Last-Modified и SHA-256: при неизменном checksum загрузка прекращается без перезаписи БД.

Общие числовые правила находятся в `etl/normalization`; пробелы-разделители и десятичная запятая поддерживаются, маркеры пропуска становятся `NULL`. Derived indicators описаны декларативно в `etl/formulas.py`.

Текущий рабочий adapter: `etl/sources/demography/population.py`, официальный CSV element 6584. Он загружает только строки `Всего` и только надёжные exact normalized match для уровня 1; несовпадения попадают в review CSV.

