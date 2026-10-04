import logging
from typing import Awaitable, Callable

from aio_pika.abc import AbstractIncomingMessage
from pydantic import BaseModel, ValidationError

from database.orm.db_helper import db_helper
from messaging.broker import Broker, broker
from messaging.events import (
    OrderCreated,
    PaymentFailed,
    PaymentSucceeded,
    StockReservationFailed,
    StockReserved,
    OrderCancelled,
)
from service.reservation import ReservationService

log = logging.getLogger(__name__)

ORDER_CREATED_QUEUE = "inventory.order_created"
ORDER_CANCELLED_QUEUE = "inventory.order_cancelled"
PAYMENT_SUCCEEDED_QUEUE = "inventory.payment_succeeded"
PAYMENT_FAILED_QUEUE = "inventory.payment_failed"


async def handle_order_cancelled(message: AbstractIncomingMessage) -> None:
    async def action(service: ReservationService, event: OrderCancelled) -> None:
        await service.release_order(event.order_id)

    await _process(message, OrderCancelled, action)


async def _process(
        message: AbstractIncomingMessage,
        model: type[BaseModel],
        action: Callable[[ReservationService, BaseModel], Awaitable[None]],
) -> None:
    try:
        event = model.model_validate_json(message.body)
    except ValidationError:
        log.exception("Invalid %s payload, dropping", model.__name__)
        await message.reject(requeue=False)
        return

    try:
        async with db_helper.session_factory() as session:
            await action(ReservationService(session), event)
    except Exception:
        log.exception("Failed to process %s, requeue", model.__name__)
        await message.nack(requeue=True)
        return

    await message.ack()


async def handle_order_created(message: AbstractIncomingMessage) -> None:
    async def action(service: ReservationService, event: OrderCreated) -> None:
        result = await service.reserve_order(event)
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

    await _process(message, OrderCreated, action)


async def handle_payment_succeeded(message: AbstractIncomingMessage) -> None:
    async def action(service: ReservationService, event: PaymentSucceeded) -> None:
        await service.confirm_order(event.order_id)

    await _process(message, PaymentSucceeded, action)


async def handle_payment_failed(message: AbstractIncomingMessage) -> None:
    async def action(service: ReservationService, event: PaymentFailed) -> None:
        await service.release_order(event.order_id)

    await _process(message, PaymentFailed, action)


async def start_consumers(b: Broker) -> None:
    bindings = [
        (ORDER_CREATED_QUEUE, "order.created", handle_order_created),
        (ORDER_CANCELLED_QUEUE, "order.cancelled", handle_order_cancelled),
        (PAYMENT_SUCCEEDED_QUEUE, "payment.succeeded", handle_payment_succeeded),
        (PAYMENT_FAILED_QUEUE, "payment.failed", handle_payment_failed),
    ]
    for queue_name, routing_key, handler in bindings:
        queue = await b.channel.declare_queue(queue_name, durable=True)
        await queue.bind(b.exchange, routing_key=routing_key)
        await queue.consume(handler)
