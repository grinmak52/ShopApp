from typing import Annotated

from fastapi import Depends

from api.auth import TokenUser, get_current_user
from cache.redis import redis_client
from clients.catalog import catalog_client
from repositories.cart import CartRepository
from service.cart import CartService

CurrentUser = Annotated[TokenUser, Depends(get_current_user)]


def get_cart_service() -> CartService:
    return CartService(CartRepository(redis_client), catalog_client)


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]