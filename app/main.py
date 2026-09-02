"""CareerPilot AI FastAPI entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.db.init_db import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize resources required by the development application."""

    initialize_database()
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        description="API for the CareerPilot AI job-search workflow.",
        version=__version__,
        debug=settings.debug,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    return application


app = create_app()

