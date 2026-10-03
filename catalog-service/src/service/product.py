import uuid

from database.orm.models import Product
from repositories.category import CategoryRepository
from repositories.product import ProductRepository
from schemas.product import ProductCreate, ProductFilters, ProductUpdate
from service.exceptions import NotFoundError


class ProductService:
    def __init__(self, repo: ProductRepository, category_repo: CategoryRepository):
        self.repo = repo
        self.category_repo = category_repo

    async def list(self, filters: ProductFilters) -> tuple[list[Product], int]:
        return await self.repo.list(filters)

    async def get(self, product_id: uuid.UUID) -> Product:
        product = await self.repo.get(product_id)
        if product is None:
            raise NotFoundError("Product")
        return product

    async def _ensure_category(self, category_id: uuid.UUID) -> None:
        if await self.category_repo.get(category_id) is None:
            raise NotFoundError("Category")

    async def create(self, data: ProductCreate) -> Product:
        await self._ensure_category(data.category_id)
        return await self.repo.create(data.model_dump())

    async def update(self, product_id: uuid.UUID, data: ProductUpdate) -> Product:
        product = await self.get(product_id)
        values = data.model_dump(exclude_unset=True)
        if "category_id" in values and values["category_id"] is not None:
            await self._ensure_category(values["category_id"])
        return await self.repo.update(product, values)

    async def deactivate(self, product_id: uuid.UUID) -> None:
        product = await self.get(product_id)
        await self.repo.update(product, {"is_active": False})