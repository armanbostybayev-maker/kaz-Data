FORMULAS = {
 "population_density":{"expression":"population / area_km2","requires":["population","area_km2"],"unit":"чел./км²"},
 "population_change_pct":{"expression":"(population - lag(population)) / lag(population) * 100","requires":["population"],"unit":"%"},
 "natural_growth":{"expression":"births - deaths","requires":["births","deaths"],"unit":"человек"},
 "migration_balance":{"expression":"arrivals - departures","requires":["arrivals","departures"],"unit":"человек"},
 "grp_per_capita":{"expression":"grp / population","requires":["grp","population"],"unit":"₸/чел."},
 "investment_per_capita":{"expression":"fixed_capital_investment / population","requires":["fixed_capital_investment","population"],"unit":"₸/чел."}
}

