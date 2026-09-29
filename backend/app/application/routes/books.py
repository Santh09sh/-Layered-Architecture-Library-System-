"""
Book Routes
CRUD and search endpoints for books, authors, publishers, categories.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.business.book_service import BookService
from app.application.schemas.book import (
    BookCreate, BookUpdate, BookResponse, BookListResponse,
    AuthorCreate, AuthorResponse,
    PublisherCreate, PublisherResponse,
    CategoryCreate, CategoryResponse,
    BookCopyCreate, BookCopyResponse,
)
from app.application.dependencies import get_current_user, require_librarian
from app.domain.entities.user import User
from app.domain.enums import BookCopyStatus

router = APIRouter(prefix="/api", tags=["Library"])


def _book_to_response(book) -> BookResponse:
    available = sum(1 for c in book.copies if c.status == BookCopyStatus.AVAILABLE) if book.copies else 0
    return BookResponse(
        id=book.id, isbn=book.isbn, title=book.title,
        description=book.description, publication_year=book.publication_year,
        language=book.language, pages=book.pages, cover_image=book.cover_image,
        average_rating=book.average_rating or 0, total_ratings=book.total_ratings or 0,
        authors=[AuthorResponse(id=a.id, name=a.name, biography=a.biography,
                                 nationality=a.nationality,
                                 book_count=len(a.books) if a.books else 0) for a in book.authors],
        publisher=PublisherResponse(id=book.publisher.id, name=book.publisher.name,
                                    website=book.publisher.website,
                                    address=book.publisher.address) if book.publisher else None,
        category=CategoryResponse(id=book.category.id, name=book.category.name,
                                   description=book.category.description) if book.category else None,
        copies=[BookCopyResponse(id=c.id, accession_number=c.accession_number, barcode=c.barcode,
                                  status=c.status.value, location=c.location,
                                  condition=c.condition.value) for c in book.copies],
        available_copies=available,
    )


def _book_to_list(book) -> BookListResponse:
    available = sum(1 for c in book.copies if c.status == BookCopyStatus.AVAILABLE) if book.copies else 0
    return BookListResponse(
        id=book.id, isbn=book.isbn, title=book.title,
        cover_image=book.cover_image,
        average_rating=book.average_rating or 0, total_ratings=book.total_ratings or 0,
        authors=[AuthorResponse(id=a.id, name=a.name, nationality=a.nationality,
                                 book_count=len(a.books) if a.books else 0) for a in book.authors],
        category=CategoryResponse(id=book.category.id, name=book.category.name) if book.category else None,
        available_copies=available,
        total_copies=len(book.copies) if book.copies else 0,
    )


# --- Books ---

@router.get("/books", response_model=List[BookListResponse])
async def list_books(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    available_only: bool = False,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
):
    service = BookService(db)
    if q or category_id or author_id or available_only:
        books = service.search_books(q or "", category_id, author_id, available_only, skip, limit)
    else:
        books = service.get_all_books(skip, limit)
    return [_book_to_list(b) for b in books]


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    service = BookService(db)
    book = service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail={"code": "BOOK_NOT_FOUND", "message": "Book not found."})
    return _book_to_response(book)


@router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(
    request: BookCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BookService(db)
    try:
        book = service.create_book(
            isbn=request.isbn, title=request.title, description=request.description,
            publication_year=request.publication_year, language=request.language,
            pages=request.pages, cover_image=request.cover_image,
            publisher_id=request.publisher_id, category_id=request.category_id,
            author_ids=request.author_ids,
        )
        return _book_to_response(service.get_book(book.id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BOOK_ERROR", "message": str(e)})


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int, request: BookUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BookService(db)
    try:
        service.update_book(book_id, **request.model_dump(exclude_none=True))
        return _book_to_response(service.get_book(book_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BOOK_ERROR", "message": str(e)})


@router.delete("/books/{book_id}")
async def delete_book(
    book_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BookService(db)
    if not service.delete_book(book_id):
        raise HTTPException(status_code=404, detail={"code": "BOOK_NOT_FOUND", "message": "Book not found."})
    return {"success": True, "message": "Book deleted."}


# --- Book Copies ---

@router.post("/book-copies", response_model=BookCopyResponse, status_code=201)
async def add_copy(
    request: BookCopyCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BookService(db)
    try:
        copy = service.add_copy(
            book_id=request.book_id, accession_number=request.accession_number,
            barcode=request.barcode, location=request.location,
        )
        return BookCopyResponse(
            id=copy.id, accession_number=copy.accession_number,
            barcode=copy.barcode, status=copy.status.value,
            location=copy.location, condition=copy.condition.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "COPY_ERROR", "message": str(e)})


# --- Authors ---

@router.get("/authors", response_model=List[AuthorResponse])
async def list_authors(
    q: Optional[str] = None, skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
):
    service = BookService(db)
    if q:
        authors = service.search_authors(q)
    else:
        authors = service.get_all_authors(skip, limit)
    return [
        AuthorResponse(id=a.id, name=a.name, biography=a.biography,
                        nationality=a.nationality,
                        book_count=len(a.books) if a.books else 0)
        for a in authors
    ]


@router.get("/authors/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int, db: Session = Depends(get_db)):
    service = BookService(db)
    author = service.get_author(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found.")
    return AuthorResponse(
        id=author.id, name=author.name, biography=author.biography,
        nationality=author.nationality,
        book_count=len(author.books) if author.books else 0,
    )


@router.post("/authors", response_model=AuthorResponse, status_code=201)
async def create_author(
    request: AuthorCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BookService(db)
    author = service.create_author(name=request.name, biography=request.biography,
                                    nationality=request.nationality)
    return AuthorResponse(id=author.id, name=author.name, biography=author.biography,
                           nationality=author.nationality)


# --- Publishers ---

@router.get("/publishers", response_model=List[PublisherResponse])
async def list_publishers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookService(db)
    publishers = service.get_all_publishers(skip, limit)
    return [PublisherResponse(id=p.id, name=p.name, website=p.website, address=p.address) for p in publishers]


@router.post("/publishers", response_model=PublisherResponse, status_code=201)
async def create_publisher(
    request: PublisherCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BookService(db)
    pub = service.create_publisher(name=request.name, website=request.website, address=request.address)
    return PublisherResponse(id=pub.id, name=pub.name, website=pub.website, address=pub.address)


# --- Categories ---

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookService(db)
    categories = service.get_all_categories(skip, limit)
    return [CategoryResponse(id=c.id, name=c.name, description=c.description) for c in categories]


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CategoryCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian),
):
    service = BookService(db)
    try:
        cat = service.create_category(name=request.name, description=request.description)
        return CategoryResponse(id=cat.id, name=cat.name, description=cat.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
