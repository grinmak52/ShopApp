import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from database.orm.models import OrderStatus


class OrderCreate(BaseModel):
    shipping_address: str = Field(min_length=5, max_length=500)


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    product_name: str
    price: Decimal
    quantity: int


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: OrderStatus
    total_price: Decimal
    shipping_address: str
    items: list[OrderItemRead]
    created_at: datetime
    updated_at: datetime


class OrderPage(BaseModel):
    items: list[OrderRead]
    total: int
    limit: int
    offset: int