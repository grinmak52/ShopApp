from fastapi import APIRouter

from database.core.config import settings

from .notifications import router as notifications_router


router = APIRouter(prefix=settings.api.v1.prefix)
router.include_router(notifications_router)
