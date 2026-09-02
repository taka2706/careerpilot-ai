"""CareerPilot AI FastAPI entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.init_db import initialize_database
from app.schemas.common import ErrorDetail, ErrorResponse

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize resources required by the development application."""

    initialize_database()
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

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
    application.include_router(api_router)

    @application.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Normalize intentional HTTP failures into the public error format."""

        message = (
            exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
        )
        payload = ErrorResponse(error=ErrorDetail(code="http_error", message=message))
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        """Return validation failures without echoing potentially sensitive input."""

        logger.info("Request validation failed with %d issue(s)", len(exc.errors()))
        payload = ErrorResponse(
            error=ErrorDetail(code="validation_error", message="Request validation failed.")
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @application.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        """Log unexpected errors and return a safe production response."""

        logger.exception(
            "Unhandled error while processing %s %s: %s",
            request.method,
            request.url.path,
            type(exc).__name__,
        )
        payload = ErrorResponse(
            error=ErrorDetail(code="internal_error", message="An unexpected error occurred.")
        )
        return JSONResponse(status_code=500, content=payload.model_dump())

    return application


app = create_app()
