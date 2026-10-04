import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_order(self, order_id: uuid.UUID) -> Payment | None:
        return await self.session.scalar(
            select(Payment).where(Payment.order_id == order_id)
        )

    async def get_for_user(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Payment | None:
        return await self.session.scalar(
            select(Payment).where(Payment.order_id == order_id, Payment.user_id == user_id)
        )

    async def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment