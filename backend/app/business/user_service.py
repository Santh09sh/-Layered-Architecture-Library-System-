"""
User Service
Business logic for user management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.data_access.user_repository import UserRepository
from app.domain.entities.user import User
from app.domain.enums import UserRole, UserStatus


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.user_repo.get_all(skip, limit)

    def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        return self.user_repo.get_by_role(role, skip, limit)

    def search_users(self, query: str, skip: int = 0, limit: int = 50) -> List[User]:
        return self.user_repo.search(query, skip, limit)

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        return self.user_repo.update(user)

    def update_status(self, user_id: int, status: UserStatus) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        user.status = status
        return self.user_repo.update(user)

    def count_by_role(self, role: UserRole) -> int:
        return self.user_repo.count_by_role(role)

    def count_active(self) -> int:
        return self.user_repo.count_active()

    def delete_user(self, user_id: int) -> bool:
        return self.user_repo.delete(user_id)
