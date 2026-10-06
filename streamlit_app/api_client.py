"""
API Client Module
Handles all HTTP communication with the FastAPI backend.
"""

import requests
from typing import Optional, Any

API_BASE = "http://localhost:8000"


class APIClient:
    """Centralized HTTP client with JWT authentication."""

    def __init__(self):
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def set_token(self, token: str):
        """Set JWT token for authenticated requests."""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_token(self):
        """Remove JWT token."""
        self.token = None
        self.session.headers.pop("Authorization", None)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict | list | None:
        """Make an HTTP request and return JSON response."""
        url = f"{API_BASE}{endpoint}"
        try:
            resp = self.session.request(method, url, timeout=30, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            detail = None
            try:
                detail = e.response.json().get("detail")
            except Exception:
                pass
            if isinstance(detail, dict):
                raise Exception(detail.get("message", str(e)))
            elif isinstance(detail, str):
                raise Exception(detail)
            raise Exception(f"HTTP {e.response.status_code}: {str(e)}")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to backend server. Is it running on port 8000?")
        except Exception as e:
            raise Exception(str(e))

    def get(self, endpoint: str, params: dict = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, json: dict = None) -> Any:
        return self._request("POST", endpoint, json=json)

    def put(self, endpoint: str, json: dict = None) -> Any:
        return self._request("PUT", endpoint, json=json)

    def delete(self, endpoint: str) -> Any:
        return self._request("DELETE", endpoint)

    # ── Auth ──────────────────────────────────────────────
    def login(self, email: str, password: str) -> dict:
        return self.post("/api/auth/login", {"email": email, "password": password})

    def register(self, name: str, email: str, password: str, student_id: str = None) -> dict:
        data = {"name": name, "email": email, "password": password}
        if student_id:
            data["student_id"] = student_id
        return self.post("/api/auth/register", data)

    def get_profile(self) -> dict:
        return self.get("/api/auth/me")

    # ── Books ─────────────────────────────────────────────
    def list_books(self, q: str = None, category_id: int = None, available_only: bool = False) -> list:
        params = {}
        if q:
            params["q"] = q
        if category_id:
            params["category_id"] = category_id
        if available_only:
            params["available_only"] = "true"
        return self.get("/api/books", params=params)

    def get_book(self, book_id: int) -> dict:
        return self.get(f"/api/books/{book_id}")

    # ── Categories ────────────────────────────────────────
    def list_categories(self) -> list:
        return self.get("/api/categories")

    # ── Circulation ───────────────────────────────────────
    def borrow_book(self, book_copy_id: int) -> dict:
        return self.post("/api/borrow", {"book_copy_id": book_copy_id})

    def return_book(self, record_id: int) -> dict:
        return self.post(f"/api/borrow/{record_id}/return")

    def renew_book(self, record_id: int) -> dict:
        return self.post(f"/api/borrow/{record_id}/renew")

    def my_borrows(self) -> list:
        return self.get("/api/borrow/my")

    def borrow_history(self) -> list:
        return self.get("/api/borrow/history")

    def all_borrows(self) -> list:
        return self.get("/api/borrow/all")

    def overdue_borrows(self) -> list:
        return self.get("/api/borrow/overdue")

    # ── Reservations ──────────────────────────────────────
    def create_reservation(self, book_id: int) -> dict:
        return self.post("/api/reservations", {"book_id": book_id})

    def my_reservations(self) -> list:
        return self.get("/api/reservations/my")

    def cancel_reservation(self, res_id: int) -> dict:
        return self.delete(f"/api/reservations/{res_id}")

    # ── Fines ─────────────────────────────────────────────
    def my_fines(self) -> list:
        return self.get("/api/fines/my")

    def all_fines(self) -> list:
        return self.get("/api/fines/all")

    def pay_fine(self, fine_id: int) -> dict:
        return self.post(f"/api/fines/{fine_id}/pay")

    # ── Reviews ───────────────────────────────────────────
    def create_review(self, book_id: int, rating: int, review_text: str = "") -> dict:
        data = {"book_id": book_id, "rating": rating}
        if review_text:
            data["review_text"] = review_text
        return self.post("/api/reviews", data)

    def get_reviews(self, book_id: int) -> list:
        return self.get(f"/api/reviews/book/{book_id}")

    # ── Graph ─────────────────────────────────────────────
    def my_graph(self) -> dict:
        return self.get("/api/graph/me")

    def search_graph(self, q: str) -> dict:
        return self.get("/api/graph/search", params={"q": q})

    def book_graph(self, book_id: int) -> dict:
        return self.get(f"/api/graph/book/{book_id}")

    def graph_recommendations(self) -> list:
        return self.get("/api/graph/recommendations")

    # ── Agent ─────────────────────────────────────────────
    def agent_chat(self, message: str, conversation_history: list = None) -> dict:
        data = {"message": message}
        if conversation_history:
            data["conversation_history"] = conversation_history
        return self.post("/api/agent/chat", data)

    # ── Analytics ─────────────────────────────────────────
    def analytics_overview(self) -> dict:
        return self.get("/api/analytics/overview")

    def borrowing_trends(self) -> dict:
        return self.get("/api/analytics/borrowing-trends")

    def popular_categories(self) -> dict:
        return self.get("/api/analytics/popular-categories")

    def most_borrowed(self) -> dict:
        return self.get("/api/analytics/most-borrowed")
