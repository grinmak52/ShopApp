from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import generate_jwt

from database.core.config import settings


class RoleJWTStrategy(JWTStrategy):
    async def write_token(self, user) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "is_superuser": user.is_superuser,
        }
        return generate_jwt(
            data,
            self.encode_key,
            self.lifetime_seconds,
            algorithm=self.algorithm,
        )


def get_jwt_strategy() -> RoleJWTStrategy:
    return RoleJWTStrategy(
        secret=settings.auth.secret,
        lifetime_seconds=settings.auth.jwt_lifetime_seconds,
        algorithm=settings.auth.algorithm,
    )