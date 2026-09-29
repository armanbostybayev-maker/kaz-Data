# КАТО и сопоставление геометрии

Порядок доверия: код из geometry → официальный transition key → exact normalized name + parent → fuzzy candidate. Последний шаг только формирует review и никогда не подтверждает соответствие.

`python -m etl geography` создаёт отдельные отчёты adm1/adm2 и summary. Статусы: `matched`, `unmatched_geometry`, `unmatched_kato`, `ambiguous`, `renamed`, `split`, `merged`, `new_territory`, `obsolete_geometry`. Ручное решение должно содержать автора, дату, источник основания и выбранный КАТО.

Снимок `geokz` относится примерно к январю 2024; текущий КАТО актуализирован 18.09.2026, поэтому расхождения ожидаемы и не являются ошибкой pipeline.

