"""SQLAlchemy models for forecast data."""
from __future__ import annotations

from datetime import date
from typing import List

from sqlalchemy import Date, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ForecastSignal(TimestampMixin, Base):
    """Predicted movement for a ticker within a sector horizon."""

    __tablename__ = "forecast_signals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sector: Mapped[str] = mapped_column(String(128), index=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    thesis: Mapped[str] = mapped_column(String)
    expected_return_pct: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    catalysts: Mapped[List[str]] = mapped_column(JSON, default=list)
    horizon_days: Mapped[int] = mapped_column(Integer, default=30)
    generated_on: Mapped[date] = mapped_column(Date, index=True)

    def __repr__(self) -> str:
        return f"ForecastSignal(ticker={self.ticker!r}, sector={self.sector!r})"