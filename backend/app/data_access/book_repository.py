"""
Book Repository
Data access operations for Book entity.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sql_func
from app.data_access.base_repository import BaseRepository
from app.domain.entities.book import Book
from app.domain.entities.book_copy import BookCopy
from app.domain.enums import BookCopyStatus


class BookRepository(BaseRepository[Book]):
    def __init__(self, db: Session):
        super().__init__(Book, db)

    def get_by_id_with_relations(self, book_id: int) -> Optional[Book]:
        return (
            self.db.query(Book)
            .options(
                joinedload(Book.authors),
                joinedload(Book.publisher),
                joinedload(Book.category),
                joinedload(Book.copies),
            )
            .filter(Book.id == book_id)
            .first()
        )

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def search(self, query: str, category_id: Optional[int] = None,
               author_id: Optional[int] = None, available_only: bool = False,
               skip: int = 0, limit: int = 50) -> List[Book]:
        q = self.db.query(Book).options(
            joinedload(Book.authors),
            joinedload(Book.publisher),
            joinedload(Book.category),
            joinedload(Book.copies),
        )

        if query:
            # Split query into words and match any word
            from sqlalchemy import or_
            words = [w.strip() for w in query.split() if len(w.strip()) > 2]
            if words:
                word_filters = []
                for word in words:
                    term = f"%{word}%"
                    word_filters.append(Book.title.ilike(term))
                    word_filters.append(Book.isbn.ilike(term))
                    word_filters.append(Book.description.ilike(term))
                q = q.filter(or_(*word_filters))


        if category_id:
            q = q.filter(Book.category_id == category_id)

        if author_id:
            q = q.filter(Book.authors.any(id=author_id))

        results = q.offset(skip).limit(limit).all()

        if available_only:
            results = [
                book for book in results
                if any(c.status == BookCopyStatus.AVAILABLE for c in book.copies)
            ]

        return results

    def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[Book]:
        return (
            self.db.query(Book)
            .options(
                joinedload(Book.authors),
                joinedload(Book.publisher),
                joinedload(Book.category),
                joinedload(Book.copies),
            )
            .offset(skip).limit(limit).all()
        )

    def get_available_copy_count(self, book_id: int) -> int:
        return (
            self.db.query(BookCopy)
            .filter(BookCopy.book_id == book_id, BookCopy.status == BookCopyStatus.AVAILABLE)
            .count()
        )

    def get_most_borrowed(self, limit: int = 10) -> List[dict]:
        """Get most borrowed books based on borrow record count."""
        from app.domain.entities.borrow_record import BorrowRecord
        results = (
            self.db.query(
                Book,
                sql_func.count(BorrowRecord.id).label("borrow_count")
            )
            .join(BookCopy, BookCopy.book_id == Book.id)
            .join(BorrowRecord, BorrowRecord.book_copy_id == BookCopy.id)
            .group_by(Book.id)
            .order_by(sql_func.count(BorrowRecord.id).desc())
            .limit(limit)
            .all()
        )
        return [{"book": book, "borrow_count": count} for book, count in results]

    def get_by_category(self, category_id: int, skip: int = 0, limit: int = 50) -> List[Book]:
        return (
            self.db.query(Book)
            .options(joinedload(Book.authors), joinedload(Book.copies))
            .filter(Book.category_id == category_id)
            .offset(skip).limit(limit).all()
        )
