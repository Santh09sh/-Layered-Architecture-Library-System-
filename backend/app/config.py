"""
Application Configuration
Centralized configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Library Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./library.db"

    # JWT Authentication
    SECRET_KEY: str = "super-secret-key-change-in-production-09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Library Configuration (Business Rules)
    MAX_BOOKS_PER_STUDENT: int = 5
    MAX_RENEWALS: int = 2
    LOAN_DURATION_DAYS: int = 14
    FINE_PER_DAY: float = 1.0
    MAX_FINE_THRESHOLD: float = 50.0
    RESERVATION_EXPIRY_HOURS: int = 48

    # AI Configuration
    GEMINI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "gemini"  # Options: gemini, mock
    LLM_MODEL: str = "gemini-2.0-flash"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8501"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
