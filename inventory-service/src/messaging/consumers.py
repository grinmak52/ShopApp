import logging

from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError

from database.orm.db_helper import db_helper
from messaging.broker import Broker, broker
from messaging.events import OrderCreated, StockReservationFailed, StockReserved
from service.reservation import ReservationService

log = logging.getLogger(__name__)

ORDER_CREATED_QUEUE = "inventory.order_created"


async def handle_order_created(message: AbstractIncomingMessage) -> None:
    try:
        event = OrderCreated.model_validate_json(message.body)
    except ValidationError:
        log.exception("Invalid OrderCreated payload, dropping")
        await message.reject(requeue=False)
        return

    try:
        async with db_helper.session_factory() as session:
            result = await ReservationService(session).reserve_order(event)

        if result.success:
            await broker.publish(
                "stock.reserved",
                StockReserved(
                    order_id=event.order_id,
                    user_id=event.user_id,
                    total_price=event.total_price,
                ),
            )
        else:
            await broker.publish(
                "stock.reservation_failed",
                StockReservationFailed(order_id=event.order_id, reason=result.reason),
            )
    except Exception:
        log.exception("Failed to process order %s, requeue", event.order_id)
        await message.nack(requeue=True)
        return

    await message.ack()


async def start_consumers(b: Broker) -> None:
    queue = await b.channel.declare_queue(ORDER_CREATED_QUEUE, durable=True)
    await queue.bind(b.exchange, routing_key="order.created")
    await queue.consume(handle_order_created)