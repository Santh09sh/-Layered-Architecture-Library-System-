"""
Reservation Service
Business logic for book reservations.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.data_access.reservation_repository import ReservationRepository
from app.data_access.book_repository import BookRepository
from app.data_access.book_copy_repository import BookCopyRepository
from app.data_access.notification_repository import NotificationRepository
from app.domain.entities.reservation import Reservation
from app.domain.entities.notification import Notification
from app.domain.enums import ReservationStatus, BookCopyStatus, NotificationType


class ReservationService:
    def __init__(self, db: Session):
        self.reservation_repo = ReservationRepository(db)
        self.book_repo = BookRepository(db)
        self.copy_repo = BookCopyRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.db = db

    def create_reservation(self, user_id: int, book_id: int) -> Reservation:
        """Create a reservation for a book. Only allowed when no copies are available."""
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found.")

        # Check if copies are available
        available = self.copy_repo.get_available_copies(book_id)
        if available:
            raise ValueError("Copies are available. Please borrow directly instead of reserving.")

        # Check if user already has an active reservation
        existing = self.reservation_repo.get_active_user_reservation_for_book(user_id, book_id)
        if existing:
            raise ValueError("You already have an active reservation for this book.")

        # Determine queue position
        active_reservations = self.reservation_repo.get_active_for_book(book_id)
        queue_position = len(active_reservations) + 1

        reservation = Reservation(
            user_id=user_id,
            book_id=book_id,
            status=ReservationStatus.PENDING,
            queue_position=queue_position,
        )

        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)

        # Notify
        notification = Notification(
            user_id=user_id,
            type=NotificationType.GENERAL,
            title="Reservation Created",
            message=f"You are #{queue_position} in the queue for '{book.title}'."
        )
        self.db.add(notification)
        self.db.commit()

        return reservation

    def cancel_reservation(self, reservation_id: int, user_id: int) -> Reservation:
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found.")
        if reservation.user_id != user_id:
            raise ValueError("You cannot cancel another user's reservation.")
        if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.READY]:
            raise ValueError("This reservation cannot be cancelled.")

        reservation.status = ReservationStatus.CANCELLED
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def get_user_reservations(self, user_id: int) -> List[Reservation]:
        return self.reservation_repo.get_user_reservations(user_id)

    def get_all_reservations(self, skip: int = 0, limit: int = 100) -> List[Reservation]:
        return self.reservation_repo.get_all_with_details(skip, limit)

    def count_pending(self) -> int:
        return self.reservation_repo.count_pending()
