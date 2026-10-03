import uuid

from fastapi import APIRouter, status

from api.dependencies import CartServiceDep, CurrentUser
from schemas.cart import CartItemAdd, CartItemUpdate, CartRead

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartRead)
async def get_cart(user: CurrentUser, service: CartServiceDep):
    return await service.get(user.id)


@router.post("/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
async def add_item(data: CartItemAdd, user: CurrentUser, service: CartServiceDep):
    return await service.add_item(user.id, data.product_id, data.quantity)


@router.patch("/items/{product_id}", response_model=CartRead)
async def update_item(
    product_id: uuid.UUID, data: CartItemUpdate, user: CurrentUser, service: CartServiceDep
):
    return await service.set_quantity(user.id, product_id, data.quantity)


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(product_id: uuid.UUID, user: CurrentUser, service: CartServiceDep):
    await service.remove_item(user.id, product_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(user: CurrentUser, service: CartServiceDep):
    await service.clear(user.id)