import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import Inventory


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_product(self, product_id: uuid.UUID) -> Inventory | None:
        return await self.session.scalar(
            select(Inventory).where(Inventory.product_id == product_id)
        )

    async def try_reserve(self, product_id: uuid.UUID, qty: int) -> bool:
        result = await self.session.execute(
            update(Inventory)
            .where(
                Inventory.product_id == product_id,
                Inventory.quantity - Inventory.reserved_quantity >= qty,
            )
            .values(reserved_quantity=Inventory.reserved_quantity + qty)
        )
        return result.rowcount == 1

    async def release(self, product_id: uuid.UUID, qty: int) -> None:
        await self.session.execute(
            update(Inventory)
            .where(Inventory.product_id == product_id)
            .values(reserved_quantity=Inventory.reserved_quantity - qty)
        )

    async def commit_sale(self, product_id: uuid.UUID, qty: int) -> None:
        # окончательное списание после успешной оплаты
        await self.session.execute(
            update(Inventory)
            .where(Inventory.product_id == product_id)
            .values(
                quantity=Inventory.quantity - qty,
                reserved_quantity=Inventory.reserved_quantity - qty,
            )
        )

    async def create(self, product_id: uuid.UUID, quantity: int) -> Inventory:
        item = Inventory(product_id=product_id, quantity=quantity, reserved_quantity=0)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def set_quantity(self, item: Inventory, quantity: int) -> Inventory:
        item.quantity = quantity
        await self.session.commit()
        await self.session.refresh(item)
        return item