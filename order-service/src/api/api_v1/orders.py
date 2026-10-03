import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from api.dependencies import CurrentUser, OrderServiceDep
from schemas.order import OrderCreate, OrderPage, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, user: CurrentUser, service: OrderServiceDep):
    return await service.create(user, data)


@router.get("", response_model=OrderPage)
async def list_orders(
    user: CurrentUser,
    service: OrderServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = await service.list(user.id, limit, offset)
    return OrderPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: uuid.UUID, user: CurrentUser, service: OrderServiceDep):
    return await service.get(order_id, user.id)