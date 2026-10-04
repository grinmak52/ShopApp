import enum
import uuid
from decimal import Decimal

from sqlalchemy import Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base
from database.orm.mixins import TimestampMixin, UUIDPkMixin


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(Base, UUIDPkMixin, TimestampMixin):
    order_id: Mapped[uuid.UUID] = mapped_column(unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.PENDING
    )
    provider: Mapped[str] = mapped_column(String(50))
    transaction_id: Mapped[str | None] = mapped_column(String(100))
    failure_reason: Mapped[str | None] = mapped_column(String(255))