"""
Analytics Service
Aggregated analytics and statistics for dashboards.
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func

from app.data_access.book_repository import BookRepository
from app.data_access.book_copy_repository import BookCopyRepository
from app.data_access.borrow_repository import BorrowRepository
from app.data_access.user_repository import UserRepository
from app.data_access.fine_repository import FineRepository
from app.data_access.reservation_repository import ReservationRepository
from app.data_access.review_repository import ReviewRepository
from app.domain.entities.borrow_record import BorrowRecord
from app.domain.entities.book_copy import BookCopy
from app.domain.entities.book import Book
from app.domain.entities.category import Category
from app.domain.enums import UserRole, BookCopyStatus


class AnalyticsService:
    def __init__(self, db: Session):
        self.book_repo = BookRepository(db)
        self.copy_repo = BookCopyRepository(db)
        self.borrow_repo = BorrowRepository(db)
        self.user_repo = UserRepository(db)
        self.fine_repo = FineRepository(db)
        self.reservation_repo = ReservationRepository(db)
        self.db = db

    def get_overview(self) -> Dict:
        """Get high-level library statistics for admin dashboard."""
        return {
            "total_books": self.book_repo.count(),
            "total_copies": self.copy_repo.count(),
            "available_copies": self.copy_repo.count_by_status(BookCopyStatus.AVAILABLE),
            "active_members": self.user_repo.count_active(),
            "total_students": self.user_repo.count_by_role(UserRole.STUDENT),
            "books_borrowed": self.borrow_repo.count_active_total(),
            "overdue_books": self.borrow_repo.count_overdue_total(),
            "pending_reservations": self.reservation_repo.count_pending(),
            "total_fines_collected": self.fine_repo.get_total_collected(),
            "total_fines_pending": self.fine_repo.get_total_pending(),
        }

    def get_borrowing_trends(self, months: int = 6) -> List[Dict]:
        """Borrowing count by month."""
        return self.borrow_repo.get_borrows_by_month(months)

    def get_popular_categories(self, limit: int = 8) -> List[Dict]:
        """Most borrowed categories."""
        results = (
            self.db.query(
                Category.name,
                sql_func.count(BorrowRecord.id).label("borrow_count")
            )
            .join(Book, Book.category_id == Category.id)
            .join(BookCopy, BookCopy.book_id == Book.id)
            .join(BorrowRecord, BorrowRecord.book_copy_id == BookCopy.id)
            .group_by(Category.name)
            .order_by(sql_func.count(BorrowRecord.id).desc())
            .limit(limit)
            .all()
        )
        return [{"category": name, "count": count} for name, count in results]

    def get_most_borrowed_books(self, limit: int = 10) -> List[Dict]:
        return self.book_repo.get_most_borrowed(limit)

    def get_library_statistics(self) -> Dict:
        """Comprehensive library stats for the AI agent."""
        overview = self.get_overview()
        overview["borrowing_trends"] = self.get_borrowing_trends()
        overview["popular_categories"] = self.get_popular_categories()
        return overview
