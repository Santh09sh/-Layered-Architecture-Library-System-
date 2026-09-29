"""
Graph Routes
Entity graph visualization and search endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.graph.graph_service import GraphService
from app.graph.models import GraphData, GraphSearchResult
from app.application.dependencies import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/api/graph", tags=["Entity Graph"])


@router.get("/book/{book_id}", response_model=GraphData)
async def get_book_graph(book_id: int, db: Session = Depends(get_db)):
    service = GraphService(db)
    return service.get_book_graph(book_id)


@router.get("/user/{user_id}", response_model=GraphData)
async def get_user_graph(
    user_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GraphService(db)
    return service.get_user_graph(user_id)


@router.get("/me", response_model=GraphData)
async def get_my_graph(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GraphService(db)
    return service.get_user_graph(current_user.id)


@router.get("/search", response_model=GraphSearchResult)
async def search_graph(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
):
    service = GraphService(db)
    return service.search_graph(q)


@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GraphService(db)
    recs = service.get_recommendations(current_user.id)
    return {
        "recommendations": [
            {
                "book_id": r["book"].id,
                "title": r["book"].title,
                "authors": [a.name for a in r["book"].authors],
                "reason": r["reason"],
                "rating": r.get("score", 0),
            }
            for r in recs
        ]
    }
