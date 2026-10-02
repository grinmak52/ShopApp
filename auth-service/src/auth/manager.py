import logging
import uuid
from typing import Annotated, AsyncGenerator, Optional, TYPE_CHECKING

from fastapi import Depends
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin

from auth.dependencies import get_user_db
from database.core.config import settings
from database.orm.models import User

if TYPE_CHECKING:
    from fastapi import Request
    from fastapi_users.db import SQLAlchemyUserDatabase

log = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.auth.reset_password_token_secret
    verification_token_secret = settings.auth.verification_token_secret

    async def validate_password(
            self,
            password: str,
            user,
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Пароль должен быть не короче 8 символов"
            )
        if len(password) > 128:
            raise InvalidPasswordException(reason="Пароль слишком длинный")
        if not any(c.isdigit() for c in password):
            raise InvalidPasswordException(reason="Пароль должен содержать цифру")
        if not any(c.isalpha() for c in password):
            raise InvalidPasswordException(reason="Пароль должен содержать букву")
        email = getattr(user, "email", None)
        if email and email.split("@")[0].lower() in password.lower():
            raise InvalidPasswordException(reason="Пароль не должен содержать email")

    async def on_after_register(
            self,
            user: User,
            request: Optional["Request"] = None,
    ):
        log.info("User %s registered", user.id)

    async def on_after_forgot_password(
            self,
            user: User,
            token: str,
            request: Optional["Request"] = None,
    ):
        log.info("User %s forgot password", user.id)

    async def on_after_request_verify(
            self,
            user: User,
            token: str,
            request: Optional["Request"] = None,
    ):
        log.info("Verification requested for %s", user.id)


async def get_user_manager(
        user_db: Annotated[
            "SQLAlchemyUserDatabase",
            Depends(get_user_db),
        ],
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)
