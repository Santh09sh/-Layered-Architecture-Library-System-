"""
Analytics & User Management Routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.business.analytics_service import AnalyticsService
from app.business.user_service import UserService
from app.application.schemas.auth import UserResponse
from app.application.schemas.common import AnalyticsOverview
from app.application.dependencies import get_current_user, require_librarian, require_admin
from app.domain.entities.user import User
from app.domain.enums import UserRole

router = APIRouter(prefix="/api", tags=["Analytics & Admin"])


# --- Analytics ---

@router.get("/analytics/overview", response_model=AnalyticsOverview)
async def analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = AnalyticsService(db)
    return service.get_overview()


@router.get("/analytics/borrowing-trends")
async def borrowing_trends(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = AnalyticsService(db)
    return {"trends": service.get_borrowing_trends(months)}


@router.get("/analytics/popular-categories")
async def popular_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = AnalyticsService(db)
    return {"categories": service.get_popular_categories()}


@router.get("/analytics/most-borrowed")
async def most_borrowed(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = AnalyticsService(db)
    results = service.get_most_borrowed_books(limit)
    return {
        "books": [
            {
                "id": r["book"].id,
                "title": r["book"].title,
                "borrow_count": r["borrow_count"],
            }
            for r in results
        ]
    }


# --- User Management (Admin) ---

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: str = None,
    q: str = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = UserService(db)
    if q:
        users = service.search_users(q, skip, limit)
    elif role:
        try:
            user_role = UserRole(role)
            users = service.get_users_by_role(user_role, skip, limit)
        except ValueError:
            users = service.get_all_users(skip, limit)
    else:
        users = service.get_all_users(skip, limit)

    return [
        UserResponse(
            id=u.id, name=u.name, email=u.email,
            role=u.role.value, student_id=u.student_id,
            phone=u.phone, status=u.status.value,
        )
        for u in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserResponse(
        id=user.id, name=user.name, email=user.email,
        role=user.role.value, student_id=user.student_id,
        phone=user.phone, status=user.status.value,
    )
