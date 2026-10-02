from fastapi_users.authentication import BearerTransport

from database.core.config import settings

bearer_transport = BearerTransport(
    tokenUrl=f"{settings.api.prefix}{settings.api.v1.prefix}/auth/jwt/login".lstrip("/")
)
