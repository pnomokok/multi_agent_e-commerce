from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.schemas.product import ProductOut

router = APIRouter()


@router.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/personas")
def list_personas(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "segment": c.segment,
            "region_code": c.region_code,
            "eco_customer_badge": c.eco_customer_badge,
            "total_co2_saved_kg": c.total_co2_saved_kg,
        }
        for c in customers
    ]
