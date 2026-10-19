"""Health check endpoint definition."""

from fastapi import APIRouter, Depends
from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Readiness Check",
    description="Returns current status, version, environment, and capability readiness of RepoSense AI backend.",
)
async def check_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return structured system status."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        phase=settings.phase,
        environment=settings.app_env,
    )
