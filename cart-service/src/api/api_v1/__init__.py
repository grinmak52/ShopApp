from fastapi import APIRouter

from core.config import settings

from .cart import router as cart_router

router = APIRouter(prefix=settings.api.v1.prefix)
router.include_router(cart_router)
