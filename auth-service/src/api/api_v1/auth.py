from fastapi import APIRouter

from auth.backend import auth_backend
from auth.fastapi_users import fastapi_users
from schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/auth")

router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/jwt", tags=["auth"])
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), tags=["auth"])
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])