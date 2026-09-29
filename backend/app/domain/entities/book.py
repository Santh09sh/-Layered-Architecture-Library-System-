"""
Book Entity
Represents a book title (not a physical copy).
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.domain.entities.associations import book_authors


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    isbn = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    language = Column(String(50), default="English")
    pages = Column(Integer, nullable=True)
    cover_image = Column(String(500), nullable=True)
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)

    # Foreign Keys
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    publisher = relationship("Publisher", back_populates="books", lazy="selectin")
    category = relationship("Category", back_populates="books", lazy="selectin")
    authors = relationship("Author", secondary=book_authors, back_populates="books", lazy="selectin")
    copies = relationship("BookCopy", back_populates="book", lazy="selectin")
    reviews = relationship("Review", back_populates="book", lazy="dynamic")
    reservations = relationship("Reservation", back_populates="book", lazy="dynamic")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"
