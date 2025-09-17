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
    session: AsyncSession | None = Depends(maybe_get_session),
) -> OpportunityPayload:
    """Return AI-derived opportunity recommendations."""

    return await get_market_opportunities(limit=limit, session=session)