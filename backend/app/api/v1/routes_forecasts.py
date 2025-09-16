"""Forecast endpoints."""
from fastapi import APIRouter, Query

from app.schemas.forecast import ForecastEnvelope
from app.services.forecasting import build_sector_forecast


router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@router.get("/sector", response_model=ForecastEnvelope, summary="Sector level forecast")
async def sector_forecast(
    sector: str = Query(default="Technology"),
    horizon_days: int = Query(default=30, ge=7, le=180),
) -> ForecastEnvelope:
    """Return aggregated forecast data for a sector."""

    return await build_sector_forecast(sector=sector, horizon_days=horizon_days)