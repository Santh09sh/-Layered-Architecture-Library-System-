"""
BookCopy Entity
Represents a physical copy of a book.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.domain.enums import BookCopyStatus, BookCondition


class BookCopy(Base):
    __tablename__ = "book_copies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    accession_number = Column(String(50), unique=True, nullable=False, index=True)
    barcode = Column(String(100), unique=True, nullable=True)
    status = Column(SAEnum(BookCopyStatus), nullable=False, default=BookCopyStatus.AVAILABLE, index=True)
    location = Column(String(255), nullable=True)
    condition = Column(SAEnum(BookCondition), nullable=False, default=BookCondition.GOOD)

    # Relationships
    book = relationship("Book", back_populates="copies")
    borrow_records = relationship("BorrowRecord", back_populates="book_copy", lazy="dynamic")

    def __repr__(self):
        return f"<BookCopy(id={self.id}, accession='{self.accession_number}', status={self.status})>"
