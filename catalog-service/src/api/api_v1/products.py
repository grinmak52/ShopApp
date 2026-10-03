import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status, Depends

from api.dependencies import ProductServiceDep
from api.auth import require_admin
from schemas.product import (
    ProductCreate,
    ProductFilters,
    ProductPage,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductPage)
async def list_products(
    filters: Annotated[ProductFilters, Query()], service: ProductServiceDep
):
    return await service.list(filters)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: uuid.UUID, service: ProductServiceDep):
    return await service.get(product_id)


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
async def create_product(data: ProductCreate, service: ProductServiceDep):
    return await service.create(data)


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(require_admin)]
)
async def update_product(
        product_id: uuid.UUID, data: ProductUpdate, service: ProductServiceDep
):
    return await service.update(product_id, data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)]
)
async def delete_product(product_id: uuid.UUID, service: ProductServiceDep):
    await service.deactivate(product_id)
