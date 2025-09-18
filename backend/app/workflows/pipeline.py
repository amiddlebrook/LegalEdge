"""Workflow orchestrators for ingestion and predictions."""
from collections.abc import Callable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.ml.legislation_pipeline import get_pipeline
from app.schemas.legislation import BillImpactRequest
from app.services.forecasting import build_sector_forecast
from app.services.legislation import analyze_legislation, get_upcoming_legislation
from app.services.portfolio import aggregate_signals
from app.ingestion import IngestionManager, get_default_connectors, persist_batches


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

        manager = IngestionManager(get_default_connectors())
        enqueued = await manager.poll_once()
        if enqueued:
            batches = await manager.drain_batches()
            logger.info('Ingestion connectors queued %s artifacts across %s sources', enqueued, len(batches))
            if active_session is not None:
                summary = await persist_batches(batches, session=active_session)
                if summary.total_persisted:
                    logger.info('Normalized %s legislative artifacts (%s created, %s updated)', summary.legislation_processed, summary.created, summary.updated)
                else:
                    logger.debug('No legislative updates detected during connector persistence')

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


async def retrain_legislation_models() -> None:
    """Trigger scheduled retraining of NLP artifacts."""

    pipeline = get_pipeline()
    await pipeline.retrain()
