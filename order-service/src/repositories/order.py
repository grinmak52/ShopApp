import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import Order, OrderStatus


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order, ["items"])
        return order

    async def get_for_user(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Order | None:
        return await self.session.scalar(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )

    async def list_for_user(
        self, user_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Order], int]:
        total = await self.session.scalar(
            select(func.count()).select_from(Order).where(Order.user_id == user_id)
        )
        rows = await self.session.scalars(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc(), Order.id)
            .limit(limit)
            .offset(offset)
        )
        return list(rows), total or 0

    async def set_status(self, order: Order, status: OrderStatus) -> None:
        order.status = status
        await self.session.commit()

    async def transition_from_pending(
        self, order_id: uuid.UUID, new_status: OrderStatus
    ) -> bool:
        result = await self.session.execute(
            update(Order)
            .where(Order.id == order_id, Order.status == OrderStatus.PENDING)
            .values(status=new_status)
        )
        await self.session.commit()
        return result.rowcount == 1