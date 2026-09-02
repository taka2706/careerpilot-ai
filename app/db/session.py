"""Database engine and request-scoped session dependency."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _ensure_sqlite_directory(database_url: str) -> None:
    """Create the parent directory for a relative SQLite database file."""

    prefix = "sqlite:///"
    if database_url.startswith(prefix) and database_url != "sqlite:///:memory:":
        database_path = Path(database_url.removeprefix(prefix))
        database_path.parent.mkdir(parents=True, exist_ok=True)


settings = get_settings()
_ensure_sqlite_directory(settings.database_url)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine: Engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session and always close it after the request."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

