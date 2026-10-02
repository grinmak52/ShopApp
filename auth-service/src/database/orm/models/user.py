from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from database.orm.base import Base
from database.orm.mixins.time_mixin import TimestampMixin


class User(Base, SQLAlchemyBaseUserTableUUID, TimestampMixin):
    pass