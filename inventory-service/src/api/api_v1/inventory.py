import uuid

from fastapi import APIRouter, Depends, status

from api.auth import require_admin
from api.dependencies import InventoryServiceDep
from schemas.inventory import InventoryCreate, InventoryRead, InventoryUpdate

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{product_id}", response_model=InventoryRead)
async def get_inventory(product_id: uuid.UUID, service: InventoryServiceDep):
    return await service.get(product_id)


@router.post(
    "",
    response_model=InventoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_inventory(data: InventoryCreate, service: InventoryServiceDep):
    return await service.create(data.product_id, data.quantity)


@router.patch(
    "/{product_id}",
    response_model=InventoryRead,
    dependencies=[Depends(require_admin)],
)
async def update_inventory(
    product_id: uuid.UUID, data: InventoryUpdate, service: InventoryServiceDep
):
    return await service.set_quantity(product_id, data.quantity)