import uuid

from sqlalchemy import CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base
from database.orm.mixins import TimestampMixin, UUIDPkMixin


class Inventory(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="quantity_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="reserved_non_negative"),
        CheckConstraint("reserved_quantity <= quantity", name="reserved_lte_quantity"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(unique=True, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0)