import asyncio
import logging
import uuid
from decimal import Decimal

from clients.cart import CartClient
from clients.catalog import CatalogClient
from database.orm.models import Order, OrderItem, OrderStatus
from messaging.broker import Broker
from messaging.events import OrderCreated, OrderEventItem
from repositories.order import OrderRepository
from schemas.order import OrderCreate
from service.exceptions import BadRequestError, NotFoundError, ServiceUnavailableError

log = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        repo: OrderRepository,
        cart: CartClient,
        catalog: CatalogClient,
        broker: Broker,
    ):
        self.repo = repo
        self.cart = cart
        self.catalog = catalog
        self.broker = broker

    async def create(self, user, data: OrderCreate) -> Order:
        cart_items = await self.cart.get_items(user.token)
        if not cart_items:
            raise BadRequestError("Cart is empty")

        products = await asyncio.gather(
            *(self.catalog.get_product(i["product_id"]) for i in cart_items)
        )

        items: list[OrderItem] = []
        total = Decimal("0")
        for cart_item, product in zip(cart_items, products):
            if not product["is_active"]:
                raise BadRequestError(f"Product '{product['name']}' is not available")
            price = Decimal(str(product["price"]))
            qty = cart_item["quantity"]
            items.append(
                OrderItem(
                    product_id=uuid.UUID(cart_item["product_id"]),
                    product_name=product["name"],
                    price=price,
                    quantity=qty,
                )
            )
            total += price * qty

        order = await self.repo.create(
            Order(
                user_id=user.id,
                total_price=total,
                shipping_address=data.shipping_address,
                items=items,
            )
        )

        event = OrderCreated(
            order_id=order.id,
            user_id=order.user_id,
            total_price=order.total_price,
            items=[
                OrderEventItem(product_id=i.product_id, quantity=i.quantity)
                for i in order.items
            ],
        )
        try:
            await self.broker.publish("order.created", event)
        except Exception:
            log.exception("Failed to publish OrderCreated for %s", order.id)
            await self.repo.set_status(order, OrderStatus.CANCELLED)
            raise ServiceUnavailableError("Could not process the order, try again later")

        try:
            await self.cart.clear(user.token)
        except Exception:
            log.warning("Order %s created, but the cart was not cleared", order.id)

        return order

    async def get(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Order:
        order = await self.repo.get_for_user(order_id, user_id)
        if order is None:
            raise NotFoundError("Order")
        return order

    async def list(self, user_id: uuid.UUID, limit: int, offset: int):
        return await self.repo.list_for_user(user_id, limit, offset)