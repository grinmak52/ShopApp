import enum
import uuid
from decimal import Decimal

from sqlalchemy import Enum, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.orm.base import Base
from database.orm.mixins import TimestampMixin, UUIDPkMixin


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Order(Base, UUIDPkMixin, TimestampMixin):
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
        index=True,
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping_address: Mapped[str] = mapped_column(Text)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )