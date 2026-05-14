"""Pricing and discount calculation helpers."""
from app.models.product import Product


def max_allowed_discount(product: Product, seller_min_margin: float) -> float:
    """Return the maximum TL discount we can offer without violating margin floor."""
    effective_floor = max(product.base_price, product.list_price * (1 - product.max_discount_pct))
    margin_floor = product.list_price * (1 - seller_min_margin / product.margin)
    floor = max(effective_floor, margin_floor, product.base_price)
    return round(max(product.list_price - floor, 0.0), 2)


def suggested_first_offer(product: Product, seller_min_margin: float, segment: str) -> float:
    """Return a sensible first-offer discount amount based on customer segment."""
    max_disc = max_allowed_discount(product, seller_min_margin)
    ratios = {"new": 0.5, "loyal": 0.65, "bargain_hunter": 0.35}
    ratio = ratios.get(segment, 0.5)
    return round(max_disc * ratio, -1)  # round to nearest 10 TL


def calculate_cart_total(cart_items: list[dict], products: dict[str, Product]) -> float:
    total = 0.0
    for item in cart_items:
        p = products.get(item["product_id"])
        if p:
            total += p.list_price * item["quantity"]
    return round(total, 2)
