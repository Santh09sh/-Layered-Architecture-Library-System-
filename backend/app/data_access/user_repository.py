"""
User Repository
Data access operations for User entity.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.data_access.base_repository import BaseRepository
from app.domain.entities.user import User
from app.domain.enums import UserRole, UserStatus


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_student_id(self, student_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.student_id == student_id).first()

    def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

    def get_active_students(self, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            self.db.query(User)
            .filter(User.role == UserRole.STUDENT, User.status == UserStatus.ACTIVE)
            .offset(skip).limit(limit).all()
        )

    def count_by_role(self, role: UserRole) -> int:
        return self.db.query(User).filter(User.role == role).count()

    def count_active(self) -> int:
        return self.db.query(User).filter(User.status == UserStatus.ACTIVE).count()

    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[User]:
        search_term = f"%{query}%"
        return (
            self.db.query(User)
            .filter(
                (User.name.ilike(search_term))
                | (User.email.ilike(search_term))
                | (User.student_id.ilike(search_term))
            )
            .offset(skip).limit(limit).all()
        )
