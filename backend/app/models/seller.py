from sqlalchemy import Boolean, Column, Float, String
from app.database import Base


class Seller(Base):
    __tablename__ = "sellers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    monthly_negotiation_budget = Column(Float, default=5000.0)
    monthly_negotiation_spent = Column(Float, default=0.0)
    min_margin_target = Column(Float, default=0.12)   # minimum acceptable margin
    eco_seller_badge = Column(Boolean, default=False)
    total_co2_saved_kg = Column(Float, default=0.0)
    # Policy fields (exposed via /api/seller/{id}/policy)
    negotiation_active = Column(Boolean, default=True)
    segment_strategy = Column(String, default="balanced")  # aggressive / balanced / gentle
