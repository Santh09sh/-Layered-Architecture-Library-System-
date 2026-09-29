"""
Review Entity
Tracks book reviews and ratings.
"""

from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 1.0 - 5.0
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_user_book_review"),
    )

    # Relationships
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, user={self.user_id}, book={self.book_id}, rating={self.rating})>"
