from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.db_helper import db_helper
from repositories.inventory import InventoryRepository
from service.inventory import InventoryService

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]


def get_inventory_service(session: SessionDep) -> InventoryService:
    return InventoryService(InventoryRepository(session))


InventoryServiceDep = Annotated[InventoryService, Depends(get_inventory_service)]