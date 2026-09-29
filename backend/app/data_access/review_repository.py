"""
Review Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sql_func
from app.data_access.base_repository import BaseRepository
from app.domain.entities.review import Review


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def get_for_book(self, book_id: int, skip: int = 0, limit: int = 50) -> List[Review]:
        return (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.book_id == book_id)
            .order_by(Review.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_user_review_for_book(self, user_id: int, book_id: int) -> Optional[Review]:
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id, Review.book_id == book_id)
            .first()
        )

    def get_average_rating(self, book_id: int) -> float:
        result = (
            self.db.query(sql_func.avg(Review.rating))
            .filter(Review.book_id == book_id)
            .scalar()
        )
        return round(result, 2) if result else 0.0

    def get_rating_count(self, book_id: int) -> int:
        return self.db.query(Review).filter(Review.book_id == book_id).count()
