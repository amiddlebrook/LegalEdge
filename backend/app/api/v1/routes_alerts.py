"""Alert feed endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.alerts import AlertFeed
from app.services.alerts import get_alert_feed


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertFeed, summary="Latest policy alerts")
async def list_alerts(
    limit: int = Query(default=5, ge=1, le=20),
    categories: list[str] | None = Query(default=None, description="Filter by alert categories"),
    severities: list[str] | None = Query(default=None, description="Filter by specific severity levels"),
    min_severity: str | None = Query(default=None, description="Return alerts at or above this severity"),
    entity: str | None = Query(default=None, description="Filter alerts mentioning a specific entity or ticker"),
    since_minutes: int | None = Query(default=None, ge=5, le=1440, description="Only include alerts raised within the past N minutes"),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> AlertFeed:
    """Return prioritized alerts for investors."""

    return await get_alert_feed(
        limit=limit,
        session=session,
        categories=categories,
        severities=severities,
        min_severity=min_severity,
        entity=entity,
        since_minutes=since_minutes,
    )
