import logging
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models import ReservationStatus
from messaging.events import OrderCreated
from repositories.inventory import InventoryRepository
from repositories.reservation import ReservationRepository

log = logging.getLogger(__name__)


@dataclass
class ReserveResult:
    success: bool
    reason: str | None = None


class ReservationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.inventory = InventoryRepository(session)
        self.reservations = ReservationRepository(session)

    async def reserve_order(self, event: OrderCreated) -> ReserveResult:
        # идемпотентность: заказ уже обработан, возвращаем прежний итог
        existing = await self.reservations.get_by_order(event.order_id)
        if existing:
            failed = any(r.status == ReservationStatus.FAILED for r in existing)
            return ReserveResult(
                success=not failed,
                reason="insufficient stock" if failed else None,
            )

        # одинаковые товары в заказе суммируем
        totals: dict = defaultdict(int)
        for item in event.items:
            totals[item.product_id] += item.quantity

        # фиксированный порядок блокировок исключает взаимные блокировки (deadlock)
        for product_id, qty in sorted(totals.items(), key=lambda x: str(x[0])):
            if not await self.inventory.try_reserve(product_id, qty):
                await self.session.rollback()  # откатывает уже сделанные резервы
                self.reservations.add(
                    event.order_id, product_id, qty, ReservationStatus.FAILED
                )
                await self.session.commit()
                return ReserveResult(False, "insufficient stock")
            self.reservations.add(
                event.order_id, product_id, qty, ReservationStatus.RESERVED
            )

        await self.session.commit()
        return ReserveResult(True)

    async def confirm_order(self, order_id) -> None:
        """Оплата прошла: окончательно списываем зарезервированное."""
        reservations = await self.reservations.get_by_order(order_id, lock=True)
        to_confirm = [r for r in reservations if r.status == ReservationStatus.RESERVED]
        if not to_confirm:
            log.info("Order %s: nothing to confirm (duplicate or unknown)", order_id)
            return

        for r in sorted(to_confirm, key=lambda r: str(r.product_id)):
            await self.inventory.commit_sale(r.product_id, r.quantity)
            r.status = ReservationStatus.CONFIRMED
        await self.session.commit()

    async def release_order(self, order_id) -> None:
        """Оплата не прошла: возвращаем резерв в свободный остаток."""
        reservations = await self.reservations.get_by_order(order_id, lock=True)
        to_release = [r for r in reservations if r.status == ReservationStatus.RESERVED]
        if not to_release:
            log.info("Order %s: nothing to release (duplicate or unknown)", order_id)
            return

        for r in sorted(to_release, key=lambda r: str(r.product_id)):
            await self.inventory.release(r.product_id, r.quantity)
            r.status = ReservationStatus.RELEASED
        await self.session.commit()
