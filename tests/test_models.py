"""Tests for data models."""
import pytest
from airgradient.models import Measures, Location


def test_measures_from_dict():
    data = {"rco2": 450, "pm02": 8.5, "atmp": 22.0, "rhum": 45}
    m = Measures.from_dict(data)
    assert m.rco2 == 450
    assert m.pm02 == 8.5
    assert m.atmp == 22.0
    assert m.rhum == 45


def test_measures_atmp_f():
    m = Measures(atmp=0.0)
    assert m.atmp_f == 32.0

    m = Measures(atmp=100.0)
    assert m.atmp_f == 212.0


def test_measures_atmp_f_none():
    m = Measures()
    assert m.atmp_f is None


def test_measures_pm25_alias():
    m = Measures(pm02=12.3)
    assert m.pm25 == 12.3


def test_aqi_categories():
    cases = [
        (0, "Good"),
        (12.0, "Good"),
        (12.1, "Moderate"),
        (35.4, "Moderate"),
        (35.5, "Unhealthy for Sensitive Groups"),
        (55.5, "Unhealthy"),
        (150.5, "Very Unhealthy"),
        (250.5, "Hazardous"),
    ]
    for pm, expected in cases:
        m = Measures(pm02=pm)
        assert m.aqi_pm25_category == expected, f"pm={pm}"


def test_aqi_none_when_no_pm25():
    m = Measures()
    assert m.aqi_pm25_category is None


def test_location_from_dict():
    data = {"id": 42, "name": "Office", "timezone": "America/Denver"}
    loc = Location.from_dict(data)
    assert loc.location_id == "42"
    assert loc.name == "Office"
    assert loc.timezone == "America/Denver"


def test_measures_ignores_unknown_fields():
    data = {"rco2": 400, "unknown_field": "ignored"}
    m = Measures.from_dict(data)
    assert m.rco2 == 400
