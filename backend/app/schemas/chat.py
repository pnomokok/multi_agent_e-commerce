from typing import Any, Optional
from pydantic import BaseModel


class ChatIn(BaseModel):
    message: str


class OfferDetails(BaseModel):
    original_price: float
    offered_price: float
    discount_amount: float
    gifts: list[str]
    free_shipping: bool
    is_final: bool


class CarbonData(BaseModel):
    co2_saved_kg: float
    discount_amount: float
    express_date: str
    consolidated_date: str
    tree_equivalent: str


class ChatOut(BaseModel):
    response_text: str
    agent_used: str           # orchestrator / negotiator / logistics
    offer_details: Optional[OfferDetails] = None
    carbon_data: Optional[CarbonData] = None
    agent_logs: list[dict[str, Any]] = []
    quota_remaining: Optional[int] = None   # pazarlık hakkı kalan tur sayısı
    awaiting_delivery_choice: bool = False  # True → lojistik teklif sundu, kullanıcı henüz seçmedi
