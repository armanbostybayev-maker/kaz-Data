from etl.pipeline import clean_value, period_label, territory_key


def test_bns_decimal_zero_groups_are_normalized_by_unit_ceiling():
    assert clean_value("5 332 700 000", 100_000) == 5332.7
    assert clean_value("1 793 149 374 500 000", 100_000_000_000, 1_000_000) == 1793.1494


def test_period_labels_do_not_invent_months():
    assert period_label("202412", "2024 год") == "2024"
    assert period_label("202506", "2 квартал 2025 г.") == "2025-Q2"


def test_city_and_region_keys_cannot_collide():
    assert territory_key("г. Алматы") != territory_key("Алматинская область")
