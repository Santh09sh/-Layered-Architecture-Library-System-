"""
Authentication Service
Handles JWT token creation, password hashing, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.data_access.user_repository import UserRepository
from app.domain.entities.user import User
from app.domain.enums import UserRole, UserStatus


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if user.status != UserStatus.ACTIVE:
            return None
        return user

    def register_user(self, name: str, email: str, password: str,
                      role: UserRole = UserRole.STUDENT,
                      student_id: Optional[str] = None,
                      phone: Optional[str] = None) -> User:
        # Check if email already exists
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("A user with this email already exists.")

        # Check if student_id already exists
        if student_id:
            existing_sid = self.user_repo.get_by_student_id(student_id)
            if existing_sid:
                raise ValueError("A user with this student ID already exists.")

        user = User(
            name=name,
            email=email,
            password_hash=self.hash_password(password),
            role=role,
            student_id=student_id,
            phone=phone,
            status=UserStatus.ACTIVE,
        )
        return self.user_repo.create(user)

    def get_current_user(self, token: str) -> Optional[User]:
        payload = self.decode_token(token)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return self.user_repo.get_by_id(int(user_id))
