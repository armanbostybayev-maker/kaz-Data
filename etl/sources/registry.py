"""Official BNS source registry used by the static statistics pipeline."""

DEMOGRAPHY_PAGE = "https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/"
LABOR_PAGE = "https://stat.gov.kz/ru/industries/labor-and-income/stat-empt-unempl/dynamic-tables/"
INCOME_PAGE = "https://stat.gov.kz/ru/industries/laborand-income/stat-life/dynamic-tables/"
ECONOMY_PAGE = "https://stat.gov.kz/ru/industries/economy/national-accounts/dynamic-tables/"
INDUSTRY_PAGE = "https://stat.gov.kz/ru/industries/business-statistics/stat-industrial-production/dynamic-tables/"
INVESTMENT_PAGE = "https://stat.gov.kz/ru/industries/business-statistics/stat-invest/dynamic-tables/"
CONSTRUCTION_PAGE = "https://stat.gov.kz/ru/industries/business-statistics/stat-inno-build/dynamic-tables/"


def csv_url(element: int) -> str:
    return f"https://stat.gov.kz/api/iblock/element/{element}/csv/file/ru/"


# Values in BNS CSV exports sometimes contain extra groups of decimal zeroes.
# ``source_unit`` and ``plausible_max`` make their removal explicit and testable.
SOURCES = [
    dict(indicator="population", name_ru="Численность населения", name_kk="Халық саны", category="demography", file="demography/population_yearly_2026-08-11.csv", element=6584, page=DEMOGRAPHY_PAGE, unit="человек", source_unit="count", plausible_max=100_000_000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего", "СГНЛ":"Все группы"}, updated="2026-08-11"),
    dict(indicator="births", name_ru="Родившиеся", name_kk="Туылғандар", category="demography", file="demography/births_2026-09-30.csv", element=6548, page=DEMOGRAPHY_PAGE, unit="человек", source_unit="count", plausible_max=10_000_000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего"}, updated="2026-07-13"),
    dict(indicator="deaths", name_ru="Умершие", name_kk="Қайтыс болғандар", category="demography", file="demography/deaths_2026-09-30.csv", element=6550, page=DEMOGRAPHY_PAGE, unit="человек", source_unit="count", plausible_max=10_000_000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего"}, updated="2026-07-13"),
    dict(indicator="natural_growth", name_ru="Естественный прирост", name_kk="Табиғи өсім", category="demography", file="demography/natural_growth_2026-09-30.csv", element=6547, page=DEMOGRAPHY_PAGE, unit="человек", source_unit="count", plausible_max=10_000_000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего"}, updated="2026-03-27"),
    dict(indicator="migration_balance", name_ru="Сальдо миграции", name_kk="Көші-қон сальдосы", category="demography", file="demography/migration_balance_2026-09-30.csv", element=6567, page=DEMOGRAPHY_PAGE, unit="человек", source_unit="count", plausible_max=10_000_000, filters={"СПТМ (по каталогу)":"Всего", "КН":"Всего", "СП":"Всего"}, updated="2026-09-25", diverging=True),
    dict(indicator="labor_force", name_ru="Численность рабочей силы", name_kk="Жұмыс күші", category="labor", file="labor/labor_force_2026-09-30.csv", element=102800, page=LABOR_PAGE, unit="человек", source_unit="count", plausible_max=100_000_000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего", "ГСУО01":"Всего", "ГСГВОЗ":"Всего"}, updated="2026-09-30"),
    dict(indicator="employed", name_ru="Занятое население", name_kk="Жұмыспен қамтылған халық", category="labor", file="labor/employed_2026-09-30.csv", element=102798, page=LABOR_PAGE, unit="человек", source_unit="count", plausible_max=100_000_000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего", "ГСУО01":"Всего", "ГСГВОЗ":"Всего", "ГОКЭД(по разделу)02 ":"Всего"}, updated="2026-09-30"),
    dict(indicator="unemployed", name_ru="Безработное население", name_kk="Жұмыссыз халық", category="labor", file="labor/unemployed_2026-09-30.csv", element=102791, page=LABOR_PAGE, unit="человек", source_unit="count", plausible_max=10_000_000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего", "ГСУО01":"Всего", "ГСГВОЗ":"Всего"}, updated="2026-09-30"),
    dict(indicator="unemployment_rate", name_ru="Уровень безработицы", name_kk="Жұмыссыздық деңгейі", category="labor", file="labor/unemployment_rate_2026-09-30.csv", element=102790, page=LABOR_PAGE, unit="%", source_unit="percent", plausible_max=1000, filters={"СПТМ (по каталогу)":"Всего", "СП":"Всего", "ГСУО01":"Всего", "ГСГВОЗ":"Всего"}, updated="2026-09-30"),
    dict(indicator="nominal_income_per_capita", name_ru="Среднедушевые номинальные денежные доходы", name_kk="Жан басына шаққандағы атаулы ақшалай табыс", category="income", file="income/nominal_income_per_capita_2026-09-30.csv", element=19298, page=INCOME_PAGE, unit="₸/месяц", source_unit="tenge", plausible_max=10_000_000, filters={}, updated="2026-09-30"),
    dict(indicator="grp", name_ru="Валовой региональный продукт", name_kk="Жалпы өңірлік өнім", category="economy", file="economy/grp_2026-09-30.csv", element=5923, page=ECONOMY_PAGE, unit="млрд ₸", source_unit="million_tenge", plausible_max=100_000_000, output_divisor=1000, filters={}, updated="2026-09-30"),
    dict(indicator="grp_per_capita", name_ru="ВРП на душу населения", name_kk="Жан басына шаққандағы ЖӨӨ", category="economy", file="economy/grp_per_capita_2026-09-30.csv", element=5930, page=ECONOMY_PAGE, unit="тыс. ₸", source_unit="thousand_tenge_per_capita", plausible_max=100_000, filters={}, updated="2026-09-30"),
    dict(indicator="grp_volume_index", name_ru="Индекс физического объёма ВРП", name_kk="ЖӨӨ нақты көлем индексі", category="economy", file="economy/grp_volume_index_2026-09-30.csv", element=5926, page=ECONOMY_PAGE, unit="%", source_unit="percent", plausible_max=1000, filters={}, updated="2026-09-30"),
    dict(indicator="industrial_output", name_ru="Объём промышленного производства", name_kk="Өнеркәсіп өндірісінің көлемі", category="industry", file="industry/industrial_output_2026-09-30.csv.gz", element=5791, page=INDUSTRY_PAGE, unit="млрд ₸", source_unit="thousand_tenge", plausible_max=100_000_000_000, output_divisor=1_000_000, filters={"ГОКЭД(по разделу)03":"Промышленность"}, updated="2026-09-30"),
    dict(indicator="industrial_production_index", name_ru="Индекс промышленного производства", name_kk="Өнеркәсіп өндірісінің индексі", category="industry", file="industry/industrial_production_index_2026-09-30.csv.gz", element=5809, page=INDUSTRY_PAGE, unit="%", source_unit="percent", plausible_max=1000, filters={"ГОКЭД(по разделу)03":"Промышленность", "ССП":"отчетный период к предыдущему периоду"}, updated="2026-09-30"),
    dict(indicator="fixed_capital_investment", name_ru="Инвестиции в основной капитал", name_kk="Негізгі капиталға салынған инвестициялар", category="investment", file="investment/fixed_capital_investment_2026-09-30.csv", element=5546, page=INVESTMENT_PAGE, unit="млрд ₸", source_unit="thousand_tenge", plausible_max=100_000_000_000, output_divisor=1_000_000, filters={"СПТМ (по отчету)":"Всего", "КРП(по каталогу)":"Всего", "ГСВЗИОК":"Всего"}, updated="2026-09-30"),
    dict(indicator="construction_output", name_ru="Объём строительных работ", name_kk="Құрылыс жұмыстарының көлемі", category="construction", file="construction/construction_output_2026-09-30.csv", element=4296, page=CONSTRUCTION_PAGE, unit="млрд ₸", source_unit="thousand_tenge", plausible_max=100_000_000_000, output_divisor=1_000_000, filters={"СПВД(по каталогу)":"Всего", "СВСР":"Всего", "ГКОФ":"Всего"}, updated="2026-09-30"),
    dict(indicator="housing_commissioned", name_ru="Ввод жилья", name_kk="Тұрғын үйді пайдалануға беру", category="construction", file="construction/housing_commissioned_2026-09-30.csv", element=4289, page=CONSTRUCTION_PAGE, unit="м²", source_unit="sqm", plausible_max=100_000_000, filters={"СПТМ (по отчету)":"Всего", "КФС(по каталогу)":"Всего", "ГСГТПЕ":"Всего", "ГКОФ":"Всего"}, updated="2026-09-30"),
]

CATEGORY_NAMES = {
    "demography": "Демография", "labor": "Рынок труда", "income": "Доходы",
    "economy": "Экономика", "industry": "Промышленность",
    "investment": "Инвестиции", "construction": "Строительство",
}
