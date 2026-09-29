"""
Fine Service
Business logic for fine management.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.data_access.fine_repository import FineRepository
from app.domain.entities.fine import Fine
from app.domain.enums import FineStatus


class FineService:
    def __init__(self, db: Session):
        self.fine_repo = FineRepository(db)
        self.db = db

    def get_user_fines(self, user_id: int) -> List[Fine]:
        return self.fine_repo.get_user_fines(user_id)

    def get_unpaid_fines(self, user_id: int) -> List[Fine]:
        return self.fine_repo.get_unpaid_for_user(user_id)

    def get_total_unpaid(self, user_id: int) -> float:
        return self.fine_repo.get_total_unpaid(user_id)

    def pay_fine(self, fine_id: int, user_id: int) -> Fine:
        fine = self.fine_repo.get_by_id(fine_id)
        if not fine:
            raise ValueError("Fine not found.")
        if fine.user_id != user_id:
            raise ValueError("This fine does not belong to you.")
        if fine.status == FineStatus.PAID:
            raise ValueError("This fine has already been paid.")

        fine.status = FineStatus.PAID
        fine.paid_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(fine)
        return fine

    def waive_fine(self, fine_id: int) -> Fine:
        """Admin/librarian can waive a fine."""
        fine = self.fine_repo.get_by_id(fine_id)
        if not fine:
            raise ValueError("Fine not found.")
        fine.status = FineStatus.WAIVED
        self.db.commit()
        self.db.refresh(fine)
        return fine

    def get_all_fines(self, skip: int = 0, limit: int = 100) -> List[Fine]:
        return self.fine_repo.get_all_with_details(skip, limit)

    def get_total_collected(self) -> float:
        return self.fine_repo.get_total_collected()

    def get_total_pending(self) -> float:
        return self.fine_repo.get_total_pending()
