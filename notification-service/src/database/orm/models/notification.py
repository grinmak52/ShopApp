import enum
import uuid

from sqlalchemy import Boolean, Enum, String, Text, UniqueConstraint, false
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base
from database.orm.mixins import TimestampMixin, UUIDPkMixin


class NotificationType(str, enum.Enum):
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    PAYMENT_SUCCEEDED = "PAYMENT_SUCCEEDED"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class Notification(Base, UUIDPkMixin, TimestampMixin):
    __table_args__ = (
        UniqueConstraint("order_id", "type", name="order_type"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    order_id: Mapped[uuid.UUID]
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type")
    )
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, server_default=false(), index=True)