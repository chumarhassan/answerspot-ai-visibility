"""SQLAlchemy engine/session wiring.

Defaults to local SQLite for zero-setup dev; point DATABASE_URL at Postgres for prod
and nothing else changes (the models are plain relational SQLAlchemy).
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_settings

settings = get_settings()

# check_same_thread is a SQLite-only quirk; harmless to omit for Postgres.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they don't exist. Called on app startup."""
    import models  # noqa: F401  (ensure models are registered on Base)

    Base.metadata.create_all(bind=engine)
