"""Entity resolution endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.entity_resolution import EntityResolutionSummary
from app.services.entity_resolution import build_entity_resolution_summary


router = APIRouter(prefix="/entity-resolution", tags=["Entity Resolution"])


@router.get("/summary", response_model=EntityResolutionSummary, summary="Entity resolution coverage and metrics")
async def get_entity_resolution_summary(session: AsyncSession | None = Depends(maybe_get_session)) -> EntityResolutionSummary:
    """Expose consolidated entity resolution coverage."""

    return await build_entity_resolution_summary(session=session)
