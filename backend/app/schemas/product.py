from pydantic import BaseModel


class ProductOut(BaseModel):
    id: str
    seller_id: str
    name: str
    category: str
    list_price: float
    stock: int
    weight_kg: float
    image_url: str
    negotiation_enabled: bool

    model_config = {"from_attributes": True}


class CartItemIn(BaseModel):
    product_id: str
    quantity: int = 1


class CartItemOut(BaseModel):
    product_id: str
    name: str
    quantity: int
    unit_price: float
    total_price: float
    weight_kg: float


class CartOut(BaseModel):
    session_id: str
    items: list[CartItemOut]
    subtotal: float
    total_weight_kg: float
