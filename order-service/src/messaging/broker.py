import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from pydantic import BaseModel

from database.core.config import settings


class Broker:
    def __init__(self):
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None
        self.exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        cfg = settings.rabbit
        self.connection = await aio_pika.connect_robust(cfg.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=cfg.prefetch_count)
        self.exchange = await self.channel.declare_exchange(
            cfg.exchange, ExchangeType.TOPIC, durable=True
        )

    async def publish(self, routing_key: str, event: BaseModel) -> None:
        message = Message(
            body=event.model_dump_json().encode(),
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
            message_id=str(event.event_id),
        )
        await self.exchange.publish(message, routing_key=routing_key)

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()


broker = Broker()