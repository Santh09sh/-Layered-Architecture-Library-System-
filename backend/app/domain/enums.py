"""
Domain Enumerations
All enum types used across the domain layer.
"""

import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    LIBRARIAN = "LIBRARIAN"
    STUDENT = "STUDENT"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"


class BookCopyStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"
    LOST = "LOST"
    DAMAGED = "DAMAGED"
    MAINTENANCE = "MAINTENANCE"


class BorrowStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    LOST = "LOST"


class ReservationStatus(str, enum.Enum):
    PENDING = "PENDING"
    READY = "READY"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class FineStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    WAIVED = "WAIVED"


class NotificationType(str, enum.Enum):
    BORROW_CONFIRMATION = "BORROW_CONFIRMATION"
    RETURN_REMINDER = "RETURN_REMINDER"
    OVERDUE_NOTICE = "OVERDUE_NOTICE"
    RESERVATION_READY = "RESERVATION_READY"
    RESERVATION_EXPIRED = "RESERVATION_EXPIRED"
    FINE_NOTICE = "FINE_NOTICE"
    GENERAL = "GENERAL"


class BookCondition(str, enum.Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    DAMAGED = "DAMAGED"
