import uuid

from pydantic import TypeAdapter
from sqlalchemy.exc import IntegrityError

from cache.redis import Cache
from database.orm.models import Category
from repositories.category import CategoryRepository
from schemas.category import CategoryRead, CategoryUpdate, CategoryCreate
from service.exceptions import ConflictError, NotFoundError

CATEGORIES_KEY = "categories:list"
categories_adapter = TypeAdapter(list[CategoryRead])


class CategoryService:
    def __init__(self, repo: CategoryRepository, cache: Cache):
        self.repo = repo
        self.cache = cache

    async def list(self) -> list[CategoryRead]:
        if cached := await self.cache.get(CATEGORIES_KEY):
            return categories_adapter.validate_json(cached)

        categories = await self.repo.list()
        result = categories_adapter.validate_python(categories, from_attributes=True)
        await self.cache.set(
            CATEGORIES_KEY,
            categories_adapter.dump_json(result).decode(),
        )
        return result

    async def get(self, category_id: uuid.UUID) -> Category:
        category = await self.repo.get(category_id)
        if category is None:
            raise NotFoundError("Category")
        return category

    async def create(self, data: CategoryCreate) -> Category:
        try:
            category = await self.repo.create(data.model_dump())
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Category with this name or slug already exists")

        await self.cache.delete(CATEGORIES_KEY)
        return category

    async def update(self, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
        category = await self.get(category_id)
        try:
            updated = await self.repo.update(
                category, data.model_dump(exclude_unset=True)
            )
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Category with this name or slug already exists")

        await self.cache.delete(CATEGORIES_KEY)
        return updated

    async def delete(self, category_id: uuid.UUID) -> None:
        category = await self.get(category_id)
        try:
            await self.repo.delete(category)
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Category has products and cannot be deleted")

        await self.cache.delete(CATEGORIES_KEY)