from fastapi import APIRouter

from auth.fastapi_users import fastapi_users
from schemas.user import UserCreate, UserRead, UserUpdate
from database.core.config import settings

router = APIRouter(prefix=settings.api.v1.users, tags=['Users'])

router.include_router(
    router=fastapi_users.get_users_router(
        UserRead, UserUpdate
    ),
)