"""
Publisher Repository
"""

from typing import List
from sqlalchemy.orm import Session
from app.data_access.base_repository import BaseRepository
from app.domain.entities.publisher import Publisher


class PublisherRepository(BaseRepository[Publisher]):
    def __init__(self, db: Session):
        super().__init__(Publisher, db)

    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Publisher]:
        search_term = f"%{query}%"
        return (
            self.db.query(Publisher)
            .filter(Publisher.name.ilike(search_term))
            .offset(skip).limit(limit).all()
        )
