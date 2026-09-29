"""
Graph Service
Builds and queries an in-memory entity graph from SQL data.
This is the core of the Entity Graph feature.
"""

from typing import List, Optional, Dict, Set
from collections import defaultdict
from sqlalchemy.orm import Session, joinedload

from app.domain.entities.book import Book
from app.domain.entities.author import Author
from app.domain.entities.publisher import Publisher
from app.domain.entities.category import Category
from app.domain.entities.book_copy import BookCopy
from app.domain.entities.user import User
from app.domain.entities.borrow_record import BorrowRecord
from app.domain.entities.review import Review
from app.domain.entities.reservation import Reservation
from app.domain.enums import BorrowStatus, ReservationStatus
from app.graph.models import GraphNode, GraphEdge, GraphData, GraphSearchResult


class GraphService:
    """
    In-memory entity graph built from relational data.
    Nodes represent entities, edges represent relationships.
    """

    def __init__(self, db: Session):
        self.db = db

    def _make_node(self, entity_type: str, entity_id: int, label: str, **props) -> GraphNode:
        return GraphNode(
            id=f"{entity_type.lower()}_{entity_id}",
            label=label,
            type=entity_type,
            properties=props,
        )

    def _make_edge(self, src: str, tgt: str, rel: str, **props) -> GraphEdge:
        return GraphEdge(source=src, target=tgt, relationship=rel, properties=props)

    def get_book_graph(self, book_id: int) -> GraphData:
        """Build the full entity graph centered on a single book."""
        book = (
            self.db.query(Book)
            .options(
                joinedload(Book.authors),
                joinedload(Book.publisher),
                joinedload(Book.category),
                joinedload(Book.copies),
            )
            .filter(Book.id == book_id)
            .first()
        )
        if not book:
            return GraphData()

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        seen_nodes: Set[str] = set()

        # Book node
        book_nid = f"book_{book.id}"
        nodes.append(self._make_node("Book", book.id, book.title,
                                      isbn=book.isbn, year=book.publication_year,
                                      rating=book.average_rating))
        seen_nodes.add(book_nid)

        # Authors
        for author in book.authors:
            nid = f"author_{author.id}"
            if nid not in seen_nodes:
                nodes.append(self._make_node("Author", author.id, author.name,
                                              nationality=author.nationality))
                seen_nodes.add(nid)
            edges.append(self._make_edge(book_nid, nid, "WRITTEN_BY"))

        # Publisher
        if book.publisher:
            nid = f"publisher_{book.publisher.id}"
            if nid not in seen_nodes:
                nodes.append(self._make_node("Publisher", book.publisher.id, book.publisher.name))
                seen_nodes.add(nid)
            edges.append(self._make_edge(book_nid, nid, "PUBLISHED_BY"))

        # Category
        if book.category:
            nid = f"category_{book.category.id}"
            if nid not in seen_nodes:
                nodes.append(self._make_node("Category", book.category.id, book.category.name))
                seen_nodes.add(nid)
            edges.append(self._make_edge(book_nid, nid, "BELONGS_TO"))

        # Copies + Borrowers
        for copy in book.copies:
            copy_nid = f"copy_{copy.id}"
            nodes.append(self._make_node("BookCopy", copy.id, f"Copy #{copy.accession_number}",
                                          status=copy.status.value, location=copy.location))
            seen_nodes.add(copy_nid)
            edges.append(self._make_edge(copy_nid, book_nid, "INSTANCE_OF"))

            # Active borrows for this copy
            borrows = (
                self.db.query(BorrowRecord)
                .filter(
                    BorrowRecord.book_copy_id == copy.id,
                    BorrowRecord.status.in_([BorrowStatus.ACTIVE, BorrowStatus.OVERDUE])
                )
                .all()
            )
            for br in borrows:
                user = self.db.query(User).filter(User.id == br.user_id).first()
                if user:
                    user_nid = f"user_{user.id}"
                    if user_nid not in seen_nodes:
                        nodes.append(self._make_node("User", user.id, user.name,
                                                      role=user.role.value))
                        seen_nodes.add(user_nid)
                    edges.append(self._make_edge(user_nid, copy_nid, "BORROWED",
                                                  due_date=str(br.due_date)))

        # Related books (same category)
        if book.category:
            related = (
                self.db.query(Book)
                .filter(Book.category_id == book.category_id, Book.id != book.id)
                .limit(5)
                .all()
            )
            for rb in related:
                rb_nid = f"book_{rb.id}"
                if rb_nid not in seen_nodes:
                    nodes.append(self._make_node("Book", rb.id, rb.title, isbn=rb.isbn))
                    seen_nodes.add(rb_nid)
                edges.append(self._make_edge(book_nid, rb_nid, "RELATED_TO"))

        return GraphData(nodes=nodes, edges=edges)

    def get_user_graph(self, user_id: int) -> GraphData:
        """Build the entity graph centered on a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return GraphData()

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        seen_nodes: Set[str] = set()

        user_nid = f"user_{user.id}"
        nodes.append(self._make_node("User", user.id, user.name,
                                      role=user.role.value, email=user.email))
        seen_nodes.add(user_nid)

        # Borrow records
        borrows = (
            self.db.query(BorrowRecord)
            .options(joinedload(BorrowRecord.book_copy).joinedload(BookCopy.book))
            .filter(BorrowRecord.user_id == user_id)
            .order_by(BorrowRecord.borrowed_at.desc())
            .limit(20)
            .all()
        )

        for br in borrows:
            copy = br.book_copy
            book = copy.book if copy else None
            if not book:
                continue

            book_nid = f"book_{book.id}"
            if book_nid not in seen_nodes:
                nodes.append(self._make_node("Book", book.id, book.title,
                                              isbn=book.isbn, category=book.category.name if book.category else None))
                seen_nodes.add(book_nid)

            copy_nid = f"copy_{copy.id}"
            if copy_nid not in seen_nodes:
                nodes.append(self._make_node("BookCopy", copy.id, f"Copy #{copy.accession_number}",
                                              status=copy.status.value))
                seen_nodes.add(copy_nid)

            edges.append(self._make_edge(user_nid, copy_nid, "BORROWED",
                                          status=br.status.value, due_date=str(br.due_date)))
            edges.append(self._make_edge(copy_nid, book_nid, "INSTANCE_OF"))

            # Book → Authors
            for author in book.authors:
                a_nid = f"author_{author.id}"
                if a_nid not in seen_nodes:
                    nodes.append(self._make_node("Author", author.id, author.name))
                    seen_nodes.add(a_nid)
                edges.append(self._make_edge(book_nid, a_nid, "WRITTEN_BY"))

            # Book → Category
            if book.category:
                c_nid = f"category_{book.category.id}"
                if c_nid not in seen_nodes:
                    nodes.append(self._make_node("Category", book.category.id, book.category.name))
                    seen_nodes.add(c_nid)
                edges.append(self._make_edge(book_nid, c_nid, "BELONGS_TO"))

        # Reviews
        reviews = self.db.query(Review).filter(Review.user_id == user_id).all()
        for review in reviews:
            book = self.db.query(Book).filter(Book.id == review.book_id).first()
            if book:
                book_nid = f"book_{book.id}"
                if book_nid not in seen_nodes:
                    nodes.append(self._make_node("Book", book.id, book.title))
                    seen_nodes.add(book_nid)
                edges.append(self._make_edge(user_nid, book_nid, "REVIEWED",
                                              rating=review.rating))

        return GraphData(nodes=nodes, edges=edges)

    def search_graph(self, query: str) -> GraphSearchResult:
        """Search across all entity types and return matching graph elements."""
        search_term = f"%{query}%"
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        seen: Set[str] = set()

        # Search books
        books = self.db.query(Book).filter(
            (Book.title.ilike(search_term)) | (Book.isbn.ilike(search_term))
        ).limit(10).all()
        for b in books:
            nid = f"book_{b.id}"
            if nid not in seen:
                nodes.append(self._make_node("Book", b.id, b.title, isbn=b.isbn))
                seen.add(nid)

        # Search authors
        authors = self.db.query(Author).filter(Author.name.ilike(search_term)).limit(10).all()
        for a in authors:
            nid = f"author_{a.id}"
            if nid not in seen:
                nodes.append(self._make_node("Author", a.id, a.name))
                seen.add(nid)

        # Search categories
        categories = self.db.query(Category).filter(Category.name.ilike(search_term)).limit(10).all()
        for c in categories:
            nid = f"category_{c.id}"
            if nid not in seen:
                nodes.append(self._make_node("Category", c.id, c.name))
                seen.add(nid)

        # Search users
        users = self.db.query(User).filter(User.name.ilike(search_term)).limit(10).all()
        for u in users:
            nid = f"user_{u.id}"
            if nid not in seen:
                nodes.append(self._make_node("User", u.id, u.name, role=u.role.value))
                seen.add(nid)

        # Build edges between found nodes
        for node in nodes:
            if node.type == "Book":
                bid = int(node.id.split("_")[1])
                book = self.db.query(Book).options(
                    joinedload(Book.authors), joinedload(Book.category)
                ).filter(Book.id == bid).first()
                if book:
                    for author in book.authors:
                        a_nid = f"author_{author.id}"
                        if a_nid not in seen:
                            nodes.append(self._make_node("Author", author.id, author.name))
                            seen.add(a_nid)
                        edges.append(self._make_edge(node.id, a_nid, "WRITTEN_BY"))
                    if book.category:
                        c_nid = f"category_{book.category.id}"
                        if c_nid not in seen:
                            nodes.append(self._make_node("Category", book.category.id, book.category.name))
                            seen.add(c_nid)
                        edges.append(self._make_edge(node.id, c_nid, "BELONGS_TO"))

        return GraphSearchResult(query=query, nodes=nodes, edges=edges)

    def get_recommendations(self, user_id: int, limit: int = 5) -> List[Dict]:
        """
        Recommend books using graph traversal:
        User → Borrowed Books → Categories → Other Books in same categories
        User → Borrowed Books → Authors → Other Books by same authors
        """
        # Get user's borrowed book IDs
        borrows = (
            self.db.query(BorrowRecord)
            .options(joinedload(BorrowRecord.book_copy).joinedload(BookCopy.book))
            .filter(BorrowRecord.user_id == user_id)
            .all()
        )

        borrowed_book_ids = set()
        category_ids = set()
        author_ids = set()

        for br in borrows:
            if br.book_copy and br.book_copy.book:
                book = br.book_copy.book
                borrowed_book_ids.add(book.id)
                if book.category_id:
                    category_ids.add(book.category_id)
                for author in book.authors:
                    author_ids.add(author.id)

        if not category_ids and not author_ids:
            # No history — return popular books
            popular = (
                self.db.query(Book)
                .options(joinedload(Book.authors), joinedload(Book.category), joinedload(Book.copies))
                .order_by(Book.average_rating.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "book": b,
                    "reason": "Popular book with high ratings",
                    "score": b.average_rating or 0
                }
                for b in popular
            ]

        # Find books in same categories or by same authors, not already borrowed
        from sqlalchemy import or_
        from app.domain.entities.associations import book_authors

        recommendations = (
            self.db.query(Book)
            .options(joinedload(Book.authors), joinedload(Book.category), joinedload(Book.copies))
            .filter(
                Book.id.notin_(borrowed_book_ids),
                or_(
                    Book.category_id.in_(category_ids),
                    Book.authors.any(Author.id.in_(author_ids))
                )
            )
            .order_by(Book.average_rating.desc())
            .limit(limit)
            .all()
        )

        results = []
        for book in recommendations:
            reasons = []
            if book.category_id in category_ids:
                reasons.append(f"Same category: {book.category.name}" if book.category else "Similar category")
            for author in book.authors:
                if author.id in author_ids:
                    reasons.append(f"By author you've read: {author.name}")
            results.append({
                "book": book,
                "reason": "; ".join(reasons) if reasons else "Recommended for you",
                "score": book.average_rating or 0,
            })

        return results

    def find_related_books(self, book_id: int, limit: int = 5) -> List[Dict]:
        """Find books related to a given book via shared authors and categories."""
        book = (
            self.db.query(Book)
            .options(joinedload(Book.authors), joinedload(Book.category))
            .filter(Book.id == book_id)
            .first()
        )
        if not book:
            return []

        author_ids = [a.id for a in book.authors]
        from sqlalchemy import or_

        related = (
            self.db.query(Book)
            .options(joinedload(Book.authors), joinedload(Book.category), joinedload(Book.copies))
            .filter(
                Book.id != book_id,
                or_(
                    Book.category_id == book.category_id,
                    Book.authors.any(Author.id.in_(author_ids)) if author_ids else False
                )
            )
            .order_by(Book.average_rating.desc())
            .limit(limit)
            .all()
        )

        results = []
        for rb in related:
            reasons = []
            if rb.category_id == book.category_id and book.category:
                reasons.append(f"Same category: {book.category.name}")
            for a in rb.authors:
                if a.id in author_ids:
                    reasons.append(f"Same author: {a.name}")
            results.append({
                "book": rb,
                "reason": "; ".join(reasons),
            })
        return results
