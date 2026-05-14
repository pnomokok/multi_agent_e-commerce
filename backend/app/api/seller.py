from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent_log import AgentLog
from app.models.seller import Seller
from app.models.session import ShoppingSession
from app.schemas.seller import (
    SellerDashboardOut,
    SellerPolicyIn,
    SellerPolicyOut,
    SellerStatsOut,
)

router = APIRouter()


@router.get("/seller/{seller_id}/dashboard", response_model=SellerDashboardOut)
def seller_dashboard(seller_id: str, db: Session = Depends(get_db)):
    seller = _get_or_404(db, seller_id)
    return SellerDashboardOut(
        policy=_policy_out(seller),
        stats=_compute_stats(db, seller),
    )


@router.get("/seller/{seller_id}/policy", response_model=SellerPolicyOut)
def get_policy(seller_id: str, db: Session = Depends(get_db)):
    return _policy_out(_get_or_404(db, seller_id))


@router.put("/seller/{seller_id}/policy", response_model=SellerPolicyOut)
def update_policy(seller_id: str, body: SellerPolicyIn, db: Session = Depends(get_db)):
    seller = _get_or_404(db, seller_id)
    if body.negotiation_active is not None:
        seller.negotiation_active = body.negotiation_active
    if body.monthly_negotiation_budget is not None:
        seller.monthly_negotiation_budget = body.monthly_negotiation_budget
    if body.min_margin_target is not None:
        seller.min_margin_target = body.min_margin_target
    if body.segment_strategy is not None:
        seller.segment_strategy = body.segment_strategy
    db.commit()
    db.refresh(seller)
    return _policy_out(seller)


@router.get("/seller/{seller_id}/stats", response_model=SellerStatsOut)
def get_stats(seller_id: str, db: Session = Depends(get_db)):
    return _compute_stats(db, _get_or_404(db, seller_id))


@router.get("/seller/{seller_id}/logs")
def get_logs(seller_id: str, limit: int = 50, db: Session = Depends(get_db)):
    _get_or_404(db, seller_id)
    logs = (
        db.query(AgentLog)
        .order_by(AgentLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": l.id,
            "session_id": l.session_id,
            "timestamp": l.timestamp.isoformat(),
            "agent_name": l.agent_name,
            "action": l.action,
            "payload": l.payload,
        }
        for l in logs
    ]


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_or_404(db: Session, seller_id: str) -> Seller:
    s = db.query(Seller).filter(Seller.id == seller_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Seller not found")
    return s


def _policy_out(seller: Seller) -> SellerPolicyOut:
    return SellerPolicyOut(
        seller_id=seller.id,
        negotiation_active=seller.negotiation_active,
        monthly_negotiation_budget=seller.monthly_negotiation_budget,
        monthly_negotiation_spent=seller.monthly_negotiation_spent,
        budget_remaining=seller.monthly_negotiation_budget - seller.monthly_negotiation_spent,
        min_margin_target=seller.min_margin_target,
        segment_strategy=seller.segment_strategy,
    )


def _compute_stats(db: Session, seller: Seller) -> SellerStatsOut:
    sessions = db.query(ShoppingSession).filter(ShoppingSession.purchase_confirmed == True).all()
    total_negotiations = db.query(AgentLog).filter(AgentLog.agent_name == "negotiator").count()
    successful = len([s for s in sessions if s.final_discount and s.final_discount > 0])
    total_discount = sum(s.final_discount or 0.0 for s in sessions)
    co2_total = sum(s.carbon_saved_kg or 0.0 for s in sessions)

    # ROI: each saved order is worth roughly avg cart value minus discount
    avg_cart = 1500.0  # mock estimate
    estimated_saved = successful
    net_roi = round(estimated_saved * avg_cart - total_discount, 2)

    return SellerStatsOut(
        seller_id=seller.id,
        seller_name=seller.name,
        total_negotiations=total_negotiations,
        successful_negotiations=successful,
        total_discount_given=round(total_discount, 2),
        estimated_orders_saved=estimated_saved,
        net_roi=net_roi,
        total_co2_saved_kg=round(seller.total_co2_saved_kg or co2_total, 2),
        eco_seller_badge=seller.eco_seller_badge,
    )
