import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.models.seller import Seller
from app.models.session import ShoppingSession

router = APIRouter()

DEFAULT_SELLER_ID = "seller-techstore-01"


class CheckoutIn(BaseModel):
    delivery_preference: str = "express"  # express / consolidated


@router.post("/checkout/{session_id}")
def checkout(session_id: str, body: CheckoutIn, db: Session = Depends(get_db)):
    session = db.query(ShoppingSession).filter(ShoppingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    session.purchase_confirmed = True
    session.delivery_preference = body.delivery_preference

    customer = db.query(Customer).filter(Customer.id == session.customer_id).first()

    # Update customer CO₂ & badge
    if body.delivery_preference == "consolidated" and session.carbon_saved_kg > 0:
        if customer:
            customer.total_co2_saved_kg = (customer.total_co2_saved_kg or 0.0) + session.carbon_saved_kg
            if customer.total_co2_saved_kg >= 5.0:
                customer.eco_customer_badge = True

    # Append this session's activity to interaction_history
    if customer:
        parts = []
        if session.final_discount and session.final_discount > 0:
            parts.append(f"{session.final_discount:.0f} TL indirim ile anlaşıldı")
        if session.final_gifts:
            parts.append(f"hediye: {', '.join(session.final_gifts)}")
        if body.delivery_preference == "consolidated":
            parts.append(
                f"konsolide teslimat seçti, {session.carbon_saved_kg or 0:.2f} kg CO₂ kurtardı"
            )
        if not parts:
            parts.append("liste fiyatından satın aldı")

        entry_type = "green_delivery" if body.delivery_preference == "consolidated" else "purchase"
        new_entry = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "type": entry_type,
            "summary": ", ".join(parts) + ".",
        }
        history = list(customer.interaction_history or [])
        history.append(new_entry)
        customer.interaction_history = history

    # Update seller's spent budget
    if session.final_discount > 0:
        seller = db.query(Seller).filter(Seller.id == DEFAULT_SELLER_ID).first()
        if seller:
            seller.monthly_negotiation_spent = (
                seller.monthly_negotiation_spent or 0.0
            ) + session.final_discount
            seller.total_co2_saved_kg = (seller.total_co2_saved_kg or 0.0) + (
                session.carbon_saved_kg or 0.0
            )

    # Persist order
    order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
    total_amount = 0.0
    for item in (session.cart_items or []):
        product = db.query(Product).filter(Product.id == item.get("product_id")).first()
        if product:
            total_amount += product.list_price * item.get("quantity", 1)
    order = Order(
        id=order_id,
        session_id=session_id,
        customer_id=session.customer_id,
        cart_items=session.cart_items,
        total_amount=total_amount,
        final_discount=session.final_discount or 0.0,
        final_gifts=session.final_gifts or [],
        delivery_preference=body.delivery_preference,
        carbon_saved_kg=session.carbon_saved_kg or 0.0,
    )
    db.add(order)
    db.commit()

    return {
        "order_id": order_id,
        "summary": {
            "cart_items": session.cart_items,
            "final_discount": session.final_discount,
            "final_gifts": session.final_gifts,
            "delivery_preference": session.delivery_preference,
            "carbon_saved_kg": session.carbon_saved_kg,
            "purchase_confirmed": True,
        },
    }


@router.get("/orders/{session_id}")
def get_order(session_id: str, db: Session = Depends(get_db)):
    order = (
        db.query(Order)
        .filter(Order.session_id == session_id)
        .order_by(Order.created_at.desc())
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found for this session")
    return {
        "order_id": order.id,
        "session_id": order.session_id,
        "customer_id": order.customer_id,
        "created_at": order.created_at.isoformat(),
        "cart_items": order.cart_items,
        "total_amount": order.total_amount,
        "final_discount": order.final_discount,
        "final_gifts": order.final_gifts,
        "delivery_preference": order.delivery_preference,
        "carbon_saved_kg": order.carbon_saved_kg,
        "net_amount": round(order.total_amount - order.final_discount, 2),
    }
