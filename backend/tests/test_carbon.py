"""Tests for carbon calculation service."""
import pytest
from app.services.carbon import calculate_co2_saved, trees_equivalent


def test_co2_saved_positive():
    result = calculate_co2_saved(total_weight_kg=1.0, distance_km=500.0)
    assert result > 0


def test_co2_saved_zero_weight():
    result = calculate_co2_saved(total_weight_kg=0.0, distance_km=500.0)
    assert result == 0.0


def test_co2_saved_formula():
    # (0.0002 - 0.00008) * 1 * 100 = 0.012
    result = calculate_co2_saved(total_weight_kg=1.0, distance_km=100.0)
    assert abs(result - 0.012) < 0.001


def test_trees_equivalent_returns_string():
    result = trees_equivalent(co2_kg=0.5)
    assert isinstance(result, str)
    assert len(result) > 0
