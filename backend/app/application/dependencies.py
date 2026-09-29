"""
Authentication Dependencies
FastAPI dependencies for JWT auth and role-based access control.
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.business.auth_service import AuthService
from app.domain.entities.user import User
from app.domain.enums import UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired authentication token."},
        )
    return user


def require_role(allowed_roles: List[UserRole]):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "You do not have permission to access this resource."},
            )
        return current_user
    return role_checker


# Convenience dependencies
require_admin = require_role([UserRole.ADMIN])
require_librarian = require_role([UserRole.ADMIN, UserRole.LIBRARIAN])
require_student = require_role([UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.STUDENT])
