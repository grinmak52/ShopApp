import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from database.orm.models import NotificationType


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationPage(BaseModel):
    items: list[NotificationRead]
    total: int
    limit: int
    offset: int


class UnreadCount(BaseModel):
    unread: int