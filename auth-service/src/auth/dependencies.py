from typing import Annotated

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.db_helper import db_helper
from database.orm.models import User


async def get_user_db(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    yield SQLAlchemyUserDatabase(session, User)