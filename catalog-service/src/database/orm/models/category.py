from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.orm.base import Base
from database.orm.mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .product import Product

class Category(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    products: Mapped[list["Product"]] = relationship(back_populates="category")