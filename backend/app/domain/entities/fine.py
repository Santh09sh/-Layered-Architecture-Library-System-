"""
Fine Entity
Tracks fines generated from overdue books.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.domain.enums import FineStatus


class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrow_record_id = Column(Integer, ForeignKey("borrow_records.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    reason = Column(String(500), nullable=False)
    status = Column(SAEnum(FineStatus), nullable=False, default=FineStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    borrow_record = relationship("BorrowRecord", back_populates="fines")
    user = relationship("User", back_populates="fines")

    def __repr__(self):
        return f"<Fine(id={self.id}, amount={self.amount}, status={self.status})>"
