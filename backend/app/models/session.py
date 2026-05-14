from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String
from app.database import Base


class ShoppingSession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    cart_items = Column(JSON, default=list)           # [{product_id, quantity, ...}]
    negotiation_history = Column(JSON, default=list)  # [{role, content, ...}]
    final_discount = Column(Float, default=0.0)
    final_gifts = Column(JSON, default=list)
    purchase_confirmed = Column(Boolean, default=False)
    delivery_preference = Column(String, default="express")  # express / consolidated
    carbon_saved_kg = Column(Float, default=0.0)
    negotiation_quota_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
