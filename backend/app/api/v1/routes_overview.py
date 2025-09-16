"""Product overview endpoints."""
from fastapi import APIRouter

from app.schemas.overview import OverviewPayload
from app.services.overview import get_product_overview


router = APIRouter(prefix="/overview", tags=["Overview"])


@router.get("", response_model=OverviewPayload, summary="Marketing overview payload")
async def fetch_overview() -> OverviewPayload:
    """Return the structured overview content consumed by the frontend."""

    return await get_product_overview()