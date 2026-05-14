from sqlalchemy import Boolean, Column, Float, JSON, String
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    segment = Column(String, default="new")           # new / loyal / bargain_hunter
    address = Column(String, default="")
    region_code = Column(String, default="IST")
    interaction_history = Column(JSON, default=list)  # last 5 interaction summaries
    total_co2_saved_kg = Column(Float, default=0.0)
    eco_customer_badge = Column(Boolean, default=False)
