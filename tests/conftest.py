"""Shared test fixtures."""

import pytest
from fastapi import FastAPI

from app.main import app


@pytest.fixture
def api_app() -> FastAPI:
    """Provide the configured ASGI application."""

    return app
