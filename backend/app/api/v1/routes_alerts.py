"""Alert feed endpoints."""
from fastapi import APIRouter, Query

from app.schemas.alerts import AlertFeed
from app.services.alerts import get_alert_feed


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertFeed, summary="Latest policy alerts")
async def list_alerts(limit: int = Query(default=5, ge=1, le=20)) -> AlertFeed:
    """Return prioritized alerts for investors."""

    return await get_alert_feed(limit=limit)