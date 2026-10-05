from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8002


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class AuthConfig(BaseModel):
    secret: str
    algorithm: str = "HS256"
    audience: str = "fastapi-users:auth"


class RedisConfig(BaseModel):
    url: str = "redis://localhost:6379/1"


class CatalogConfig(BaseModel):
    url: str = "http://localhost:8001"
    timeout: float = 3.0


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    auth: AuthConfig
    redis: RedisConfig = RedisConfig()
    catalog: CatalogConfig = CatalogConfig()


settings = Settings()