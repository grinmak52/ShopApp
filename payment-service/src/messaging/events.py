import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class StockReserved(BaseModel):
    event_id: uuid.UUID
    order_id: uuid.UUID
    user_id: uuid.UUID
    total_price: Decimal


class PaymentSucceeded(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    order_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal


class PaymentFailed(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    order_id: uuid.UUID
    reason: str