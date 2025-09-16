"""Dashboard schema definitions."""
from pydantic import BaseModel

from app.schemas.forecast import ForecastEnvelope
from app.schemas.legislation import LegislativeBrief
from app.schemas.portfolio import PortfolioSignal


class DashboardPayload(BaseModel):
    """Aggregate payload for the investor dashboard."""

    upcoming_legislation: list[LegislativeBrief]
    sector_forecast: ForecastEnvelope
    portfolio_signals: list[PortfolioSignal]