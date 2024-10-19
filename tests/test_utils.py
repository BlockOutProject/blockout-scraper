import pytest
from utils import parse_season, standardize_division_name, parse_date

def test_parse_season_valid():
    season_str = '2023/2024'
    result = parse_season(season_str)
    assert result == 2023

def test_parse_season_invalid():
    season_str = 'invalid_format'
    with pytest.raises(ValueError):
        parse_season(season_str)

def test_standardize_division_known():
    division = "Elite Masc."
    result = standardize_division_name(division)
    assert result['division'] == 'Élite'
    assert result['gender'] == 'M'

def test_standardize_division_unknown():
    division = 'Unknown Division'
    result = standardize_division_name(division)
    assert result['division'] == 'Unknown Division'
    assert result['gender'] is None

def test_parse_date_valid():
    date_str = '2023-10-01'
    time_str = '15:00'
    result = parse_date(date_str, time_str)
    assert result is not None

def test_parse_date_invalid():
    date_str = 'invalid_date'
    time_str = 'invalid_time'
    result = parse_date(date_str, time_str)
    assert result is None