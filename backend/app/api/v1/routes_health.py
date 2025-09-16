"""Health and metadata endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/status", summary="Service liveness probe")
def health_status() -> dict[str, str]:
    """Expose liveness data for monitoring."""

    return {
        "status": "ok",
        "service": settings.app_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.environment,
    }


@router.get("/readiness", summary="Service readiness probe")
def readiness() -> dict[str, str]:
    """Placeholder readiness handler until database wiring is complete."""

    return {
        "status": "initializing",
        "dependencies": "database, ai_engine",
    }