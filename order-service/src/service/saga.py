import logging
import uuid

from database.orm.models import OrderStatus
from repositories.order import OrderRepository

log = logging.getLogger(__name__)


class OrderSagaService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def confirm(self, order_id: uuid.UUID) -> None:
        if await self.repo.transition_from_pending(order_id, OrderStatus.CONFIRMED):
            log.info("Order %s confirmed", order_id)
        else:
            log.warning("Order %s: confirm ignored (not PENDING or unknown)", order_id)

    async def cancel(self, order_id: uuid.UUID, reason: str) -> None:
        if await self.repo.transition_from_pending(order_id, OrderStatus.CANCELLED):
            log.info("Order %s cancelled: %s", order_id, reason)
        else:
            log.warning("Order %s: cancel ignored (not PENDING or unknown)", order_id)