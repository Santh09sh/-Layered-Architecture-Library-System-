"""
Auth Routes
Login, Register, and user profile endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.business.auth_service import AuthService
from app.application.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse, UserUpdateRequest,
)
from app.application.dependencies import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."},
        )

    token = auth_service.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id, name=user.name, email=user.email,
            role=user.role.value, student_id=user.student_id,
            phone=user.phone, status=user.status.value,
            avatar_url=user.avatar_url,
        ),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        user = auth_service.register_user(
            name=request.name, email=request.email, password=request.password,
            student_id=request.student_id, phone=request.phone,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"code": "REGISTRATION_ERROR", "message": str(e)})

    token = auth_service.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id, name=user.name, email=user.email,
            role=user.role.value, student_id=user.student_id,
            phone=user.phone, status=user.status.value,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id, name=current_user.name, email=current_user.email,
        role=current_user.role.value, student_id=current_user.student_id,
        phone=current_user.phone, status=current_user.status.value,
        avatar_url=current_user.avatar_url,
    )
