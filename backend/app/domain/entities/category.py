"""
Category Entity
Represents book categories/genres.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    books = relationship("Book", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
