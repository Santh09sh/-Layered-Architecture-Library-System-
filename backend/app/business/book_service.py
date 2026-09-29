"""
Book Service
Business logic for book management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.data_access.book_repository import BookRepository
from app.data_access.author_repository import AuthorRepository
from app.data_access.publisher_repository import PublisherRepository
from app.data_access.category_repository import CategoryRepository
from app.data_access.book_copy_repository import BookCopyRepository
from app.domain.entities.book import Book
from app.domain.entities.book_copy import BookCopy
from app.domain.entities.author import Author
from app.domain.entities.publisher import Publisher
from app.domain.entities.category import Category
from app.domain.enums import BookCopyStatus, BookCondition


class BookService:
    def __init__(self, db: Session):
        self.book_repo = BookRepository(db)
        self.author_repo = AuthorRepository(db)
        self.publisher_repo = PublisherRepository(db)
        self.category_repo = CategoryRepository(db)
        self.copy_repo = BookCopyRepository(db)
        self.db = db

    # --- Book Operations ---

    def get_book(self, book_id: int) -> Optional[Book]:
        return self.book_repo.get_by_id_with_relations(book_id)

    def get_all_books(self, skip: int = 0, limit: int = 100) -> List[Book]:
        return self.book_repo.get_all_with_relations(skip, limit)

    def search_books(self, query: str, category_id: Optional[int] = None,
                     author_id: Optional[int] = None, available_only: bool = False,
                     skip: int = 0, limit: int = 50) -> List[Book]:
        return self.book_repo.search(query, category_id, author_id, available_only, skip, limit)

    def create_book(self, isbn: str, title: str, description: Optional[str] = None,
                    publication_year: Optional[int] = None, language: str = "English",
                    pages: Optional[int] = None, cover_image: Optional[str] = None,
                    publisher_id: Optional[int] = None, category_id: Optional[int] = None,
                    author_ids: Optional[List[int]] = None) -> Book:
        # Validate ISBN uniqueness
        existing = self.book_repo.get_by_isbn(isbn)
        if existing:
            raise ValueError(f"A book with ISBN '{isbn}' already exists.")

        book = Book(
            isbn=isbn, title=title, description=description,
            publication_year=publication_year, language=language,
            pages=pages, cover_image=cover_image,
            publisher_id=publisher_id, category_id=category_id,
        )

        # Add authors
        if author_ids:
            for aid in author_ids:
                author = self.author_repo.get_by_id(aid)
                if author:
                    book.authors.append(author)

        return self.book_repo.create(book)

    def update_book(self, book_id: int, **kwargs) -> Optional[Book]:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found.")

        author_ids = kwargs.pop("author_ids", None)
        for key, value in kwargs.items():
            if hasattr(book, key) and value is not None:
                setattr(book, key, value)

        if author_ids is not None:
            book.authors.clear()
            for aid in author_ids:
                author = self.author_repo.get_by_id(aid)
                if author:
                    book.authors.append(author)

        return self.book_repo.update(book)

    def delete_book(self, book_id: int) -> bool:
        return self.book_repo.delete(book_id)

    def get_most_borrowed(self, limit: int = 10) -> List[dict]:
        return self.book_repo.get_most_borrowed(limit)

    def get_available_copy_count(self, book_id: int) -> int:
        return self.book_repo.get_available_copy_count(book_id)

    # --- BookCopy Operations ---

    def add_copy(self, book_id: int, accession_number: str,
                 barcode: Optional[str] = None, location: Optional[str] = None,
                 condition: BookCondition = BookCondition.NEW) -> BookCopy:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found.")

        existing = self.copy_repo.get_by_accession(accession_number)
        if existing:
            raise ValueError(f"Accession number '{accession_number}' already exists.")

        copy = BookCopy(
            book_id=book_id, accession_number=accession_number,
            barcode=barcode, location=location,
            status=BookCopyStatus.AVAILABLE, condition=condition,
        )
        return self.copy_repo.create(copy)

    def get_copies_for_book(self, book_id: int) -> List[BookCopy]:
        return self.copy_repo.get_copies_for_book(book_id)

    def get_available_copies(self, book_id: int) -> List[BookCopy]:
        return self.copy_repo.get_available_copies(book_id)

    # --- Author Operations ---

    def get_author(self, author_id: int) -> Optional[Author]:
        return self.author_repo.get_with_books(author_id)

    def get_all_authors(self, skip: int = 0, limit: int = 100) -> List[Author]:
        return self.author_repo.get_all_with_books(skip, limit)

    def create_author(self, name: str, biography: Optional[str] = None,
                      nationality: Optional[str] = None) -> Author:
        author = Author(name=name, biography=biography, nationality=nationality)
        return self.author_repo.create(author)

    def search_authors(self, query: str) -> List[Author]:
        return self.author_repo.search(query)

    # --- Publisher Operations ---

    def get_publisher(self, publisher_id: int) -> Optional[Publisher]:
        return self.publisher_repo.get_by_id(publisher_id)

    def get_all_publishers(self, skip: int = 0, limit: int = 100) -> List[Publisher]:
        return self.publisher_repo.get_all(skip, limit)

    def create_publisher(self, name: str, website: Optional[str] = None,
                         address: Optional[str] = None) -> Publisher:
        publisher = Publisher(name=name, website=website, address=address)
        return self.publisher_repo.create(publisher)

    # --- Category Operations ---

    def get_category(self, category_id: int) -> Optional[Category]:
        return self.category_repo.get_by_id(category_id)

    def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.category_repo.get_all(skip, limit)

    def create_category(self, name: str, description: Optional[str] = None) -> Category:
        existing = self.category_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Category '{name}' already exists.")
        category = Category(name=name, description=description)
        return self.category_repo.create(category)

    # --- Statistics ---

    def get_total_books(self) -> int:
        return self.book_repo.count()

    def get_total_copies(self) -> int:
        return self.copy_repo.count()
