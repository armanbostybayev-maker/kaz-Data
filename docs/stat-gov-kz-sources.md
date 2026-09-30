# Каталог наборов stat.gov.kz

Аудит: 30.09.2026. Машиночитаемый полный реестр с точными download URL, периодами и статусом находится в `data/catalog/stat_gov_kz_sources.json`.

| category | datasets | source page | raw | level | status |
|---|---|---|---|---|---|
| demography | население, родившиеся, умершие, естественный прирост, сальдо миграции | https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/ | CSV | adm1 | active |
| labor | рабочая сила, занятость, безработица | https://stat.gov.kz/ru/industries/labor-and-income/stat-empt-unempl/dynamic-tables/ | CSV | adm1 | active |
| income | среднедушевые доходы | https://stat.gov.kz/ru/industries/laborand-income/stat-life/dynamic-tables/ | CSV | adm1 | active |
| economy | ВРП и индексы | https://stat.gov.kz/ru/industries/economy/national-accounts/dynamic-tables/ | CSV | adm1 | active |
| industry | объём и индекс промышленного производства | https://stat.gov.kz/ru/industries/business-statistics/stat-industrial-production/dynamic-tables/ | CSV.gz | adm1 | active |
| investment | инвестиции в основной капитал | https://stat.gov.kz/ru/industries/business-statistics/stat-invest/dynamic-tables/ | CSV | adm1 | active |
| construction | строительные работы, ввод жилья | https://stat.gov.kz/ru/industries/business-statistics/stat-inno-build/dynamic-tables/ | CSV | adm1 | active |

Производные показатели рассчитываются только из перечисленных официальных входов: изменение и плотность населения, инвестиции на душу населения. Формула и inputs записаны в payload и catalog.

CSV-ссылки коэффициентов рождаемости и смертности на странице БНС во время аудита отдавали содержимое других таблиц. Такие ответы удалены и не включены в production. Прибывшие/выбывшие и средняя зарплата доступны в XLSX, но не подключены до отдельной проверки стабильной структуры региональных файлов. Значения для них не моделируются.
