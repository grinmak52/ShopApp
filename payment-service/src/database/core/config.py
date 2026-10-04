from pydantic import BaseModel, Field
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8002


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 50

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class RabbitConfig(BaseModel):
    url: str = "amqp://guest:guest@localhost:5672/"
    exchange: str = "shop.events"
    prefetch_count: int = 10


class PaymentConfig(BaseModel):
    success_rate: float = Field(default=0.8, ge=0, le=1)
    delay_seconds: float = 0.5


class AuthConfig(BaseModel):
    secret: str
    algorithm: str = "HS256"
    audience: str = "fastapi-users:auth"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            ".env.template",
            ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    rabbit: RabbitConfig = RabbitConfig()
    payment: PaymentConfig = PaymentConfig()
    auth: AuthConfig


settings = Settings()
