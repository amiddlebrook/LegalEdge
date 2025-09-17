"""Market opportunities endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.opportunity import OpportunityPayload
from app.services.opportunities import get_market_opportunities


router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("", response_model=OpportunityPayload, summary="Curated market opportunities")
async def list_opportunities(
    limit: int = Query(default=5, ge=1, le=10),
    risk_ratings: list[str] | None = Query(default=None, description="Filter by risk ratings"),
    min_conviction: float | None = Query(default=None, ge=0.0, le=1.0, description="Minimum conviction score"),
    max_horizon_days: int | None = Query(default=None, ge=1, description="Maximum horizon in days"),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> OpportunityPayload:
    """Return AI-derived opportunity recommendations."""

    return await get_market_opportunities(
        limit=limit,
        session=session,
        risk_ratings=risk_ratings,
        min_conviction=min_conviction,
        max_horizon_days=max_horizon_days,
    )
