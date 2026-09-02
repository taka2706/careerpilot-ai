"""Database initialization helpers."""

from app.db.base import Base
from app.db.session import engine
from app.models import database as _database_models  # noqa: F401


def initialize_database() -> None:
    """Create missing development tables without deleting existing data."""

    Base.metadata.create_all(bind=engine)

