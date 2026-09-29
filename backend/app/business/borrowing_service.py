"""
Borrowing Service
Core business logic for borrowing, returning, and renewing books.
All business rules are enforced here — NOT in controllers.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.data_access.borrow_repository import BorrowRepository
from app.data_access.book_copy_repository import BookCopyRepository
from app.data_access.user_repository import UserRepository
from app.data_access.fine_repository import FineRepository
from app.data_access.reservation_repository import ReservationRepository
from app.domain.entities.borrow_record import BorrowRecord
from app.domain.entities.fine import Fine
from app.domain.entities.notification import Notification
from app.data_access.notification_repository import NotificationRepository
from app.domain.enums import (
    BorrowStatus, BookCopyStatus, UserStatus,
    FineStatus, ReservationStatus, NotificationType
)


class BorrowingService:
    def __init__(self, db: Session):
        self.borrow_repo = BorrowRepository(db)
        self.copy_repo = BookCopyRepository(db)
        self.user_repo = UserRepository(db)
        self.fine_repo = FineRepository(db)
        self.reservation_repo = ReservationRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.db = db

    def check_eligibility(self, user_id: int) -> dict:
        """Check if a user is eligible to borrow books. Returns eligibility status and reasons."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"eligible": False, "reasons": ["User not found."]}

        reasons = []

        # Rule 1: Account must be active
        if user.status != UserStatus.ACTIVE:
            reasons.append(f"Account is {user.status.value}. Please contact the librarian.")

        # Rule 2: Borrowing limit not exceeded
        active_count = self.borrow_repo.count_active_borrows(user_id)
        if active_count >= settings.MAX_BOOKS_PER_STUDENT:
            reasons.append(f"Borrowing limit reached ({active_count}/{settings.MAX_BOOKS_PER_STUDENT} books).")

        # Rule 3: No excessive unpaid fines
        total_fines = self.fine_repo.get_total_unpaid(user_id)
        if total_fines >= settings.MAX_FINE_THRESHOLD:
            reasons.append(f"Unpaid fines of ${total_fines:.2f} exceed the ${settings.MAX_FINE_THRESHOLD:.2f} threshold.")

        return {
            "eligible": len(reasons) == 0,
            "reasons": reasons,
            "active_borrows": active_count,
            "max_borrows": settings.MAX_BOOKS_PER_STUDENT,
            "unpaid_fines": total_fines,
        }

    def borrow_book(self, user_id: int, book_copy_id: int) -> BorrowRecord:
        """Borrow a book copy. Enforces all business rules."""
        # Check eligibility
        eligibility = self.check_eligibility(user_id)
        if not eligibility["eligible"]:
            raise ValueError("Cannot borrow: " + " ".join(eligibility["reasons"]))

        # Check book copy availability
        copy = self.copy_repo.get_by_id(book_copy_id)
        if not copy:
            raise ValueError("Book copy not found.")
        if copy.status != BookCopyStatus.AVAILABLE:
            raise ValueError(f"This copy is currently {copy.status.value}.")

        # Create borrow record
        due_date = datetime.utcnow() + timedelta(days=settings.LOAN_DURATION_DAYS)
        record = BorrowRecord(
            user_id=user_id,
            book_copy_id=book_copy_id,
            due_date=due_date,
            status=BorrowStatus.ACTIVE,
            renewal_count=0,
        )

        # Update copy status
        copy.status = BookCopyStatus.BORROWED

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        # Create notification
        self._notify(user_id, NotificationType.BORROW_CONFIRMATION,
                     "Book Borrowed",
                     f"You have borrowed a book. Due date: {due_date.strftime('%Y-%m-%d')}.")

        return record

    def return_book(self, borrow_record_id: int) -> dict:
        """Return a borrowed book. Auto-calculates fines if overdue."""
        record = self.borrow_repo.get_by_id(borrow_record_id)
        if not record:
            raise ValueError("Borrow record not found.")
        if record.status not in [BorrowStatus.ACTIVE, BorrowStatus.OVERDUE]:
            raise ValueError(f"Cannot return: record status is {record.status.value}.")

        now = datetime.utcnow()
        record.returned_at = now
        record.status = BorrowStatus.RETURNED

        # Update copy status
        copy = self.copy_repo.get_by_id(record.book_copy_id)
        copy.status = BookCopyStatus.AVAILABLE

        result = {"record_id": record.id, "fine": None}

        # Calculate fine if overdue
        if now > record.due_date:
            overdue_days = (now - record.due_date).days
            fine_amount = overdue_days * settings.FINE_PER_DAY
            fine = Fine(
                borrow_record_id=record.id,
                user_id=record.user_id,
                amount=fine_amount,
                reason=f"Overdue by {overdue_days} day(s) at ${settings.FINE_PER_DAY}/day",
                status=FineStatus.PENDING,
            )
            self.db.add(fine)
            result["fine"] = {"amount": fine_amount, "days_overdue": overdue_days}

            self._notify(record.user_id, NotificationType.FINE_NOTICE,
                         "Fine Generated",
                         f"A fine of ${fine_amount:.2f} has been generated for overdue return ({overdue_days} days).")

        self.db.commit()

        # Check if anyone is waiting for this book
        self._process_reservation_queue(copy.book_id)

        return result

    def renew_book(self, borrow_record_id: int) -> BorrowRecord:
        """Renew a borrowed book. Enforces renewal limits and reservation checks."""
        record = self.borrow_repo.get_by_id(borrow_record_id)
        if not record:
            raise ValueError("Borrow record not found.")
        if record.status != BorrowStatus.ACTIVE:
            raise ValueError(f"Cannot renew: record status is {record.status.value}.")

        # Rule: Renewal limit
        if record.renewal_count >= settings.MAX_RENEWALS:
            raise ValueError(f"Maximum renewal limit ({settings.MAX_RENEWALS}) reached.")

        # Rule: No reservation exists for this book
        copy = self.copy_repo.get_by_id(record.book_copy_id)
        if self.reservation_repo.has_active_reservation(copy.book_id):
            raise ValueError("Cannot renew: another user has reserved this book.")

        # Rule: No excessive fines
        total_fines = self.fine_repo.get_total_unpaid(record.user_id)
        if total_fines >= settings.MAX_FINE_THRESHOLD:
            raise ValueError(f"Cannot renew: unpaid fines (${total_fines:.2f}) exceed threshold.")

        # Extend due date
        record.due_date = datetime.utcnow() + timedelta(days=settings.LOAN_DURATION_DAYS)
        record.renewal_count += 1

        self.db.commit()
        self.db.refresh(record)
        return record

    def get_active_borrows(self, user_id: int) -> List[BorrowRecord]:
        return self.borrow_repo.get_active_borrows_for_user(user_id)

    def get_user_history(self, user_id: int, skip: int = 0, limit: int = 50) -> List[BorrowRecord]:
        return self.borrow_repo.get_user_history(user_id, skip, limit)

    def get_all_borrows(self, skip: int = 0, limit: int = 100) -> List[BorrowRecord]:
        return self.borrow_repo.get_all_with_details(skip, limit)

    def get_overdue_records(self) -> List[BorrowRecord]:
        return self.borrow_repo.get_overdue_records()

    def get_due_soon(self, user_id: int, days: int = 3) -> List[BorrowRecord]:
        return self.borrow_repo.get_due_soon(user_id, days)

    # --- Statistics ---

    def count_active_borrows(self) -> int:
        return self.borrow_repo.count_active_total()

    def count_overdue(self) -> int:
        return self.borrow_repo.count_overdue_total()

    def get_borrowing_trends(self, months: int = 6) -> List[dict]:
        return self.borrow_repo.get_borrows_by_month(months)

    # --- Internal helpers ---

    def _process_reservation_queue(self, book_id: int):
        """When a copy becomes available, notify the next person in the reservation queue."""
        next_reservation = self.reservation_repo.get_next_in_queue(book_id)
        if next_reservation:
            next_reservation.status = ReservationStatus.READY
            next_reservation.expires_at = datetime.utcnow() + timedelta(hours=settings.RESERVATION_EXPIRY_HOURS)
            self.db.commit()
            self._notify(
                next_reservation.user_id, NotificationType.RESERVATION_READY,
                "Reservation Ready",
                f"A book you reserved is now available! Pick it up within {settings.RESERVATION_EXPIRY_HOURS} hours."
            )

    def _notify(self, user_id: int, ntype: NotificationType, title: str, message: str):
        notification = Notification(
            user_id=user_id, type=ntype, title=title, message=message
        )
        self.db.add(notification)
