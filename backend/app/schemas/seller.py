from pydantic import BaseModel


class SellerPolicyOut(BaseModel):
    seller_id: str
    negotiation_active: bool
    monthly_negotiation_budget: float
    monthly_negotiation_spent: float
    budget_remaining: float
    min_margin_target: float
    segment_strategy: str

    model_config = {"from_attributes": True}


class SellerPolicyIn(BaseModel):
    negotiation_active: bool | None = None
    monthly_negotiation_budget: float | None = None
    min_margin_target: float | None = None
    segment_strategy: str | None = None


class SellerStatsOut(BaseModel):
    seller_id: str
    seller_name: str
    total_negotiations: int
    successful_negotiations: int
    total_discount_given: float
    estimated_orders_saved: int
    net_roi: float
    total_co2_saved_kg: float
    eco_seller_badge: bool


class SellerDashboardOut(BaseModel):
    policy: SellerPolicyOut
    stats: SellerStatsOut
