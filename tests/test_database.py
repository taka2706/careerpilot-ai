"""Development database initialization tests."""

from app.db.base import Base
from app.db.init_db import initialize_database


def test_initialize_database_registers_expected_tables() -> None:
    initialize_database()

    assert {
        "agent_runs",
        "application_drafts",
        "errors",
        "evaluations",
        "job_rankings",
        "jobs",
        "user_profiles",
    }.issubset(Base.metadata.tables)

