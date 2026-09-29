"""
Pydantic Schemas for Books, Authors, Publishers, Categories
"""

from typing import Optional, List
from pydantic import BaseModel, Field


# --- Author ---
class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    biography: Optional[str] = None
    nationality: Optional[str] = None


class AuthorResponse(BaseModel):
    id: int
    name: str
    biography: Optional[str] = None
    nationality: Optional[str] = None
    book_count: int = 0

    class Config:
        from_attributes = True


# --- Publisher ---
class PublisherCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website: Optional[str] = None
    address: Optional[str] = None


class PublisherResponse(BaseModel):
    id: int
    name: str
    website: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


# --- Category ---
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# --- BookCopy ---
class BookCopyResponse(BaseModel):
    id: int
    accession_number: str
    barcode: Optional[str] = None
    status: str
    location: Optional[str] = None
    condition: str

    class Config:
        from_attributes = True


class BookCopyCreate(BaseModel):
    book_id: int
    accession_number: str
    barcode: Optional[str] = None
    location: Optional[str] = None
    condition: str = "NEW"


# --- Book ---
class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    publication_year: Optional[int] = None
    language: str = "English"
    pages: Optional[int] = None
    cover_image: Optional[str] = None
    publisher_id: Optional[int] = None
    category_id: Optional[int] = None
    author_ids: Optional[List[int]] = []


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    publication_year: Optional[int] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    cover_image: Optional[str] = None
    publisher_id: Optional[int] = None
    category_id: Optional[int] = None
    author_ids: Optional[List[int]] = None


class BookResponse(BaseModel):
    id: int
    isbn: str
    title: str
    description: Optional[str] = None
    publication_year: Optional[int] = None
    language: str = "English"
    pages: Optional[int] = None
    cover_image: Optional[str] = None
    average_rating: float = 0.0
    total_ratings: int = 0
    authors: List[AuthorResponse] = []
    publisher: Optional[PublisherResponse] = None
    category: Optional[CategoryResponse] = None
    copies: List[BookCopyResponse] = []
    available_copies: int = 0

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    id: int
    isbn: str
    title: str
    cover_image: Optional[str] = None
    average_rating: float = 0.0
    total_ratings: int = 0
    authors: List[AuthorResponse] = []
    category: Optional[CategoryResponse] = None
    available_copies: int = 0
    total_copies: int = 0

    class Config:
        from_attributes = True
