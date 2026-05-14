"""Chat endpoint — the main entry point for Eko conversations."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.session import ShoppingSession
from app.schemas.chat import ChatIn, ChatOut
from app.agents.graph import eko_graph
from app.agents.data_agent import (
    get_customer_data,
    get_seller_data,
    get_cart_products,
    get_delivery_data,
)
from app.services.logging import write_log
from app.services.segmentation import QUOTA_BY_SEGMENT

router = APIRouter()

DEFAULT_SELLER_ID = "seller-techstore-01"


@router.post("/chat/{session_id}", response_model=ChatOut)
async def chat(session_id: str, body: ChatIn, db: Session = Depends(get_db)):
    session = db.query(ShoppingSession).filter(ShoppingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Block chat only when the order is fully finalized (delivery choice made).
    # pending_customer_choice means logistics offered green delivery but user hasn't decided yet.
    if session.purchase_confirmed and session.delivery_preference not in ("pending_customer_choice",):
        return ChatOut(
            response_text=(
                "Siparişiniz zaten tamamlandı! Yeni bir alışveriş için "
                "sepetinizi güncelleyip yeni bir sohbet başlatabilirsiniz."
            ),
            agent_used="orchestrator",
            agent_logs=[],
            quota_remaining=0,
        )

    cart_items = session.cart_items or []
    cart_products = get_cart_products(db, cart_items)
    customer_data = get_customer_data(db, session.customer_id)
    seller_data = get_seller_data(db, DEFAULT_SELLER_ID)

    if not cart_items:
        return ChatOut(
            response_text=(
                "Sepetiniz boş görünüyor. Ürünleri sepete ekledikten sonra "
                "fiyat, teslimat veya ürünler hakkında konuşabiliriz!"
            ),
            agent_used="orchestrator",
            agent_logs=[],
        )

    if not seller_data.get("negotiation_active", True):
        return ChatOut(
            response_text=(
                "Şu an pazarlık özelliği aktif değil. "
                "Ürünlerimizi listelenen fiyatlardan satın alabilirsiniz."
            ),
            agent_used="orchestrator",
            agent_logs=[],
        )

    cart_total = sum(
        p["list_price"] * item["quantity"]
        for item in cart_items
        for p in [cart_products.get(item["product_id"])]
        if p
    )

    total_weight = sum(
        p["weight_kg"] * item["quantity"]
        for item in cart_items
        for p in [cart_products.get(item["product_id"])]
        if p
    )

    delivery_data = get_delivery_data(
        customer_data.get("region_code", "IST"),
        total_weight,
    )

    # Merge seller data into product_data under a special key
    product_data_with_seller = dict(cart_products)
    product_data_with_seller["_seller"] = seller_data

    initial_state = {
        "session_id": session_id,
        "customer_id": session.customer_id,
        "seller_id": DEFAULT_SELLER_ID,
        "user_message": body.message,
        "cart_items": cart_items,
        "cart_total": cart_total,
        "negotiation_history": session.negotiation_history or [],
        "final_discount": session.final_discount or 0.0,
        "final_gifts": session.final_gifts or [],
        "negotiation_quota_used": session.negotiation_quota_used or 0,
        "customer_segment": customer_data.get("segment", "new"),
        "purchase_confirmed": session.purchase_confirmed or False,
        "delivery_preference": session.delivery_preference or "express",
        "carbon_saved_kg": session.carbon_saved_kg or 0.0,
        "intent": "",
        "intent_confidence": 0.0,
        "response_text": "",
        "agent_used": "",
        "offer_details": None,
        "carbon_data": None,
        "agent_logs": [],
        "product_data": product_data_with_seller,
        "customer_data": customer_data,
        "delivery_data": delivery_data,
    }

    result = await eko_graph.ainvoke(initial_state)

    # Persist state changes back to session
    if result.get("negotiation_history"):
        session.negotiation_history = result["negotiation_history"]
    if result.get("final_discount"):
        session.final_discount = result["final_discount"]
    if result.get("final_gifts"):
        session.final_gifts = result["final_gifts"]
    if result.get("negotiation_quota_used") is not None:
        session.negotiation_quota_used = result["negotiation_quota_used"]
    if result.get("purchase_confirmed"):
        session.purchase_confirmed = result["purchase_confirmed"]
    if result.get("carbon_saved_kg"):
        session.carbon_saved_kg = result["carbon_saved_kg"]
    if result.get("delivery_preference") and result["delivery_preference"] != "express":
        session.delivery_preference = result["delivery_preference"]
    db.commit()

    # Persist agent logs to DB (and broadcast via WebSocket)
    for log_entry in result.get("agent_logs", []):
        await write_log(
            db=db,
            session_id=session_id,
            agent_name=log_entry.get("agent", "unknown"),
            action=log_entry.get("action", ""),
            payload=log_entry.get("payload"),
        )

    quota_used = result.get("negotiation_quota_used", session.negotiation_quota_used or 0)
    quota_total = QUOTA_BY_SEGMENT.get(customer_data.get("segment", "new"), 3)
    quota_remaining = max(quota_total - quota_used, 0)

    awaiting_delivery_choice = (
        session.delivery_preference == "pending_customer_choice"
    )

    return ChatOut(
        response_text=result.get("response_text", ""),
        agent_used=result.get("agent_used", "orchestrator"),
        offer_details=result.get("offer_details"),
        carbon_data=result.get("carbon_data"),
        agent_logs=result.get("agent_logs", []),
        quota_remaining=quota_remaining,
        awaiting_delivery_choice=awaiting_delivery_choice,
    )
