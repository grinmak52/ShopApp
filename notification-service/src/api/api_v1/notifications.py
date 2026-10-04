import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import TokenUser, get_current_user
from database.orm.db_helper import db_helper
from repositories.notification import NotificationRepository
from schemas.notification import NotificationPage, NotificationRead, UnreadCount

router = APIRouter(prefix="/notifications", tags=["notifications"])

CurrentUser = Annotated[TokenUser, Depends(get_current_user)]
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]


@router.get("", response_model=NotificationPage)
async def list_notifications(
    user: CurrentUser,
    session: SessionDep,
    unread_only: bool = False,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = await NotificationRepository(session).list_for_user(
        user.id, unread_only, limit, offset
    )
    return NotificationPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/unread-count", response_model=UnreadCount)
async def unread_count(user: CurrentUser, session: SessionDep):
    return UnreadCount(unread=await NotificationRepository(session).unread_count(user.id))


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def read_all(user: CurrentUser, session: SessionDep):
    await NotificationRepository(session).mark_all_read(user.id)


@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def read_one(notification_id: uuid.UUID, user: CurrentUser, session: SessionDep):
    notification = await NotificationRepository(session).mark_read(notification_id, user.id)
    if notification is None:
        raise HTTPException(404, "Notification not found")
    return notification