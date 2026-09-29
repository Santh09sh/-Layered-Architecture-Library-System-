"""
Notification Service
Business logic for user notifications.
"""

from typing import List
from sqlalchemy.orm import Session

from app.data_access.notification_repository import NotificationRepository
from app.domain.entities.notification import Notification
from app.domain.enums import NotificationType


class NotificationService:
    def __init__(self, db: Session):
        self.notification_repo = NotificationRepository(db)
        self.db = db

    def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
        return self.notification_repo.get_for_user(user_id, skip, limit)

    def get_unread(self, user_id: int) -> List[Notification]:
        return self.notification_repo.get_unread_for_user(user_id)

    def count_unread(self, user_id: int) -> int:
        return self.notification_repo.count_unread(user_id)

    def mark_read(self, notification_id: int, user_id: int) -> Notification:
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ValueError("Notification not found.")
        if notification.user_id != user_id:
            raise ValueError("Access denied.")
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_read(self, user_id: int) -> None:
        self.notification_repo.mark_all_read(user_id)

    def create_notification(self, user_id: int, ntype: NotificationType,
                            title: str, message: str) -> Notification:
        notification = Notification(
            user_id=user_id, type=ntype, title=title, message=message
        )
        return self.notification_repo.create(notification)
