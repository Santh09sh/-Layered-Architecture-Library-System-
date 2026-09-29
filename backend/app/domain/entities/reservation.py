"""
Reservation Entity
Tracks book reservations when all copies are unavailable.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.domain.enums import ReservationStatus


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    reserved_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SAEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING, index=True)
    queue_position = Column(Integer, default=1)

    # Relationships
    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation(id={self.id}, user={self.user_id}, book={self.book_id}, status={self.status})>"
