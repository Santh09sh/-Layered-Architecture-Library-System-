"""
Fine Repository
"""

from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sql_func
from app.data_access.base_repository import BaseRepository
from app.domain.entities.fine import Fine
from app.domain.enums import FineStatus


class FineRepository(BaseRepository[Fine]):
    def __init__(self, db: Session):
        super().__init__(Fine, db)

    def get_unpaid_for_user(self, user_id: int) -> List[Fine]:
        return (
            self.db.query(Fine)
            .filter(Fine.user_id == user_id, Fine.status == FineStatus.PENDING)
            .all()
        )

    def get_total_unpaid(self, user_id: int) -> float:
        result = (
            self.db.query(sql_func.sum(Fine.amount))
            .filter(Fine.user_id == user_id, Fine.status == FineStatus.PENDING)
            .scalar()
        )
        return result or 0.0

    def get_user_fines(self, user_id: int) -> List[Fine]:
        return (
            self.db.query(Fine)
            .options(joinedload(Fine.borrow_record))
            .filter(Fine.user_id == user_id)
            .order_by(Fine.created_at.desc())
            .all()
        )

    def get_total_collected(self) -> float:
        result = (
            self.db.query(sql_func.sum(Fine.amount))
            .filter(Fine.status == FineStatus.PAID)
            .scalar()
        )
        return result or 0.0

    def get_total_pending(self) -> float:
        result = (
            self.db.query(sql_func.sum(Fine.amount))
            .filter(Fine.status == FineStatus.PENDING)
            .scalar()
        )
        return result or 0.0

    def get_all_with_details(self, skip: int = 0, limit: int = 100) -> List[Fine]:
        return (
            self.db.query(Fine)
            .options(joinedload(Fine.user), joinedload(Fine.borrow_record))
            .order_by(Fine.created_at.desc())
            .offset(skip).limit(limit).all()
        )
