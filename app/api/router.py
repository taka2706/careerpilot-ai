"""Top-level API router assembled from small route modules."""

from fastapi import APIRouter

from app.api.routes.agents import router as agents_router
from app.api.routes.agents import run_router
from app.api.routes.applications import router as applications_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.profiles import router as profiles_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(profiles_router)
api_router.include_router(jobs_router)
api_router.include_router(agents_router)
api_router.include_router(run_router)
api_router.include_router(applications_router)
api_router.include_router(evaluations_router)
