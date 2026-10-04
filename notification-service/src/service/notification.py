import logging
import uuid

from sqlalchemy.exc import IntegrityError

from database.orm.models import Notification, NotificationType
from repositories.notification import NotificationRepository

log = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def create(
        self,
        user_id: uuid.UUID,
        order_id: uuid.UUID,
        type_: NotificationType,
        title: str,
        message: str,
    ) -> None:
        try:
            await self.repo.add(
                Notification(
                    user_id=user_id,
                    order_id=order_id,
                    type=type_,
                    title=title,
                    message=message,
                )
            )
        except IntegrityError:
            await self.repo.session.rollback()
            log.info("Duplicate notification %s for order %s, skipped", type_, order_id)