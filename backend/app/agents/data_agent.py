"""Data Agent — deterministic service (no LLM).

Provides structured data to other agents:
  - product data (base_price, margin, stock, sales_velocity)
  - customer segment & history
  - delivery options & dates
  - carbon calculation
  - negotiation quota check
  - seller budget check
"""
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session as DBSession

from app.models.customer import Customer
from app.models.product import Product
from app.models.seller import Seller
from app.models.session import ShoppingSession
from app.services.carbon import calculate_co2_saved, get_distance, trees_equivalent
from app.services.segmentation import remaining_quota


def get_product_data(db: DBSession, product_id: str) -> dict[str, Any]:
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        return {}
    return {
        "id": p.id,
        "name": p.name,
        "list_price": p.list_price,
        "base_price": p.base_price,
        "margin": p.margin,
        "stock": p.stock,
        "sales_velocity": p.sales_velocity,
        "weight_kg": p.weight_kg,
        "negotiation_enabled": p.negotiation_enabled,
        "max_discount_pct": p.max_discount_pct,
        "preferred_concessions": p.preferred_concessions or [],
    }


def get_customer_data(db: DBSession, customer_id: str) -> dict[str, Any]:
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        return {}
    return {
        "id": c.id,
        "name": c.name,
        "segment": c.segment,
        "region_code": c.region_code,
        "interaction_history": c.interaction_history or [],
        "total_co2_saved_kg": c.total_co2_saved_kg,
    }


def get_seller_data(db: DBSession, seller_id: str) -> dict[str, Any]:
    s = db.query(Seller).filter(Seller.id == seller_id).first()
    if not s:
        return {}
    return {
        "id": s.id,
        "monthly_negotiation_budget": s.monthly_negotiation_budget,
        "monthly_negotiation_spent": s.monthly_negotiation_spent,
        "budget_remaining": s.monthly_negotiation_budget - s.monthly_negotiation_spent,
        "min_margin_target": s.min_margin_target,
        "negotiation_active": s.negotiation_active,
        "segment_strategy": s.segment_strategy,
    }


def get_delivery_data(region_code: str, total_weight_kg: float) -> dict[str, Any]:
    today = datetime.utcnow().date()
    express_date = today + timedelta(days=1)
    consolidated_date = today + timedelta(days=4)
    distance_km = get_distance(region_code)
    co2_saved = calculate_co2_saved(total_weight_kg, distance_km)
    # Discount = ~10 TL per saved kg of CO₂, min 20 TL
    discount_amount = max(round(co2_saved * 10, -1), 20.0)
    return {
        "express_date": express_date.strftime("%d %B %Y"),
        "consolidated_date": consolidated_date.strftime("%d %B %Y"),
        "distance_km": distance_km,
        "co2_saved_kg": co2_saved,
        "discount_amount": discount_amount,
        "tree_equivalent": trees_equivalent(co2_saved),
    }


def check_negotiation_quota(customer: dict, quota_used: int) -> int:
    from app.services.segmentation import QUOTA_BY_SEGMENT
    total = QUOTA_BY_SEGMENT.get(customer.get("segment", "new"), 3)
    return max(total - quota_used, 0)


def check_seller_budget(seller: dict) -> float:
    return seller.get("budget_remaining", 0.0)


def get_cart_products(db: DBSession, cart_items: list[dict]) -> dict[str, Any]:
    result = {}
    for item in cart_items:
        pid = item["product_id"]
        result[pid] = get_product_data(db, pid)
    return result


def calculate_max_cart_discount(
    cart_products: dict[str, Any],
    seller_min_margin: float,
    budget_remaining: float,
) -> float:
    total_max = 0.0
    for pid, p in cart_products.items():
        if not p or not p.get("negotiation_enabled"):
            continue
        floor = max(p["base_price"], p["list_price"] * (1 - p["max_discount_pct"]))
        total_max += max(p["list_price"] - floor, 0.0)
    return round(min(total_max, budget_remaining), 2)
