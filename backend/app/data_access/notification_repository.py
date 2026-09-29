"""
Notification Repository
"""

from typing import List
from sqlalchemy.orm import Session
from app.data_access.base_repository import BaseRepository
from app.domain.entities.notification import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def get_for_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_unread_for_user(self, user_id: int) -> List[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .order_by(Notification.created_at.desc())
            .all()
        )

    def count_unread(self, user_id: int) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .count()
        )

    def mark_all_read(self, user_id: int) -> None:
        self.db.query(Notification).filter(
            Notification.user_id == user_id, Notification.is_read == False  # noqa: E712
        ).update({"is_read": True})
        self.db.commit()
