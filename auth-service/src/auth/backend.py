from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend

from database.core.config import settings

bearer_transport = BearerTransport(
    tokenUrl=f"{settings.api.prefix}{settings.api.v1.prefix}/auth/jwt/login".lstrip("/")
)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth.secret,
        lifetime_seconds=settings.auth.jwt_lifetime_seconds,
        algorithm=settings.auth.algorithm,
    )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)