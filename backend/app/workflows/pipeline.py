"""Workflow orchestrators for ingestion and predictions."""
from collections.abc import Callable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.schemas.legislation import BillImpactRequest
from app.services.forecasting import build_sector_forecast
from app.services.legislation import analyze_legislation, get_upcoming_legislation
from app.services.portfolio import aggregate_signals


async def run_daily_ingestion(
    session: AsyncSession | None = None,
    *,
    session_factory: async_sessionmaker[AsyncSession] | Callable[[], AsyncSession] | None = None,
) -> None:
    """Execute ingestion pipelines, preferring a DB session when available."""

    async def _ingest(active_session: AsyncSession | None) -> None:
        logger.info('Starting ingestion pipelines for Congress and legislation feeds')
        if active_session is not None:
            bills = await get_upcoming_legislation(limit=5, session=active_session)
            logger.debug('Ingestion warm-up retrieved %s bills', len(bills))
        else:
            await get_upcoming_legislation(limit=5)

    if session is not None:
        await _ingest(session)
        return

    if session_factory is not None:
        async_session = session_factory()
        async with async_session as generated_session:
            await _ingest(generated_session)
        return

    await _ingest(None)


async def generate_full_market_snapshot(
    request: BillImpactRequest,
    *,
    session: AsyncSession | None = None,
) -> dict:
    """Combine legislation analysis, forecasts, and portfolio signals."""

    analysis = await analyze_legislation(request)
    sector_forecast = await build_sector_forecast('Technology', session=session)
    signals = await aggregate_signals(limit=5, session=session)

    return {
        'analysis': analysis.model_dump(),
        'sector_forecast': sector_forecast.model_dump(),
        'signals': [signal.model_dump() for signal in signals],
    }