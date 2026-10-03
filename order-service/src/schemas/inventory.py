import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field


class InventoryCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=0)


class InventoryUpdate(BaseModel):
    quantity: int = Field(ge=0)


class InventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    quantity: int
    reserved_quantity: int
    updated_at: datetime

    @computed_field
    @property
    def available(self) -> int:
        return self.quantity - self.reserved_quantity