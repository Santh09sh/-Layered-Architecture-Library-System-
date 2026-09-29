"""
Pydantic Schemas for Borrowing, Reservations, Fines, Reviews, Notifications
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# --- Borrow ---
class BorrowRequest(BaseModel):
    book_copy_id: int


class BorrowResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    book_copy_id: int
    book_title: Optional[str] = None
    book_isbn: Optional[str] = None
    borrowed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    status: str
    renewal_count: int = 0

    class Config:
        from_attributes = True


class ReturnResponse(BaseModel):
    record_id: int
    fine: Optional[dict] = None


# --- Reservation ---
class ReservationRequest(BaseModel):
    book_id: int


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: Optional[str] = None
    reserved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str
    queue_position: int = 1

    class Config:
        from_attributes = True


# --- Fine ---
class FineResponse(BaseModel):
    id: int
    borrow_record_id: int
    user_id: int
    amount: float
    reason: str
    status: str
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Review ---
class ReviewCreate(BaseModel):
    book_id: int
    rating: float = Field(..., ge=1.0, le=5.0)
    review_text: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    book_id: int
    rating: float
    review_text: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Notification ---
class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Agent ---
class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_history: Optional[List[dict]] = []


class AgentChatResponse(BaseModel):
    response: str
    tool_calls: List[dict] = []
    reasoning_steps: List[dict] = []


# --- Analytics ---
class AnalyticsOverview(BaseModel):
    total_books: int = 0
    total_copies: int = 0
    available_copies: int = 0
    active_members: int = 0
    total_students: int = 0
    books_borrowed: int = 0
    overdue_books: int = 0
    pending_reservations: int = 0
    total_fines_collected: float = 0.0
    total_fines_pending: float = 0.0


# --- Generic ---
class APIResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict = {"code": "UNKNOWN", "message": "An error occurred."}
