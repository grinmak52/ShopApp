import uuid
from datetime import datetime

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    created_at: datetime


class UserCreate(schemas.CreateUpdateDictModel):
    email: EmailStr
    password: str


class UserUpdate(schemas.CreateUpdateDictModel):
    email: EmailStr | None = None
    password: str | None = None