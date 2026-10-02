from fastapi_users.authentication import JWTStrategy

from database.core.config import settings


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth.secret,
        lifetime_seconds=settings.auth.jwt_lifetime_seconds,
        algorithm=settings.auth.algorithm,
    )
