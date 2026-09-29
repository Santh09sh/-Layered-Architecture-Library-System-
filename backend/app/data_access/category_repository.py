"""
Category Repository
"""

from typing import List
from sqlalchemy.orm import Session
from app.data_access.base_repository import BaseRepository
from app.domain.entities.category import Category


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_by_name(self, name: str):
        return self.db.query(Category).filter(Category.name == name).first()

    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Category]:
        search_term = f"%{query}%"
        return (
            self.db.query(Category)
            .filter(Category.name.ilike(search_term))
            .offset(skip).limit(limit).all()
        )
