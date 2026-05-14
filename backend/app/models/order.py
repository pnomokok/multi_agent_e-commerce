from datetime import datetime

from sqlalchemy import Column, DateTime, Float, JSON, String

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)           # ORD-XXXXXXXX
    session_id = Column(String, nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cart_items = Column(JSON, default=list)
    total_amount = Column(Float, default=0.0)       # list price total
    final_discount = Column(Float, default=0.0)
    final_gifts = Column(JSON, default=list)
    delivery_preference = Column(String, default="express")
    carbon_saved_kg = Column(Float, default=0.0)
