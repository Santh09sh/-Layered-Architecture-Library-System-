"""
Graph Models
Data structures for the entity graph.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str              # Unique node ID, e.g. "book_1", "author_3"
    label: str           # Display label
    type: str            # Node type: User, Book, Author, Publisher, Category, BookCopy
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str          # Source node ID
    target: str          # Target node ID
    relationship: str    # Edge type: BORROWED, WRITTEN_BY, PUBLISHED_BY, etc.
    properties: Dict[str, Any] = {}


class GraphData(BaseModel):
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []


class GraphSearchResult(BaseModel):
    query: str
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
    paths: List[List[str]] = []
