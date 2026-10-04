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
        if user_id is not None:
            log.info("Order %s confirmed", order_id)
            await self.broker.publish(
                "order.confirmed", OrderConfirmed(order_id=order_id, user_id=user_id)
            )
            return

        order = await self.repo.get(order_id)
        if order is not None and order.status == OrderStatus.CANCELLED:
            # деньги пришли за отменённый заказ: просим Payment вернуть их
            log.warning("Order %s: payment for cancelled order, requesting refund", order_id)
            await self.broker.publish(
                "order.cancelled",
                OrderCancelled(
                    order_id=order_id,
                    user_id=order.user_id,
                    reason="late payment for cancelled order",
                ),
            )
        else:
            log.warning("Order %s: confirm ignored", order_id)

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