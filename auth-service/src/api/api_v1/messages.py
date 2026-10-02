from typing import Annotated
from fastapi import APIRouter, Depends

from auth.fastapi_users import current_active_user, current_superuser
from database.core.config import settings
from database.orm.models import User
from schemas.user import UserRead

router = APIRouter(
    prefix=settings.api.v1.messages,
    tags=["Messages"]
)


@router.get("")
def get_user_messages(
    user: Annotated[
        User,
        Depends(current_active_user)
    ],
):
    return {
        "messages": [],
        "user": UserRead.model_validate(user)
    }


@router.get("/secrets")
def get_superuser_messages(
    user: Annotated[
        User,
        Depends(current_superuser)
    ],
):
    return {
        "messages": ['secret'],
        "user": UserRead.model_validate(user)
    }