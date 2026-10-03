import enum
import uuid

from sqlalchemy import Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base
from database.orm.mixins import TimestampMixin, UUIDPkMixin


class ReservationStatus(str, enum.Enum):
    PENDING = "PENDING"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class StockReservation(Base, UUIDPkMixin, TimestampMixin):
    order_id: Mapped[uuid.UUID] = mapped_column(index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, name="reservation_status"),
        default=ReservationStatus.PENDING,
    )