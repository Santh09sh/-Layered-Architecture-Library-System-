"""
BorrowRecord Entity
Tracks book borrowing transactions.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.domain.enums import BorrowStatus


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=False, index=True)
    borrowed_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SAEnum(BorrowStatus), nullable=False, default=BorrowStatus.ACTIVE, index=True)
    renewal_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="borrow_records")
    book_copy = relationship("BookCopy", back_populates="borrow_records")
    fines = relationship("Fine", back_populates="borrow_record", lazy="selectin")

    def __repr__(self):
        return f"<BorrowRecord(id={self.id}, user={self.user_id}, copy={self.book_copy_id}, status={self.status})>"
