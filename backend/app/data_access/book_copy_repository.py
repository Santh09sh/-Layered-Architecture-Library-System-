"""
BookCopy Repository
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.data_access.base_repository import BaseRepository
from app.domain.entities.book_copy import BookCopy
from app.domain.enums import BookCopyStatus


class BookCopyRepository(BaseRepository[BookCopy]):
    def __init__(self, db: Session):
        super().__init__(BookCopy, db)

    def get_by_accession(self, accession_number: str) -> Optional[BookCopy]:
        return self.db.query(BookCopy).filter(BookCopy.accession_number == accession_number).first()

    def get_by_barcode(self, barcode: str) -> Optional[BookCopy]:
        return self.db.query(BookCopy).filter(BookCopy.barcode == barcode).first()

    def get_available_copies(self, book_id: int) -> List[BookCopy]:
        return (
            self.db.query(BookCopy)
            .filter(BookCopy.book_id == book_id, BookCopy.status == BookCopyStatus.AVAILABLE)
            .all()
        )

    def get_copies_for_book(self, book_id: int) -> List[BookCopy]:
        return (
            self.db.query(BookCopy)
            .filter(BookCopy.book_id == book_id)
            .all()
        )

    def get_first_available(self, book_id: int) -> Optional[BookCopy]:
        return (
            self.db.query(BookCopy)
            .filter(BookCopy.book_id == book_id, BookCopy.status == BookCopyStatus.AVAILABLE)
            .first()
        )

    def count_by_status(self, status: BookCopyStatus) -> int:
        return self.db.query(BookCopy).filter(BookCopy.status == status).count()

    def get_all_with_book(self, skip: int = 0, limit: int = 100) -> List[BookCopy]:
        return (
            self.db.query(BookCopy)
            .options(joinedload(BookCopy.book))
            .offset(skip).limit(limit).all()
        )
