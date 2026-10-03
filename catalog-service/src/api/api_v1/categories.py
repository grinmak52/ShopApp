import uuid

from fastapi import APIRouter, status, Depends

from api.dependencies import CategoryServiceDep
from api.auth import require_admin
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(service: CategoryServiceDep):
    return await service.list()


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: uuid.UUID, service: CategoryServiceDep):
    return await service.get(category_id)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
async def create_category(data: CategoryCreate, service: CategoryServiceDep):
    return await service.create(data)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_admin)]
)
async def update_category(
        category_id: uuid.UUID, data: CategoryUpdate, service: CategoryServiceDep
):
    return await service.update(category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)]
)
async def delete_category(category_id: uuid.UUID, service: CategoryServiceDep):
    await service.delete(category_id)
