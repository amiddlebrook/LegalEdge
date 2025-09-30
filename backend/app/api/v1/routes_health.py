"""Health and metadata endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db


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
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:
    """Check service readiness with database connectivity."""

    try:
        # Test database connectivity
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ready" if db_status == "healthy" else "not_ready",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }