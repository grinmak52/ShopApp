import uuid

from sqlalchemy.exc import IntegrityError

from database.orm.models import Category
from repositories.category import CategoryRepository
from schemas.category import CategoryCreate, CategoryUpdate
from service.exceptions import ConflictError, NotFoundError


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def list(self) -> list[Category]:
        return await self.repo.list()

    async def get(self, category_id: uuid.UUID) -> Category:
        category = await self.repo.get(category_id)
        if category is None:
            raise NotFoundError("Category")
        return category

    async def create(self, data: CategoryCreate) -> Category:
        try:
            return await self.repo.create(data.model_dump())
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Category with this name or slug already exists")

    async def update(self, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
        category = await self.get(category_id)
        try:
            return await self.repo.update(category, data.model_dump(exclude_unset=True))
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Category with this name or slug already exists")

    async def delete(self, category_id: uuid.UUID) -> None:
        category = await self.get(category_id)
        try:
            await self.repo.delete(category)
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Category has products and cannot be deleted")