"""
Borrow Repository
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sql_func
from app.data_access.base_repository import BaseRepository
from app.domain.entities.borrow_record import BorrowRecord
from app.domain.entities.book_copy import BookCopy
from app.domain.enums import BorrowStatus


class BorrowRepository(BaseRepository[BorrowRecord]):
    def __init__(self, db: Session):
        super().__init__(BorrowRecord, db)

    def get_active_borrows_for_user(self, user_id: int) -> List[BorrowRecord]:
        return (
            self.db.query(BorrowRecord)
            .options(joinedload(BorrowRecord.book_copy).joinedload(BookCopy.book))
            .filter(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status.in_([BorrowStatus.ACTIVE, BorrowStatus.OVERDUE])
            )
            .all()
        )

    def count_active_borrows(self, user_id: int) -> int:
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status.in_([BorrowStatus.ACTIVE, BorrowStatus.OVERDUE])
            )
            .count()
        )

    def get_overdue_records(self) -> List[BorrowRecord]:
        now = datetime.utcnow()
        return (
            self.db.query(BorrowRecord)
            .options(
                joinedload(BorrowRecord.user),
                joinedload(BorrowRecord.book_copy).joinedload(BookCopy.book)
            )
            .filter(
                BorrowRecord.status == BorrowStatus.ACTIVE,
                BorrowRecord.due_date < now
            )
            .all()
        )

    def get_active_borrow_for_copy(self, book_copy_id: int) -> Optional[BorrowRecord]:
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.book_copy_id == book_copy_id,
                BorrowRecord.status.in_([BorrowStatus.ACTIVE, BorrowStatus.OVERDUE])
            )
            .first()
        )

    def get_user_history(self, user_id: int, skip: int = 0, limit: int = 50) -> List[BorrowRecord]:
        return (
            self.db.query(BorrowRecord)
            .options(joinedload(BorrowRecord.book_copy).joinedload(BookCopy.book))
            .filter(BorrowRecord.user_id == user_id)
            .order_by(BorrowRecord.borrowed_at.desc())
            .offset(skip).limit(limit).all()
        )

    def count_total_borrows(self) -> int:
        return self.db.query(BorrowRecord).count()

    def count_active_total(self) -> int:
        return (
            self.db.query(BorrowRecord)
            .filter(BorrowRecord.status.in_([BorrowStatus.ACTIVE, BorrowStatus.OVERDUE]))
            .count()
        )

    def count_overdue_total(self) -> int:
        now = datetime.utcnow()
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.status == BorrowStatus.ACTIVE,
                BorrowRecord.due_date < now
            )
            .count()
        )

    def get_borrows_by_month(self, months: int = 6) -> List[dict]:
        """Get borrowing stats grouped by month for the last N months."""
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=months * 30)
        results = (
            self.db.query(
                sql_func.strftime('%Y-%m', BorrowRecord.borrowed_at).label('month'),
                sql_func.count(BorrowRecord.id).label('count')
            )
            .filter(BorrowRecord.borrowed_at >= start_date)
            .group_by(sql_func.strftime('%Y-%m', BorrowRecord.borrowed_at))
            .order_by(sql_func.strftime('%Y-%m', BorrowRecord.borrowed_at))
            .all()
        )
        return [{"month": r.month, "count": r.count} for r in results]

    def get_all_with_details(self, skip: int = 0, limit: int = 100) -> List[BorrowRecord]:
        return (
            self.db.query(BorrowRecord)
            .options(
                joinedload(BorrowRecord.user),
                joinedload(BorrowRecord.book_copy).joinedload(BookCopy.book),
            )
            .order_by(BorrowRecord.borrowed_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_due_soon(self, user_id: int, days: int = 3) -> List[BorrowRecord]:
        from datetime import timedelta
        now = datetime.utcnow()
        soon = now + timedelta(days=days)
        return (
            self.db.query(BorrowRecord)
            .options(joinedload(BorrowRecord.book_copy).joinedload(BookCopy.book))
            .filter(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status == BorrowStatus.ACTIVE,
                BorrowRecord.due_date.between(now, soon)
            )
            .all()
        )
