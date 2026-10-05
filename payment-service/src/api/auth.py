import uuid
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class TokenUser:
    id: uuid.UUID
    is_superuser: bool
    token: str


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> TokenUser:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.auth.secret,
            algorithms=[settings.auth.algorithm],
            audience=settings.auth.audience,
            options={"require": ["exp", "sub"]},
        )
        return TokenUser(
            id=uuid.UUID(payload["sub"]),
            is_superuser=bool(payload.get("is_superuser", False)),
            token=credentials.credentials,
        )
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

