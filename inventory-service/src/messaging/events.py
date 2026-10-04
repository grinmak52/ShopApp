import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0)


class OrderCreated(BaseModel):
    event_id: uuid.UUID
    order_id: uuid.UUID
    user_id: uuid.UUID
    total_price: Decimal
    items: list[OrderItem] = Field(min_length=1)


class OrderCancelled(BaseModel):
    order_id: uuid.UUID


class StockReserved(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    order_id: uuid.UUID
    user_id: uuid.UUID
    total_price: Decimal


class StockReservationFailed(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    order_id: uuid.UUID
    reason: str


class PaymentSucceeded(BaseModel):
    event_id: uuid.UUID
    order_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal


class PaymentFailed(BaseModel):
    event_id: uuid.UUID
    order_id: uuid.UUID
    reason: str