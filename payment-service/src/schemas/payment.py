import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from database.orm.models import PaymentStatus


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: uuid.UUID
    amount: Decimal
    status: PaymentStatus
    provider: str
    failure_reason: str | None
    created_at: datetime