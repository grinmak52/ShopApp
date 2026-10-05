import asyncio
import logging
from typing import Awaitable, Callable

from aio_pika.abc import AbstractIncomingMessage
from pydantic import BaseModel, ValidationError

from database.orm.db_helper import db_helper
from messaging.broker import Broker, broker
from messaging.events import (
    PaymentFailed,
    PaymentSucceeded,
    StockReservationExpired,
    StockReservationFailed,
)
from repositories.order import OrderRepository
from service.saga import OrderSagaService

log = logging.getLogger(__name__)


async def _process(
    message: AbstractIncomingMessage,
    model: type[BaseModel],
    action: Callable[[OrderSagaService, BaseModel], Awaitable[None]],
) -> None:
    try:
        event = model.model_validate_json(message.body)
    except ValidationError:
        log.exception("Invalid %s payload, dropping", model.__name__)
        await message.reject(requeue=False)
        return

    try:
        async with db_helper.session_factory() as session:
            await action(OrderSagaService(OrderRepository(session), broker), event)
    except Exception:
        log.exception("Failed to process %s, requeue", model.__name__)
        await asyncio.sleep(5)
        await message.nack(requeue=True)
        return

    await message.ack()


async def handle_stock_failed(message: AbstractIncomingMessage) -> None:
    async def action(service: OrderSagaService, event: StockReservationFailed) -> None:
        await service.cancel(event.order_id, f"stock: {event.reason}")

    await _process(message, StockReservationFailed, action)



async def handle_stock_expired(message: AbstractIncomingMessage) -> None:
    async def action(service: OrderSagaService, event: StockReservationExpired) -> None:
        await service.cancel(event.order_id, f"stock: {event.reason}")

    await _process(message, StockReservationExpired, action)

async def handle_payment_succeeded(message: AbstractIncomingMessage) -> None:
    async def action(service: OrderSagaService, event: PaymentSucceeded) -> None:
        await service.confirm(event.order_id)

    await _process(message, PaymentSucceeded, action)


async def handle_payment_failed(message: AbstractIncomingMessage) -> None:
    async def action(service: OrderSagaService, event: PaymentFailed) -> None:
        await service.cancel(event.order_id, f"payment: {event.reason}")

    await _process(message, PaymentFailed, action)


async def start_consumers(b: Broker) -> None:
    bindings = [
        ("order.stock_reservation_failed", "stock.reservation_failed", handle_stock_failed),
        ("order.stock_reservation_expired", "stock.reservation_expired", handle_stock_expired),
        ("order.payment_succeeded", "payment.succeeded", handle_payment_succeeded),
        ("order.payment_failed", "payment.failed", handle_payment_failed),
    ]
    for queue_name, routing_key, handler in bindings:
        queue = await b.channel.declare_queue(queue_name, durable=True)
        await queue.bind(b.exchange, routing_key=routing_key)
        await queue.consume(handler)