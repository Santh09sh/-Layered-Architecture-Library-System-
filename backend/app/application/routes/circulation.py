"""
Circulation Routes
Borrowing, returning, renewing, reservations, fines.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.business.borrowing_service import BorrowingService
from app.business.reservation_service import ReservationService
from app.business.fine_service import FineService
from app.business.review_service import ReviewService
from app.business.notification_service import NotificationService
from app.application.schemas.common import (
    BorrowRequest, BorrowResponse, ReturnResponse,
    ReservationRequest, ReservationResponse,
    FineResponse, ReviewCreate, ReviewResponse,
    NotificationResponse,
)
from app.application.dependencies import get_current_user, require_librarian
from app.domain.entities.user import User

router = APIRouter(prefix="/api", tags=["Circulation"])


def _borrow_to_response(record) -> BorrowResponse:
    return BorrowResponse(
        id=record.id, user_id=record.user_id,
        user_name=record.user.name if hasattr(record, 'user') and record.user else None,
        book_copy_id=record.book_copy_id,
        book_title=record.book_copy.book.title if record.book_copy and record.book_copy.book else None,
        book_isbn=record.book_copy.book.isbn if record.book_copy and record.book_copy.book else None,
        borrowed_at=record.borrowed_at, due_date=record.due_date,
        returned_at=record.returned_at, status=record.status.value,
        renewal_count=record.renewal_count,
    )


# --- Borrowing ---

@router.post("/borrow", response_model=BorrowResponse, status_code=201)
async def borrow_book(
    request: BorrowRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BorrowingService(db)
    try:
        record = service.borrow_book(current_user.id, request.book_copy_id)
        return _borrow_to_response(record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BORROW_ERROR", "message": str(e)})


@router.post("/borrow/{record_id}/return", response_model=ReturnResponse)
async def return_book(
    record_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BorrowingService(db)
    try:
        result = service.return_book(record_id)
        return ReturnResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "RETURN_ERROR", "message": str(e)})


@router.post("/borrow/{record_id}/renew", response_model=BorrowResponse)
async def renew_book(
    record_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BorrowingService(db)
    try:
        record = service.renew_book(record_id)
        return _borrow_to_response(record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "RENEW_ERROR", "message": str(e)})


@router.get("/borrow/my", response_model=List[BorrowResponse])
async def my_borrows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BorrowingService(db)
    records = service.get_active_borrows(current_user.id)
    return [_borrow_to_response(r) for r in records]


@router.get("/borrow/history", response_model=List[BorrowResponse])
async def borrow_history(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BorrowingService(db)
    records = service.get_user_history(current_user.id, skip, limit)
    return [_borrow_to_response(r) for r in records]


@router.get("/borrow/all", response_model=List[BorrowResponse])
async def all_borrows(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BorrowingService(db)
    records = service.get_all_borrows(skip, limit)
    return [_borrow_to_response(r) for r in records]


@router.get("/borrow/overdue", response_model=List[BorrowResponse])
async def overdue_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BorrowingService(db)
    records = service.get_overdue_records()
    return [_borrow_to_response(r) for r in records]


@router.get("/borrow/eligibility")
async def check_eligibility(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BorrowingService(db)
    return service.check_eligibility(current_user.id)


# --- Reservations ---

@router.post("/reservations", response_model=ReservationResponse, status_code=201)
async def create_reservation(
    request: ReservationRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReservationService(db)
    try:
        res = service.create_reservation(current_user.id, request.book_id)
        return ReservationResponse(
            id=res.id, user_id=res.user_id, book_id=res.book_id,
            book_title=res.book.title if res.book else None,
            reserved_at=res.reserved_at, expires_at=res.expires_at,
            status=res.status.value, queue_position=res.queue_position,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "RESERVATION_ERROR", "message": str(e)})


@router.get("/reservations/my", response_model=List[ReservationResponse])
async def my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReservationService(db)
    reservations = service.get_user_reservations(current_user.id)
    return [
        ReservationResponse(
            id=r.id, user_id=r.user_id, book_id=r.book_id,
            book_title=r.book.title if r.book else None,
            reserved_at=r.reserved_at, expires_at=r.expires_at,
            status=r.status.value, queue_position=r.queue_position,
        )
        for r in reservations
    ]


@router.delete("/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReservationService(db)
    try:
        service.cancel_reservation(reservation_id, current_user.id)
        return {"success": True, "message": "Reservation cancelled."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reservations/all", response_model=List[ReservationResponse])
async def all_reservations(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = ReservationService(db)
    reservations = service.get_all_reservations(skip, limit)
    return [
        ReservationResponse(
            id=r.id, user_id=r.user_id, book_id=r.book_id,
            book_title=r.book.title if r.book else None,
            reserved_at=r.reserved_at, expires_at=r.expires_at,
            status=r.status.value, queue_position=r.queue_position,
        )
        for r in reservations
    ]


# --- Fines ---

@router.get("/fines/my", response_model=List[FineResponse])
async def my_fines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FineService(db)
    fines = service.get_user_fines(current_user.id)
    return [FineResponse(
        id=f.id, borrow_record_id=f.borrow_record_id, user_id=f.user_id,
        amount=f.amount, reason=f.reason, status=f.status.value,
        created_at=f.created_at, paid_at=f.paid_at,
    ) for f in fines]


@router.post("/fines/{fine_id}/pay")
async def pay_fine(
    fine_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FineService(db)
    try:
        service.pay_fine(fine_id, current_user.id)
        return {"success": True, "message": "Fine paid successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/fines/all", response_model=List[FineResponse])
async def all_fines(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = FineService(db)
    fines = service.get_all_fines(skip, limit)
    return [FineResponse(
        id=f.id, borrow_record_id=f.borrow_record_id, user_id=f.user_id,
        amount=f.amount, reason=f.reason, status=f.status.value,
        created_at=f.created_at, paid_at=f.paid_at,
    ) for f in fines]


# --- Reviews ---

@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    request: ReviewCreate, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReviewService(db)
    try:
        review = service.create_review(current_user.id, request.book_id, request.rating, request.review_text)
        return ReviewResponse(
            id=review.id, user_id=review.user_id, user_name=current_user.name,
            book_id=review.book_id, rating=review.rating,
            review_text=review.review_text, created_at=review.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reviews/book/{book_id}", response_model=List[ReviewResponse])
async def book_reviews(book_id: int, db: Session = Depends(get_db)):
    service = ReviewService(db)
    reviews = service.get_book_reviews(book_id)
    return [ReviewResponse(
        id=r.id, user_id=r.user_id, user_name=r.user.name if r.user else None,
        book_id=r.book_id, rating=r.rating,
        review_text=r.review_text, created_at=r.created_at,
    ) for r in reviews]


# --- Notifications ---

@router.get("/notifications", response_model=List[NotificationResponse])
async def my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    notifications = service.get_user_notifications(current_user.id)
    return [NotificationResponse(
        id=n.id, type=n.type.value, title=n.title,
        message=n.message, is_read=n.is_read, created_at=n.created_at,
    ) for n in notifications]


@router.get("/notifications/unread-count")
async def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    return {"count": service.count_unread(current_user.id)}


@router.post("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    service.mark_read(notification_id, current_user.id)
    return {"success": True}


@router.post("/notifications/read-all")
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    service.mark_all_read(current_user.id)
    return {"success": True}
