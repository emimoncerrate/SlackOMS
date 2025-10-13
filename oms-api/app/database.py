"""
Database configuration and session management
Uses SQLAlchemy with PostgreSQL or SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Configure engine based on database type
if settings.database_url.startswith("sqlite"):
    # SQLite configuration (for local development)
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=settings.debug
    )
else:
    # PostgreSQL configuration (for production)
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10,
        echo=settings.debug  # Log SQL queries in debug mode
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database sessions in FastAPI endpoints
    Ensures proper cleanup after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    # Import models to register them with Base
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

