"""Shared test fixtures."""

import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db import models as _models  # noqa: F401
from app.db.base import Base
from app.main import app


@pytest.fixture
def api_app() -> FastAPI:
    """Provide the configured ASGI application."""

    return app


@pytest.fixture
def test_settings(tmp_path) -> Settings:  # type: ignore[no-untyped-def]
    return Settings(
        _env_file=None,
        database_url="sqlite://",
        rag_storage_path=tmp_path / "rag",
        debug=False,
    )


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()
