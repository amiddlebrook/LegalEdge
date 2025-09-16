"""Workflow orchestrators for ingestion and predictions."""
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.legislation import BillImpactRequest
from app.services.forecasting import build_sector_forecast
from app.services.legislation import analyze_legislation, get_upcoming_legislation
from app.services.portfolio import aggregate_signals


async def run_daily_ingestion(session: AsyncSession | None = None) -> None:
    """Placeholder orchestration function that will coordinate ETL jobs."""

    logger.info("Starting ingestion pipelines for Congress and legislation feeds")
    if session is not None:
        bills = await get_upcoming_legislation(limit=5, session=session)
        logger.debug("Ingestion warm-up retrieved %s bills", len(bills))
    # TODO: integrate prefect or celery workflows here


async def generate_full_market_snapshot(
    request: BillImpactRequest,
    *,
    session: AsyncSession | None = None,
) -> dict:
    """Combine legislation analysis, forecasts, and portfolio signals."""

    analysis = await analyze_legislation(request)
    sector_forecast = await build_sector_forecast("Technology", session=session)
    signals = await aggregate_signals(limit=5, session=session)

    return {
        "analysis": analysis.model_dump(),
        "sector_forecast": sector_forecast.model_dump(),
        "signals": [signal.model_dump() for signal in signals],
    }