"""
Author Entity
Represents book authors.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.domain.entities.associations import book_authors


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    biography = Column(Text, nullable=True)
    nationality = Column(String(100), nullable=True)
    photo_url = Column(String(500), nullable=True)

    # Relationships
    books = relationship("Book", secondary=book_authors, back_populates="authors", lazy="selectin")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"
