from sqlalchemy import Boolean, Column, Float, Integer, String, JSON
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    seller_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    list_price = Column(Float, nullable=False)        # displayed price
    base_price = Column(Float, nullable=False)        # floor price — never go below
    margin = Column(Float, nullable=False)            # 0.0-1.0
    stock = Column(Integer, nullable=False, default=0)
    sales_velocity = Column(Float, default=0.0)       # avg daily sales
    weight_kg = Column(Float, default=0.5)
    image_url = Column(String, default="")
    negotiation_enabled = Column(Boolean, default=True)
    max_discount_pct = Column(Float, default=0.10)    # 10% default max
    preferred_concessions = Column(JSON, default=list) # ["discount","gift","bundle"]
