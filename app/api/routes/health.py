"""Service health route."""

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Confirm that the API process is running and configuration loaded."""

    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=__version__,
        environment=settings.app_env,
    )

