"""Forecasting schema definitions."""
from datetime import date

from pydantic import BaseModel, Field


class ForecastBreakdown(BaseModel):
    """Explainable insights for each ticker."""

    ticker: str
    thesis: str
    expected_return_pct: float
    confidence: float
    catalysts: list[str]


class ForecastEnvelope(BaseModel):
    """Aggregate forecast output."""

    sector: str
    horizon_days: int
    generated_on: date
    signals: list[ForecastBreakdown]
    estimated_accuracy: float = Field(ge=0.0, le=1.0)
    methodology_summary: str
    drivers: list[str] | None = None
