"""
FastAPI Application Entry Point
Main application setup with all routes, middleware, and CORS.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.application.middleware.error_handler import ErrorHandlerMiddleware
from app.application.routes import auth, books, circulation, graph, agent, analytics

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Library Management System with Entity Graph and AI Agent",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
app.add_middleware(ErrorHandlerMiddleware)

# Register routes
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(circulation.router)
app.include_router(graph.router)
app.include_router(agent.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}
