"""
ReOrder AI — Database engine and session management.
Provides both a context-manager (for pipeline/background jobs)
and a FastAPI dependency (for request-scoped sessions).
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import get_settings
from src.db.models import Base


_engine = None
_SessionLocal = None


def get_engine():
    """Return the global SQLAlchemy engine (creates on first use)."""
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        # SQLite needs check_same_thread=False for FastAPI's thread pool
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(
            settings.database_url,
            echo=settings.log_level.upper() == "DEBUG",
            future=True,
            connect_args=connect_args,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return the session factory (creates on first use)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


# ── Context manager (pipeline / background jobs) ─────────────


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for a single DB session (auto-commit on success)."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ── FastAPI dependency ────────────────────────────────────────


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a request-scoped DB session.

    Usage:
        @app.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    factory = get_session_factory()
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Table creation ────────────────────────────────────────────


def init_db() -> None:
    """Create all tables if they do not exist."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
