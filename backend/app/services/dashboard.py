"""Dashboard aggregation services."""
from loguru import logger

from app.schemas.dashboard import DashboardPayload
from app.services.forecasting import build_sector_forecast
from app.services.legislation import get_upcoming_legislation
from app.services.portfolio import aggregate_signals


async def get_dashboard_snapshot() -> DashboardPayload:
    logger.debug('Assembling dashboard snapshot')
    """Assemble core dashboard data in a single call."""

    upcoming = await get_upcoming_legislation(limit=5)
    forecast = await build_sector_forecast(sector="Technology", horizon_days=30)
    signals = await aggregate_signals(limit=5)
    return DashboardPayload(
        upcoming_legislation=upcoming,
        sector_forecast=forecast,
        portfolio_signals=signals,
    )