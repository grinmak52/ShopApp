from fastapi import APIRouter

from database.core.config import settings

from .inventory import router as inventory_router


router = APIRouter(prefix=settings.api.v1.prefix)
router.include_router(inventory_router)
