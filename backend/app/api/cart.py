import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent_log import AgentLog
from app.models.product import Product
from app.models.session import ShoppingSession
from app.schemas.product import CartItemIn, CartItemOut, CartOut
from app.schemas.session import SessionStartIn, SessionOut

router = APIRouter()


@router.post("/session/start", response_model=SessionOut)
def start_session(body: SessionStartIn, db: Session = Depends(get_db)):
    session = ShoppingSession(
        id=str(uuid.uuid4()),
        customer_id=body.customer_id,
        cart_items=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _session_out(session)


@router.get("/session/{session_id}", response_model=SessionOut)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = _get_or_404(db, session_id)
    return _session_out(session)


@router.post("/cart/{session_id}/add", response_model=CartOut)
def add_to_cart(session_id: str, body: CartItemIn, db: Session = Depends(get_db)):
    session = _get_or_404(db, session_id)
    product = db.query(Product).filter(Product.id == body.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    items: list[dict] = list(session.cart_items or [])
    for item in items:
        if item["product_id"] == body.product_id:
            item["quantity"] += body.quantity
            break
    else:
        items.append({"product_id": body.product_id, "quantity": body.quantity})

    session.cart_items = items
    db.commit()
    return _build_cart_out(session_id, items, db)


@router.post("/cart/{session_id}/remove", response_model=CartOut)
def remove_from_cart(session_id: str, body: CartItemIn, db: Session = Depends(get_db)):
    session = _get_or_404(db, session_id)
    items = [i for i in (session.cart_items or []) if i["product_id"] != body.product_id]
    session.cart_items = items
    db.commit()
    return _build_cart_out(session_id, items, db)


@router.get("/cart/{session_id}", response_model=CartOut)
def get_cart(session_id: str, db: Session = Depends(get_db)):
    session = _get_or_404(db, session_id)
    return _build_cart_out(session_id, session.cart_items or [], db)


@router.get("/sessions/{session_id}/logs")
def get_session_logs(session_id: str, db: Session = Depends(get_db)):
    _get_or_404(db, session_id)
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.session_id == session_id)
        .order_by(AgentLog.timestamp)
        .all()
    )
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.strftime("%H:%M:%S"),
            "agent": log.agent_name,
            "action": log.action,
            "payload": log.payload,
        }
        for log in logs
    ]


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_or_404(db: Session, session_id: str) -> ShoppingSession:
    s = db.query(ShoppingSession).filter(ShoppingSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


def _build_cart_out(session_id: str, items: list[dict], db: Session) -> CartOut:
    result: list[CartItemOut] = []
    subtotal = 0.0
    total_weight = 0.0
    for item in items:
        p = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not p:
            continue
        qty = item["quantity"]
        line = CartItemOut(
            product_id=p.id,
            name=p.name,
            quantity=qty,
            unit_price=p.list_price,
            total_price=round(p.list_price * qty, 2),
            weight_kg=p.weight_kg,
        )
        result.append(line)
        subtotal += line.total_price
        total_weight += p.weight_kg * qty
    return CartOut(
        session_id=session_id,
        items=result,
        subtotal=round(subtotal, 2),
        total_weight_kg=round(total_weight, 3),
    )


def _session_out(s: ShoppingSession) -> SessionOut:
    pref = s.delivery_preference or "express"
    return SessionOut(
        session_id=s.id,
        customer_id=s.customer_id,
        cart_items=s.cart_items or [],
        negotiation_history=s.negotiation_history or [],
        final_discount=s.final_discount or 0.0,
        final_gifts=s.final_gifts or [],
        purchase_confirmed=s.purchase_confirmed or False,
        delivery_preference=pref,
        awaiting_delivery_choice=(pref == "pending_customer_choice"),
        carbon_saved_kg=s.carbon_saved_kg or 0.0,
        negotiation_quota_used=s.negotiation_quota_used or 0,
        created_at=s.created_at,
    )
