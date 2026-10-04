from fastapi import APIRouter

from database.core.config import settings

from .payments import router as payments_router


router = APIRouter(prefix=settings.api.v1.prefix)
router.include_router(payments_router)
