import uuid
from decimal import Decimal

from pydantic import BaseModel


class OrderCreated(BaseModel):
    order_id: uuid.UUID
    user_id: uuid.UUID
    total_price: Decimal


class OrderConfirmed(BaseModel):
    order_id: uuid.UUID
    user_id: uuid.UUID


class OrderCancelled(BaseModel):
    order_id: uuid.UUID
    user_id: uuid.UUID
    reason: str


class PaymentSucceeded(BaseModel):
    order_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal


class PaymentFailed(BaseModel):
    order_id: uuid.UUID
    user_id: uuid.UUID
    reason: str