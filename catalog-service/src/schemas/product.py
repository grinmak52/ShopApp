import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    category_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    image: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class ProductUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    image: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    image: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductSort(str, Enum):
    price_asc = "price"
    price_desc = "-price"
    name_asc = "name"
    newest = "-created_at"


class ProductFilters(BaseModel):
    q: str | None = None
    category_id: uuid.UUID | None = None
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    sort: ProductSort = ProductSort.newest
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ProductPage(BaseModel):
    items: list[ProductRead]
    total: int
    limit: int
    offset: int