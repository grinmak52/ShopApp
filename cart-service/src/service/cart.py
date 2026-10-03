import uuid

from clients.catalog import CatalogClient
from repositories.cart import CartRepository
from schemas.cart import (
    MAX_DISTINCT_ITEMS,
    MAX_QUANTITY,
    CartItem,
    CartRead,
)
from service.exceptions import BadRequestError, NotFoundError


class CartService:
    def __init__(self, repo: CartRepository, catalog: CatalogClient):
        self.repo = repo
        self.catalog = catalog

    async def get(self, user_id: uuid.UUID) -> CartRead:
        raw = await self.repo.get_all(user_id)
        items = [CartItem(product_id=pid, quantity=qty) for pid, qty in raw.items()]
        return CartRead(items=items, total_quantity=sum(i.quantity for i in items))

    async def add_item(self, user_id: uuid.UUID, product_id: uuid.UUID, qty: int) -> CartRead:
        await self.catalog.ensure_available(product_id)

        if (
            not await self.repo.exists(user_id, product_id)
            and await self.repo.count(user_id) >= MAX_DISTINCT_ITEMS
        ):
            raise BadRequestError(f"Cart cannot hold more than {MAX_DISTINCT_ITEMS} different products")

        new_qty = await self.repo.increment(user_id, product_id, qty)
        if new_qty > MAX_QUANTITY:
            await self.repo.increment(user_id, product_id, -qty)  # откат
            raise BadRequestError(f"Maximum quantity per product is {MAX_QUANTITY}")
        return await self.get(user_id)

    async def set_quantity(self, user_id: uuid.UUID, product_id: uuid.UUID, qty: int) -> CartRead:
        if not await self.repo.exists(user_id, product_id):
            raise NotFoundError("Cart item")
        await self.repo.set_quantity(user_id, product_id, qty)
        return await self.get(user_id)

    async def remove_item(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None:
        if not await self.repo.remove(user_id, product_id):
            raise NotFoundError("Cart item")

    async def clear(self, user_id: uuid.UUID) -> None:
        await self.repo.clear(user_id)