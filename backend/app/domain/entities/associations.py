"""
Association Tables
Many-to-many relationship tables.
"""

from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

# Book <-> Author (many-to-many)
book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)
