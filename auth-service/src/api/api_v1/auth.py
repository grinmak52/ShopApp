from fastapi import APIRouter

from auth.backend import auth_backend
from auth.fastapi_users import fastapi_users
from schemas.user import UserCreate, UserRead, UserUpdate
from database.core.config import settings

router = APIRouter(prefix=settings.api.v1.auth, tags=['Auth'])

# /logim
# /logout

router.include_router(
    router=fastapi_users.get_auth_router(auth_backend),
)

# /register

router.include_router(
    router=fastapi_users.get_register_router(
        UserRead, UserCreate
    ),
)

# /request-verify-token
# /verify

router.include_router(
    router=fastapi_users.get_verify_router(UserRead),
)

# /forgot-password
# /reset-password

router.include_router(
    router=fastapi_users.get_reset_password_router(),
)