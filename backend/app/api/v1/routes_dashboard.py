"""Dashboard endpoints."""
from fastapi import APIRouter

from app.schemas.dashboard import DashboardPayload
from app.services.dashboard import get_dashboard_snapshot


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/snapshot", response_model=DashboardPayload, summary="Investor dashboard snapshot")
async def dashboard_snapshot() -> DashboardPayload:
    """Return upcoming legislation, a featured forecast, and key signals."""

    return await get_dashboard_snapshot()