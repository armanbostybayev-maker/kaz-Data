# Каталог наборов stat.gov.kz

Аудит: 29.09.2026. `download_url` фиксируется только когда URL проверен. Статус `metadata` означает, что показатель есть в схеме MVP, но parser ещё не подтверждён на реальном файле.

| category | indicator | source_page | download_url | format | periodicity | territorial_level | latest_update | parser | status |
|---|---|---|---|---|---|---|---|---|---|
| demography | Численность населения | https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/ | https://stat.gov.kz/api/iblock/element/6584/csv/file/ru/ | CSV | annual | country/adm1/adm2 (as published) | 2026-08-11 | `population.py` | active |
| demography | Число родившихся | https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/ | — | CSV/JSON/XLSX | annual | to verify | 2026-07-13 | — | discovered |
| demography | Общий коэффициент рождаемости | https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/ | — | CSV/JSON/XLSX | annual | to verify | 2026-07-13 | — | discovered |
| demography | Число умерших | https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/ | — | CSV/JSON/XLSX | annual | to verify | 2026-07-13 | — | discovered |
| demography | Общий коэффициент смертности | https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/ | — | CSV/JSON/XLSX | annual | to verify | 2026-07-13 | — | discovered |
| labor | Рабочая сила / занятость / безработица | https://stat.gov.kz/ru/industries/labor-and-income/stat-empt-unempl/ | — | XLSX | quarterly | country/adm1 | — | — | metadata |
| income | Среднедушевые доходы | https://stat.gov.kz/ru/industries/labor-and-income/stat-life/ | — | XLSX | quarterly | country/adm1 | — | — | metadata |
| economy | ВРП | https://stat.gov.kz/ru/industries/eco-nomy/national-accounts/ | — | XLSX/CSV/JSON | annual | adm1 | — | — | discovered |
| industry | Промышленное производство | https://stat.gov.kz/ru/industries/business-statistics/stat-industrial-production/ | — | XLSX | monthly | country/adm1 | — | — | metadata |
| investment | Инвестиции в основной капитал | https://stat.gov.kz/ru/industries/business-statistics/stat-invest/ | — | XLSX | monthly | country/adm1/adm2 if published | — | — | metadata |
| construction | Ввод жилья | https://stat.gov.kz/ru/industries/business-statistics/stat-inno-build/ | — | XLSX | monthly | country/adm1/adm2 if published | — | — | metadata |

