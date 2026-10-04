from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import TokenUser, get_current_user
from clients.cart import cart_client
from clients.catalog import catalog_client
from database.orm.db_helper import db_helper
from messaging.broker import broker
from repositories.order import OrderRepository
from service.order import OrderService

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]
CurrentUser = Annotated[TokenUser, Depends(get_current_user)]


def get_order_service(session: SessionDep) -> OrderService:
    return OrderService(OrderRepository(session), cart_client, catalog_client, broker)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]