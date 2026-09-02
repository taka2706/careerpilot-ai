"""Create all configured database tables without deleting existing data."""

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.init_db import initialize_database


def main() -> None:
    """Initialize the database using the configured DATABASE_URL."""

    settings = get_settings()
    configure_logging(settings.log_level)
    initialize_database()
    get_logger(__name__).info("Database tables are ready")


if __name__ == "__main__":
    main()
