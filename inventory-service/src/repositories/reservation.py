import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import ReservationStatus, StockReservation


class ReservationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_order(self, order_id: uuid.UUID) -> list[StockReservation]:
        result = await self.session.scalars(
            select(StockReservation).where(StockReservation.order_id == order_id)
        )
        return list(result)

    def add(self, order_id, product_id, quantity, status: ReservationStatus) -> None:
        self.session.add(
            StockReservation(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                status=status,
            )
        )