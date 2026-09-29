"""
Author Repository
Data access operations for Author entity.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.data_access.base_repository import BaseRepository
from app.domain.entities.author import Author


class AuthorRepository(BaseRepository[Author]):
    def __init__(self, db: Session):
        super().__init__(Author, db)

    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Author]:
        search_term = f"%{query}%"
        return (
            self.db.query(Author)
            .filter(Author.name.ilike(search_term))
            .offset(skip).limit(limit).all()
        )

    def get_with_books(self, author_id: int) -> Optional[Author]:
        return (
            self.db.query(Author)
            .options(joinedload(Author.books))
            .filter(Author.id == author_id)
            .first()
        )

    def get_all_with_books(self, skip: int = 0, limit: int = 100) -> List[Author]:
        return (
            self.db.query(Author)
            .options(joinedload(Author.books))
            .offset(skip).limit(limit).all()
        )
