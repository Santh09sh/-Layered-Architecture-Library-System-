"""
User Entity
Represents students, librarians, and administrators.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.domain.enums import UserRole, UserStatus


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    student_id = Column(String(50), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    status = Column(SAEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    borrow_records = relationship("BorrowRecord", back_populates="user", lazy="dynamic")
    reservations = relationship("Reservation", back_populates="user", lazy="dynamic")
    reviews = relationship("Review", back_populates="user", lazy="dynamic")
    fines = relationship("Fine", back_populates="user", lazy="dynamic")
    notifications = relationship("Notification", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role={self.role})>"
