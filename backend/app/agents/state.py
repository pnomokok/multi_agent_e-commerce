"""LangGraph AgentState — the single shared state object flowing through the graph."""
from typing import Any, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # Session context
    session_id: str
    customer_id: str
    seller_id: str

    # User input
    user_message: str

    # Cart
    cart_items: list[dict]      # [{product_id, quantity}]
    cart_total: float

    # Orchestrator output
    intent: str                 # greeting/price_objection/purchase_decision/general/...
    intent_confidence: float

    # Negotiation
    negotiation_history: list[dict]   # [{role, content}]
    final_discount: float
    final_gifts: list[str]
    negotiation_quota_used: int
    customer_segment: str

    # Logistics / Green delivery
    purchase_confirmed: bool
    delivery_preference: str          # express / consolidated
    carbon_saved_kg: float

    # Response aggregation
    response_text: str
    agent_used: str
    offer_details: Optional[dict]
    carbon_data: Optional[dict]
    agent_logs: list[dict[str, Any]]

    # Internal — passed between nodes, not returned to client
    product_data: dict[str, Any]      # product_id → data dict
    customer_data: dict[str, Any]
    delivery_data: dict[str, Any]
