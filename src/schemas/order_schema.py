from typing import List, Optional

from pydantic import BaseModel

from src.models.order_model import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    client_id: int
    items: List[OrderItemCreate]


class OrderItemOutput(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        orm_mode = True


class OrderOutput(BaseModel):
    id: int
    client_id: int
    status: OrderStatus
    total: float
    items: List[OrderItemOutput]

    class Config:
        orm_mode = True


class ListOrders(BaseModel):
    orders: List[OrderOutput]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
