from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import os

# SQLite database URL
DATABASE_URL = "sqlite:///./tvtracker.db"

# Create engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)


@contextmanager
def SessionLocal():
    """Context manager for database sessions"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)
