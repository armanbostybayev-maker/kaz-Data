# Интерактивный статистический атлас Казахстана

Production-oriented монорепозиторий для пространственного анализа официальной статистики Бюро национальной статистики РК. КАТО — основной идентификатор территории; геометрия `geokz` считается снимком границ, а не справочником актуального административного устройства. Нулевое значение и отсутствие данных (`NULL`) принципиально различаются.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

Интерфейс: `http://localhost:3000`, OpenAPI: `http://localhost:8000/docs`, healthcheck: `http://localhost:8000/health`.

После первого запуска импортируйте подготовленные источники:

```bash
docker compose run --rm etl-worker python -m etl all
```

## Статическая сборка без Docker

GitHub Pages не запускает FastAPI/PostGIS, поэтому репозиторий поддерживает автономный экспорт с официальными данными, подготовленными на этапе сборки:

```powershell
cd apps\frontend
npm install
npm run build:static
```

Готовый сайт находится в `apps/frontend/out`. Его можно открыть через любой статический HTTP-сервер:

```bash
npx serve out
```

Проверенный статический data bundle уже находится в `apps/frontend/public/data`, поэтому для обычной сборки Python и база данных не нужны. Чтобы обновить bundle из свежих raw-файлов, отдельно выполните ETL и `python scripts/prepare_static_site.py`.

Workflow `.github/workflows/pages.yml` повторяет эти шаги и публикует `out` в GitHub Pages при push в `main` или `master`. В настройках репозитория выберите **Settings → Pages → Source: GitHub Actions**. Статическая публикация содержит проверенные геометрии adm1/adm2 и 21 реально подключённый показатель из семи категорий; серверные MVT, Redis и динамический ETL доступны только в full-stack режиме.

Raw-файлы хранятся с датой версии. Репозиторий содержит официальный `KATO_2026-09-18.xlsx`, исходные shapefile `geokz` и официальные CSV БНС; особо крупные исходники промышленности сохранены без изменения содержимого в gzip.

## Подключённые данные

- Демография: население, изменение и плотность населения, родившиеся, умершие, естественный прирост, сальдо миграции.
- Рынок труда: рабочая сила, занятые, безработные, уровень безработицы.
- Доходы: среднедушевые номинальные денежные доходы.
- Экономика: ВРП, ВРП на душу населения, индекс физического объёма ВРП.
- Промышленность: объём и индекс промышленного производства.
- Инвестиции: инвестиции в основной капитал и расчёт на душу населения.
- Строительство: объём строительных работ и ввод жилья.

Меню строится из `public/data/catalog.json`, а выбранный dataset загружается лениво. Фактическое покрытие видно на странице `/data-status` и в `data/reports/indicator_coverage.csv`. Региональные и доступные районные ряды привязаны только к подтверждённому КАТО; неоднозначные совпадения исключаются, значения между уровнями не распределяются.

## Архитектура

- `apps/frontend` — Next.js, TypeScript, MapLibre GL, TanStack Query, Zustand; адаптивный GIS dashboard.
- `apps/backend` — FastAPI, async SQLAlchemy, GeoAlchemy2; GeoJSON для малых выборок и PostGIS MVT для районов.
- `etl` — независимые адаптеры, нормализация, КАТО, matching, validation и derived-formula registry.
- `database` — PostGIS schema и metadata seed 20 MVP-показателей.
- `data/raw` — неизменяемые версии источников; `data/processed` — нормализованные результаты; `data/reports` — несовпадения и качество.

Подробности: [архитектура](docs/architecture.md), [модель данных](docs/data-model.md), [ETL](docs/etl.md), [КАТО matching](docs/kato-matching.md), [подложки](docs/basemaps.md), [каталог БНС](docs/stat-gov-kz-sources.md).

## CLI

```bash
make db                 # PostgreSQL/PostGIS + Redis
make kato               # разобрать текущий КАТО
make geography          # точное сопоставление и review-файлы
make etl-demography     # официальный ряд населения
make validate           # validation report
make test               # backend + frontend unit tests
```

Эквиваленты: `python -m etl kato`, `python -m etl geography`, `python -m etl demography`, `python -m etl labor`, `python -m etl income`, `python -m etl economy`, `python -m etl industry`, `python -m etl investment`, `python -m etl construction`, `python -m etl all`, `python -m etl validate`. Проверенные URL обновляются командой `python -m etl download`.

## Обновление КАТО и геометрии

1. Скачайте актуальный Excel только со [страницы классификатора КАТО](https://stat.gov.kz/ru/classifiers/statistical/21/).
2. Сохраните как новую датированную версию в `data/raw/kato/`; не заменяйте старую.
3. Измените `KATO_RAW` и version metadata в `etl/__main__.py`, запустите `make kato`.
4. Для геометрии сохраните новый снимок в отдельном датированном каталоге `data/raw/geokz/` и запустите matching.
5. Разберите каждый `ambiguous`, `unmatched_*`, `split`, `merged` вручную. Fuzzy-кандидат никогда не подтверждается автоматически.

## Новый показатель БНС

Добавьте metadata в `database/seeds/indicators.sql`, затем отдельный adapter в `etl/sources/<category>/`. Адаптер обязан сохранить URL, дату обновления, raw checksum, период, единицу и quality flag. Предпочтение: JSON → CSV → XLSX/XLS → HTML. Территориальные уровни указываются явно; районные значения не выводятся из областных.

## Basemaps

OSM включён для разработки с обязательной attribution. Для production задайте коммерчески/операционно подходящий tile provider через env. COSMO и TOPO намеренно выключены: URL не выдумываются. После получения легального endpoint заполните `NEXT_PUBLIC_COSMO_TILES` или `NEXT_PUBLIC_TOPO_TILES` и attribution; описание в `docs/basemaps.md`.

## Troubleshooting

- Пустая карта: сначала проверьте `/health`, затем наличие импортированных territories и values.
- COSMO/TOPO неактивны: это ожидаемо без URL и условий использования провайдера.
- Init SQL не применился после изменения: он выполняется только на пустом volume; для локальной разработки пересоздайте именно volume проекта осознанно.
- Старая территория не сопоставилась: не добавляйте guessed КАТО; оформите решение в review-файле с provenance.
