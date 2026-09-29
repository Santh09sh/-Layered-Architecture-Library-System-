"""
Review Service
Business logic for book reviews.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.data_access.review_repository import ReviewRepository
from app.data_access.book_repository import BookRepository
from app.domain.entities.review import Review


class ReviewService:
    def __init__(self, db: Session):
        self.review_repo = ReviewRepository(db)
        self.book_repo = BookRepository(db)
        self.db = db

    def create_review(self, user_id: int, book_id: int, rating: float, review_text: Optional[str] = None) -> Review:
        if rating < 1.0 or rating > 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0.")

        # Check if user already reviewed this book
        existing = self.review_repo.get_user_review_for_book(user_id, book_id)
        if existing:
            raise ValueError("You have already reviewed this book.")

        review = Review(
            user_id=user_id,
            book_id=book_id,
            rating=rating,
            review_text=review_text,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        # Update book's average rating
        self._update_book_rating(book_id)

        return review

    def get_book_reviews(self, book_id: int, skip: int = 0, limit: int = 50) -> List[Review]:
        return self.review_repo.get_for_book(book_id, skip, limit)

    def _update_book_rating(self, book_id: int):
        avg = self.review_repo.get_average_rating(book_id)
        count = self.review_repo.get_rating_count(book_id)
        book = self.book_repo.get_by_id(book_id)
        if book:
            book.average_rating = avg
            book.total_ratings = count
            self.db.commit()
