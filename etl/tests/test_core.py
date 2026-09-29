from etl.normalization.text import normalize_name, parse_number
from etl.kato.parser import _level

def test_numbers():
    assert parse_number("1 234,5") == 1234.5
    assert parse_number("…") is None

def test_names():
    assert normalize_name("область Абай") == "абай"

def test_hierarchy_levels():
    assert _level("100000000") == 1
    assert _level("101000000") == 2

