"""
Tool Registry
Defines all tools available to the AI agent.
Tools are functions that the AI can call to get real data.
"""

from typing import Dict, List, Any, Callable, Optional
from sqlalchemy.orm import Session

from app.business.book_service import BookService
from app.business.borrowing_service import BorrowingService
from app.business.fine_service import FineService
from app.business.analytics_service import AnalyticsService
from app.business.reservation_service import ReservationService
from app.graph.graph_service import GraphService
from app.domain.enums import BookCopyStatus


class ToolRegistry:
    """Registry of tools the AI agent can use. All data comes from real database queries."""

    def __init__(self, db: Session, user_id: Optional[int] = None):
        self.db = db
        self.user_id = user_id
        self.book_service = BookService(db)
        self.borrow_service = BorrowingService(db)
        self.fine_service = FineService(db)
        self.analytics_service = AnalyticsService(db)
        self.reservation_service = ReservationService(db)
        self.graph_service = GraphService(db)

    def get_tool_definitions(self) -> List[Dict]:
        """Return tool schemas for the LLM to understand available tools."""
        return [
            {
                "name": "search_books",
                "description": "Search for books by title, ISBN, or description. Returns matching books with availability.",
                "parameters": {"query": "string - search query", "available_only": "boolean - only show available books"},
            },
            {
                "name": "get_book_details",
                "description": "Get detailed information about a specific book including availability and reviews.",
                "parameters": {"book_id": "integer - the book ID"},
            },
            {
                "name": "check_book_availability",
                "description": "Check if a specific book has available copies for borrowing.",
                "parameters": {"book_id": "integer - the book ID"},
            },
            {
                "name": "get_user_borrowing_history",
                "description": "Get the current user's borrowing history.",
                "parameters": {},
            },
            {
                "name": "get_overdue_books",
                "description": "Get list of overdue books (for librarians/admins) or current user's overdue books.",
                "parameters": {},
            },
            {
                "name": "calculate_fine",
                "description": "Get the current user's pending fines.",
                "parameters": {},
            },
            {
                "name": "search_entity_graph",
                "description": "Search the entity graph for relationships between books, authors, categories, and users.",
                "parameters": {"query": "string - search query"},
            },
            {
                "name": "find_related_books",
                "description": "Find books related to a given book through shared authors or categories.",
                "parameters": {"book_id": "integer - the book ID"},
            },
            {
                "name": "recommend_books",
                "description": "Get personalized book recommendations based on borrowing history.",
                "parameters": {},
            },
            {
                "name": "search_authors",
                "description": "Search for authors by name.",
                "parameters": {"query": "string - author name to search"},
            },
            {
                "name": "get_library_statistics",
                "description": "Get library statistics: total books, active borrows, overdue count, etc.",
                "parameters": {},
            },
            {
                "name": "check_borrowing_eligibility",
                "description": "Check if the current user is eligible to borrow books.",
                "parameters": {},
            },
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result. All data comes from the database."""
        try:
            handler = self._get_handler(tool_name)
            if handler is None:
                return {"error": f"Unknown tool: {tool_name}"}
            return handler(arguments)
        except Exception as e:
            return {"error": str(e)}

    def _get_handler(self, tool_name: str) -> Optional[Callable]:
        handlers = {
            "search_books": self._search_books,
            "get_book_details": self._get_book_details,
            "check_book_availability": self._check_availability,
            "get_user_borrowing_history": self._get_history,
            "get_overdue_books": self._get_overdue,
            "calculate_fine": self._calculate_fine,
            "search_entity_graph": self._search_graph,
            "find_related_books": self._find_related,
            "recommend_books": self._recommend,
            "search_authors": self._search_authors,
            "get_library_statistics": self._get_stats,
            "check_borrowing_eligibility": self._check_eligibility,
        }
        return handlers.get(tool_name)

    def _search_books(self, args: Dict) -> Dict:
        query = args.get("query", "")
        available_only = args.get("available_only", False)
        books = self.book_service.search_books(query, available_only=available_only)
        return {
            "results": [
                {
                    "id": b.id, "title": b.title, "isbn": b.isbn,
                    "authors": [a.name for a in b.authors],
                    "category": b.category.name if b.category else None,
                    "rating": b.average_rating,
                    "available_copies": sum(1 for c in b.copies if c.status == BookCopyStatus.AVAILABLE),
                    "total_copies": len(b.copies),
                }
                for b in books[:10]
            ],
            "total": len(books),
        }

    def _get_book_details(self, args: Dict) -> Dict:
        book_id = args.get("book_id")
        if not book_id:
            return {"error": "book_id is required"}
        book = self.book_service.get_book(int(book_id))
        if not book:
            return {"error": "Book not found"}
        return {
            "id": book.id, "title": book.title, "isbn": book.isbn,
            "description": book.description,
            "authors": [a.name for a in book.authors],
            "publisher": book.publisher.name if book.publisher else None,
            "category": book.category.name if book.category else None,
            "year": book.publication_year,
            "rating": book.average_rating, "total_ratings": book.total_ratings,
            "copies": [
                {"id": c.id, "status": c.status.value, "location": c.location}
                for c in book.copies
            ],
        }

    def _check_availability(self, args: Dict) -> Dict:
        book_id = args.get("book_id")
        if not book_id:
            return {"error": "book_id is required"}
        copies = self.book_service.get_available_copies(int(book_id))
        return {
            "book_id": book_id,
            "available": len(copies) > 0,
            "available_count": len(copies),
            "copies": [{"id": c.id, "location": c.location} for c in copies],
        }

    def _get_history(self, args: Dict) -> Dict:
        if not self.user_id:
            return {"error": "User not authenticated"}
        records = self.borrow_service.get_user_history(self.user_id)
        return {
            "records": [
                {
                    "id": r.id,
                    "book_title": r.book_copy.book.title if r.book_copy and r.book_copy.book else "Unknown",
                    "borrowed_at": str(r.borrowed_at),
                    "due_date": str(r.due_date),
                    "returned_at": str(r.returned_at) if r.returned_at else None,
                    "status": r.status.value,
                }
                for r in records
            ]
        }

    def _get_overdue(self, args: Dict) -> Dict:
        records = self.borrow_service.get_overdue_records()
        return {
            "overdue_count": len(records),
            "records": [
                {
                    "user_name": r.user.name if r.user else "Unknown",
                    "book_title": r.book_copy.book.title if r.book_copy and r.book_copy.book else "Unknown",
                    "due_date": str(r.due_date),
                    "days_overdue": (
                        __import__("datetime").datetime.utcnow() - r.due_date
                    ).days if r.due_date else 0,
                }
                for r in records[:20]
            ],
        }

    def _calculate_fine(self, args: Dict) -> Dict:
        if not self.user_id:
            return {"error": "User not authenticated"}
        total = self.fine_service.get_total_unpaid(self.user_id)
        fines = self.fine_service.get_unpaid_fines(self.user_id)
        return {
            "total_unpaid": total,
            "fines": [
                {"id": f.id, "amount": f.amount, "reason": f.reason}
                for f in fines
            ],
        }

    def _search_graph(self, args: Dict) -> Dict:
        query = args.get("query", "")
        result = self.graph_service.search_graph(query)
        return {
            "nodes": [n.model_dump() for n in result.nodes],
            "edges": [e.model_dump() for e in result.edges],
        }

    def _find_related(self, args: Dict) -> Dict:
        book_id = args.get("book_id")
        if not book_id:
            return {"error": "book_id is required"}
        related = self.graph_service.find_related_books(int(book_id))
        return {
            "related": [
                {
                    "id": r["book"].id, "title": r["book"].title,
                    "reason": r["reason"],
                    "rating": r["book"].average_rating,
                }
                for r in related
            ]
        }

    def _recommend(self, args: Dict) -> Dict:
        if not self.user_id:
            return {"error": "User not authenticated"}
        recs = self.graph_service.get_recommendations(self.user_id)
        return {
            "recommendations": [
                {
                    "id": r["book"].id, "title": r["book"].title,
                    "authors": [a.name for a in r["book"].authors],
                    "reason": r["reason"],
                    "rating": r.get("score", 0),
                    "available": sum(1 for c in r["book"].copies if c.status == BookCopyStatus.AVAILABLE),
                }
                for r in recs
            ]
        }

    def _search_authors(self, args: Dict) -> Dict:
        query = args.get("query", "")
        authors = self.book_service.search_authors(query)
        return {
            "authors": [
                {"id": a.id, "name": a.name, "nationality": a.nationality,
                 "book_count": len(a.books) if hasattr(a, 'books') and a.books else 0}
                for a in authors[:10]
            ]
        }

    def _get_stats(self, args: Dict) -> Dict:
        return self.analytics_service.get_library_statistics()

    def _check_eligibility(self, args: Dict) -> Dict:
        if not self.user_id:
            return {"error": "User not authenticated"}
        return self.borrow_service.check_eligibility(self.user_id)
