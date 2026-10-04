import asyncio
import logging
from dataclasses import dataclass
from typing import Callable

from aio_pika.abc import AbstractIncomingMessage
from pydantic import BaseModel, ValidationError

from database.orm.db_helper import db_helper
from database.orm.models import NotificationType
from messaging import events
from messaging.broker import Broker
from repositories.notification import NotificationRepository
from service.notification import NotificationService

log = logging.getLogger(__name__)


@dataclass
class Rule:
    routing_key: str
    model: type[BaseModel]
    type_: NotificationType
    title: str
    message: Callable[[BaseModel], str]


RULES = [
    Rule("order.created", events.OrderCreated, NotificationType.ORDER_CREATED,
         "Заказ оформлен",
         lambda e: f"Ваш заказ на сумму {e.total_price} принят в обработку."),
    Rule("order.confirmed", events.OrderConfirmed, NotificationType.ORDER_CONFIRMED,
         "Заказ подтверждён",
         lambda e: "Оплата прошла, заказ подтверждён."),
    Rule("order.cancelled", events.OrderCancelled, NotificationType.ORDER_CANCELLED,
         "Заказ отменён",
         lambda e: f"Заказ отменён. Причина: {e.reason}."),
    Rule("payment.succeeded", events.PaymentSucceeded, NotificationType.PAYMENT_SUCCEEDED,
         "Оплата прошла",
         lambda e: f"Списано {e.amount}."),
    Rule("payment.failed", events.PaymentFailed, NotificationType.PAYMENT_FAILED,
         "Оплата не прошла",
         lambda e: f"Не удалось провести платёж: {e.reason}."),
]


def make_handler(rule: Rule):
    async def handler(message: AbstractIncomingMessage) -> None:
        try:
            event = rule.model.model_validate_json(message.body)
        except ValidationError:
            log.exception("Invalid %s payload, dropping", rule.routing_key)
            await message.reject(requeue=False)
            return

        try:
            async with db_helper.session_factory() as session:
                await NotificationService(NotificationRepository(session)).create(
                    user_id=event.user_id,
                    order_id=event.order_id,
                    type_=rule.type_,
                    title=rule.title,
                    message=rule.message(event),
                )
        except Exception:
            log.exception("Failed to save notification for %s, requeue", rule.routing_key)
            await asyncio.sleep(5)
            await message.nack(requeue=True)
            return

        await message.ack()

    return handler


async def start_consumers(b: Broker) -> None:
    for rule in RULES:
        queue = await b.channel.declare_queue(
            f"notification.{rule.routing_key}", durable=True
        )
        await queue.bind(b.exchange, routing_key=rule.routing_key)
        await queue.consume(make_handler(rule))