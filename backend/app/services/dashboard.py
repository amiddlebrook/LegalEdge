"""Dashboard aggregation services."""
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.dashboard import DashboardPayload
from app.services.forecasting import build_sector_forecast
from app.services.legislation import get_upcoming_legislation
from app.services.portfolio import aggregate_signals


async def get_dashboard_snapshot(*, session: AsyncSession | None = None) -> DashboardPayload:
    logger.debug('Assembling dashboard snapshot')
    """Assemble core dashboard data in a single call."""

    upcoming = await get_upcoming_legislation(limit=5, session=session)
    forecast = await build_sector_forecast(sector="Technology", horizon_days=30, session=session)
    signals = await aggregate_signals(limit=5, session=session)
    return DashboardPayload(
        upcoming_legislation=upcoming,
        sector_forecast=forecast,
        portfolio_signals=signals,
    )