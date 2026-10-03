import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderEventItem(BaseModel):
    product_id: uuid.UUID
    quantity: int


class OrderCreated(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    order_id: uuid.UUID
    user_id: uuid.UUID
    total_price: Decimal
    items: list[OrderEventItem]