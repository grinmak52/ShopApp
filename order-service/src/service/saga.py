import logging
import uuid

from database.orm.models import OrderStatus
from messaging.broker import Broker
from messaging.events import OrderCancelled, OrderConfirmed
from repositories.order import OrderRepository

log = logging.getLogger(__name__)


class OrderSagaService:
    def __init__(self, repo: OrderRepository, broker: Broker):
        self.repo = repo
        self.broker = broker

    async def confirm(self, order_id: uuid.UUID) -> None:
        user_id = await self.repo.transition_from_pending(order_id, OrderStatus.CONFIRMED)
        if user_id is None:
            log.warning("Order %s: confirm ignored (not PENDING or unknown)", order_id)
            return
        log.info("Order %s confirmed", order_id)
        await self.broker.publish(
            "order.confirmed", OrderConfirmed(order_id=order_id, user_id=user_id)
        )

    async def cancel(self, order_id: uuid.UUID, reason: str) -> None:
        user_id = await self.repo.transition_from_pending(order_id, OrderStatus.CANCELLED)
        if user_id is None:
            log.warning("Order %s: cancel ignored (not PENDING or unknown)", order_id)
            return
        log.info("Order %s cancelled: %s", order_id, reason)
        await self.broker.publish(
            "order.cancelled",
            OrderCancelled(order_id=order_id, user_id=user_id, reason=reason),
        )