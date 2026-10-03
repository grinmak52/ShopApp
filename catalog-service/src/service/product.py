import hashlib
import uuid

from cache.redis import Cache
from repositories.category import CategoryRepository
from repositories.product import ProductRepository
from schemas.product import (
    ProductCreate,
    ProductFilters,
    ProductPage,
    ProductRead,
    ProductUpdate,
)
from service.exceptions import NotFoundError

VERSION_KEY = "products:version"


class ProductService:
    def __init__(
        self, repo: ProductRepository, category_repo: CategoryRepository, cache: Cache
    ):
        self.repo = repo
        self.category_repo = category_repo
        self.cache = cache

    async def list(self, filters: ProductFilters) -> ProductPage:
        version = await self.cache.version(VERSION_KEY)
        digest = hashlib.sha256(filters.model_dump_json().encode()).hexdigest()[:16]
        key = f"products:list:v{version}:{digest}"

        if cached := await self.cache.get(key):
            return ProductPage.model_validate_json(cached)

        items, total = await self.repo.list(filters)
        page = ProductPage(
            items=[ProductRead.model_validate(p) for p in items],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )
        await self.cache.set(key, page.model_dump_json())
        return page

    async def get(self, product_id: uuid.UUID) -> ProductRead:
        key = f"product:{product_id}"
        if cached := await self.cache.get(key):
            return ProductRead.model_validate_json(cached)

        product = await self._get_or_404(product_id)
        result = ProductRead.model_validate(product)
        await self.cache.set(key, result.model_dump_json())
        return result

    async def create(self, data: ProductCreate) -> ProductRead:
        await self._ensure_category(data.category_id)
        product = await self.repo.create(data.model_dump())
        await self.cache.bump(VERSION_KEY)
        return ProductRead.model_validate(product)

    async def update(self, product_id: uuid.UUID, data: ProductUpdate) -> ProductRead:
        product = await self._get_or_404(product_id)
        values = data.model_dump(exclude_unset=True)
        if values.get("category_id") is not None:
            await self._ensure_category(values["category_id"])
        product = await self.repo.update(product, values)
        await self._invalidate(product_id)
        return ProductRead.model_validate(product)

    async def deactivate(self, product_id: uuid.UUID) -> None:
        product = await self._get_or_404(product_id)
        await self.repo.update(product, {"is_active": False})
        await self._invalidate(product_id)

    async def _get_or_404(self, product_id: uuid.UUID):
        product = await self.repo.get(product_id)
        if product is None:
            raise NotFoundError("Product")
        return product

    async def _ensure_category(self, category_id: uuid.UUID) -> None:
        if await self.category_repo.get(category_id) is None:
            raise NotFoundError("Category")

    async def _invalidate(self, product_id: uuid.UUID) -> None:
        await self.cache.delete(f"product:{product_id}")
        await self.cache.bump(VERSION_KEY)