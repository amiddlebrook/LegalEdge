"""Legislation endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.legislation import BillImpactProjection, BillImpactRequest, LegislativeBrief
from app.services.legislation import analyze_legislation, get_upcoming_legislation


router = APIRouter(prefix="/legislation", tags=["Legislation"])


@router.get("/upcoming", response_model=list[LegislativeBrief], summary="Upcoming tracked bills")
async def upcoming_bills(
    limit: int = Query(default=5, le=25),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> list[LegislativeBrief]:
    """Expose normalized legislative summaries."""

    return await get_upcoming_legislation(limit=limit, session=session)


@router.post(
    "/analyze",
    response_model=BillImpactProjection,
    summary="Run impact analysis for a bill",
)
async def analyze_bill(payload: BillImpactRequest) -> BillImpactProjection:
    """Trigger the AI forecasting workflow for a bill."""

    return await analyze_legislation(payload)