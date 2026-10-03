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
        )
        return TokenUser(
            id=uuid.UUID(payload["sub"]),
            is_superuser=bool(payload.get("is_superuser", False)),
        )
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


def require_admin(user: Annotated[TokenUser, Depends(get_current_user)]) -> TokenUser:
    if not user.is_superuser:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user