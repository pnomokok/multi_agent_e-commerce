"""Tests for pricing service."""
import pytest
from unittest.mock import MagicMock

from app.services.pricing import max_allowed_discount, suggested_first_offer


def _mock_product(list_price=1000.0, base_price=800.0, margin=0.20, max_discount_pct=0.10):
    p = MagicMock()
    p.list_price = list_price
    p.base_price = base_price
    p.margin = margin
    p.max_discount_pct = max_discount_pct
    return p


def test_max_discount_respects_base_price():
    p = _mock_product(list_price=1000, base_price=900, max_discount_pct=0.20)
    disc = max_allowed_discount(p, seller_min_margin=0.10)
    assert disc <= 100.0


def test_max_discount_zero_when_base_equals_list():
    p = _mock_product(list_price=1000, base_price=1000)
    disc = max_allowed_discount(p, seller_min_margin=0.10)
    assert disc == 0.0


def test_suggested_offer_new_customer():
    p = _mock_product(list_price=2000, base_price=1600, max_discount_pct=0.15)
    offer = suggested_first_offer(p, seller_min_margin=0.12, segment="new")
    assert 0 <= offer <= max_allowed_discount(p, 0.12)
