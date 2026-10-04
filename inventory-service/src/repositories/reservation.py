import uuid
from datetime import timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import ReservationStatus, StockReservation


class ReservationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_order(
            self, order_id: uuid.UUID, lock: bool = False
    ) -> list[StockReservation]:
        query = select(StockReservation).where(StockReservation.order_id == order_id)
        if lock:
            query = query.with_for_update()
        return list(await self.session.scalars(query))

    def add(self, order_id, product_id, quantity, status: ReservationStatus) -> None:
        self.session.add(
            StockReservation(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                status=status,
            )
        )

    async def get_stale_reserved(self, ttl_seconds: int, limit: int = 100) -> list[StockReservation]:
        threshold = func.now() - timedelta(seconds=ttl_seconds)
        query = (
            select(StockReservation)
            .where(
                StockReservation.status == ReservationStatus.RESERVED,
                StockReservation.created_at < threshold,
            )
            .order_by(StockReservation.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(await self.session.scalars(query))

