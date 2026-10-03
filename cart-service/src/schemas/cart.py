import uuid

from pydantic import BaseModel, Field

MAX_QUANTITY = 99
MAX_DISTINCT_ITEMS = 50


class CartItemAdd(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, le=MAX_QUANTITY)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=MAX_QUANTITY)


class CartItem(BaseModel):
    product_id: uuid.UUID
    quantity: int


class CartRead(BaseModel):
    items: list[CartItem]
    total_quantity: int