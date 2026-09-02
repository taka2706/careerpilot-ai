"""Database initialization helpers."""

from app.db import models as _database_models  # noqa: F401
from app.db.base import Base
from app.db.session import engine


def initialize_database() -> None:
    """Create missing development tables without deleting existing data."""

    Base.metadata.create_all(bind=engine)
