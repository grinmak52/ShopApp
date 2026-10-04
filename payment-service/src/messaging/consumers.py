import asyncio
import logging

from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError

from database.orm.db_helper import db_helper
from database.orm.models import PaymentStatus
from messaging.broker import Broker, broker
from messaging.events import (
    PaymentFailed,
    PaymentSucceeded,
    StockReserved,
    OrderCancelled,
    PaymentRefunded,
)
from providers.mock import MockPaymentProvider
from repositories.payment import PaymentRepository
from service.payment import PaymentService

log = logging.getLogger(__name__)
provider = MockPaymentProvider()


async def handle_order_cancelled(message: AbstractIncomingMessage) -> None:
    try:
        event = OrderCancelled.model_validate_json(message.body)
    except ValidationError:
        log.exception("Invalid OrderCancelled payload, dropping")
        await message.reject(requeue=False)
        return

    try:
        async with db_helper.session_factory() as session:
            row = await PaymentService(PaymentRepository(session), provider).refund(event.order_id)
        if row is not None:
            await broker.publish(
                "payment.refunded",
                PaymentRefunded(order_id=event.order_id, user_id=row.user_id, amount=row.amount),
            )
    except Exception:
        log.exception("Failed to refund order %s, requeue", event.order_id)
        await asyncio.sleep(5)
        await message.nack(requeue=True)
        return

    await message.ack()


async def handle_stock_reserved(message: AbstractIncomingMessage) -> None:
    try:
        event = StockReserved.model_validate_json(message.body)
    except ValidationError:
        log.exception("Invalid StockReserved payload, dropping")
        await message.reject(requeue=False)
        return

    try:
        async with db_helper.session_factory() as session:
            payment = await PaymentService(PaymentRepository(session), provider).process(event)

        if payment.status == PaymentStatus.SUCCEEDED:
            await broker.publish(
                "payment.succeeded",
                PaymentSucceeded(
                    order_id=payment.order_id,
                    user_id=payment.user_id,
                    amount=payment.amount,
                ),
            )
        else:
            await broker.publish(
                "payment.failed",
                PaymentFailed(
                    order_id=payment.order_id,
                    user_id=payment.user_id,
                    reason=payment.failure_reason or "payment failed",
                ),
            )
    except Exception:
        log.exception("Failed to process StockReserved for %s, requeue", event.order_id)
        await asyncio.sleep(5)
        await message.nack(requeue=True)
        return

    await message.ack()


async def start_consumers(b: Broker) -> None:
    queue = await b.channel.declare_queue("payment.stock_reserved", durable=True)
    await queue.bind(b.exchange, routing_key="stock.reserved")
    await queue.consume(handle_stock_reserved)
    cancelled_queue = await b.channel.declare_queue("payment.order_cancelled", durable=True)
    await cancelled_queue.bind(b.exchange, routing_key="order.cancelled")
    await cancelled_queue.consume(handle_order_cancelled)
