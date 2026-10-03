import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.orm.base import Base
from database.orm.mixins import UUIDPkMixin


class OrderItem(Base, UUIDPkMixin):
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[uuid.UUID]  # просто UUID, без FK на другой сервис
    product_name: Mapped[str] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int] = mapped_column(Integer)

    order: Mapped["Order"] = relationship(back_populates="items")