"""Coverage endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.coverage import CoverageSummary
from app.services.coverage import get_coverage_summary


router = APIRouter(prefix="/coverage", tags=["Coverage"])


@router.get("", response_model=CoverageSummary, summary="Coverage snapshot across jurisdictions")
async def coverage_summary(
    session: AsyncSession | None = Depends(maybe_get_session),
) -> CoverageSummary:
    """Return coverage, ingestion, and trade surveillance health aggregates."""

    return await get_coverage_summary(session=session)
