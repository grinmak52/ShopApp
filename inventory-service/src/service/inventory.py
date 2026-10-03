import uuid

from sqlalchemy.exc import IntegrityError

from database.orm.models import Inventory
from repositories.inventory import InventoryRepository
from service.exceptions import ConflictError, NotFoundError


class InventoryService:
    def __init__(self, repo: InventoryRepository):
        self.repo = repo

    async def get(self, product_id: uuid.UUID) -> Inventory:
        item = await self.repo.get_by_product(product_id)
        if item is None:
            raise NotFoundError("Inventory")
        return item

    async def create(self, product_id: uuid.UUID, quantity: int) -> Inventory:
        if await self.repo.get_by_product(product_id):
            raise ConflictError("Inventory for this product already exists")
        try:
            return await self.repo.create(product_id, quantity)
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Inventory for this product already exists")

    async def set_quantity(self, product_id: uuid.UUID, quantity: int) -> Inventory:
        item = await self.get(product_id)
        if quantity < item.reserved_quantity:
            raise ConflictError(
                f"Quantity cannot be lower than reserved ({item.reserved_quantity})"
            )
        try:
            return await self.repo.set_quantity(item, quantity)
        except IntegrityError:
            await self.repo.session.rollback()
            raise ConflictError("Quantity is lower than reserved")