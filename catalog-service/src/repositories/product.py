import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import Product
from schemas.product import ProductFilters, ProductSort

SORT_COLUMNS = {
    ProductSort.price_asc: Product.price.asc(),
    ProductSort.price_desc: Product.price.desc(),
    ProductSort.name_asc: Product.name.asc(),
    ProductSort.newest: Product.created_at.desc(),
}


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, product_id: uuid.UUID) -> Product | None:
        return await self.session.get(Product, product_id)

    async def list(
        self, filters: ProductFilters, only_active: bool = True
    ) -> tuple[list[Product], int]:
        conditions = []
        if only_active:
            conditions.append(Product.is_active.is_(True))
        if filters.q:
            conditions.append(Product.name.ilike(f"%{filters.q}%"))
        if filters.category_id:
            conditions.append(Product.category_id == filters.category_id)
        if filters.min_price is not None:
            conditions.append(Product.price >= filters.min_price)
        if filters.max_price is not None:
            conditions.append(Product.price <= filters.max_price)

        total = await self.session.scalar(
            select(func.count()).select_from(Product).where(*conditions)
        )
        query = (
            select(Product)
            .where(*conditions)
            .order_by(SORT_COLUMNS[filters.sort], Product.id)
            .limit(filters.limit)
            .offset(filters.offset)
        )
        items = list(await self.session.scalars(query))
        return items, total or 0

    async def create(self, data: dict) -> Product:
        product = Product(**data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product: Product, data: dict) -> Product:
        for key, value in data.items():
            setattr(product, key, value)
        await self.session.commit()
        await self.session.refresh(product)
        return product