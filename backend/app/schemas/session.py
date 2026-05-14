from datetime import datetime
from pydantic import BaseModel


class SessionStartIn(BaseModel):
    customer_id: str


class SessionOut(BaseModel):
    session_id: str
    customer_id: str
    cart_items: list
    negotiation_history: list
    final_discount: float
    final_gifts: list
    purchase_confirmed: bool
    delivery_preference: str
    awaiting_delivery_choice: bool  # True → logistics teklif verdi, kullanıcı henüz seçmedi
    carbon_saved_kg: float
    negotiation_quota_used: int
    created_at: datetime

    model_config = {"from_attributes": True}
