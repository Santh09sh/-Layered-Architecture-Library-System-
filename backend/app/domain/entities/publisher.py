"""
Publisher Entity
Represents book publishers.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    website = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)

    # Relationships
    books = relationship("Book", back_populates="publisher", lazy="dynamic")

    def __repr__(self):
        return f"<Publisher(id={self.id}, name='{self.name}')>"
