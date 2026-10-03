import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, category_id: uuid.UUID) -> Category | None:
        return await self.session.get(Category, category_id)

    async def list(self) -> list[Category]:
        result = await self.session.scalars(select(Category).order_by(Category.name))
        return list(result)

    async def create(self, data: dict) -> Category:
        category = Category(**data)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def update(self, category: Category, data: dict) -> Category:
        for key, value in data.items():
            setattr(category, key, value)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
        await self.session.commit()