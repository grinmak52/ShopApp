import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.orm.base import Base
from database.orm.mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .category import Category


class Product(Base, UUIDPkMixin, TimestampMixin):
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    image: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())

    category: Mapped["Category"] = relationship(back_populates="products")