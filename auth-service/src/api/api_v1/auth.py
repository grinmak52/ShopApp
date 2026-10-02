from fastapi import APIRouter

from auth.backend import auth_backend
from auth.fastapi_users import fastapi_users
from schemas.user import UserCreate, UserRead, UserUpdate
from database.core.config import settings

router = APIRouter(prefix=settings.api.v1.auth, tags=['auth'])

router.include_router(
    router=fastapi_users.get_auth_router(auth_backend),
)
router.include_router(
    router=fastapi_users.get_register_router(
        UserRead, UserCreate
    ),
)
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead, UserUpdate
    ),
    prefix="/users",
)
