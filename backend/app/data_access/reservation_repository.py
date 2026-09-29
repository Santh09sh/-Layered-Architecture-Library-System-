"""
Reservation Repository
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.data_access.base_repository import BaseRepository
from app.domain.entities.reservation import Reservation
from app.domain.enums import ReservationStatus


class ReservationRepository(BaseRepository[Reservation]):
    def __init__(self, db: Session):
        super().__init__(Reservation, db)

    def get_active_for_book(self, book_id: int) -> List[Reservation]:
        return (
            self.db.query(Reservation)
            .filter(
                Reservation.book_id == book_id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.READY])
            )
            .order_by(Reservation.queue_position)
            .all()
        )

    def get_next_in_queue(self, book_id: int) -> Optional[Reservation]:
        return (
            self.db.query(Reservation)
            .filter(
                Reservation.book_id == book_id,
                Reservation.status == ReservationStatus.PENDING
            )
            .order_by(Reservation.queue_position)
            .first()
        )

    def get_user_reservations(self, user_id: int) -> List[Reservation]:
        return (
            self.db.query(Reservation)
            .options(joinedload(Reservation.book))
            .filter(Reservation.user_id == user_id)
            .order_by(Reservation.reserved_at.desc())
            .all()
        )

    def get_active_user_reservation_for_book(self, user_id: int, book_id: int) -> Optional[Reservation]:
        return (
            self.db.query(Reservation)
            .filter(
                Reservation.user_id == user_id,
                Reservation.book_id == book_id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.READY])
            )
            .first()
        )

    def count_pending(self) -> int:
        return (
            self.db.query(Reservation)
            .filter(Reservation.status == ReservationStatus.PENDING)
            .count()
        )

    def has_active_reservation(self, book_id: int) -> bool:
        return (
            self.db.query(Reservation)
            .filter(
                Reservation.book_id == book_id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.READY])
            )
            .first() is not None
        )

    def get_all_with_details(self, skip: int = 0, limit: int = 100) -> List[Reservation]:
        return (
            self.db.query(Reservation)
            .options(joinedload(Reservation.user), joinedload(Reservation.book))
            .order_by(Reservation.reserved_at.desc())
            .offset(skip).limit(limit).all()
        )
