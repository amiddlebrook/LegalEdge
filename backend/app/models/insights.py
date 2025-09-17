"""SQLAlchemy models for alerts and opportunities."""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PolicyAlert(TimestampMixin, Base):
    """Persistent alert surfaced to investors."""

    __tablename__ = "policy_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    related_entities: Mapped[List[str]] = mapped_column(JSON, default=list)


class OpportunityRecommendation(TimestampMixin, Base):
    """Persistent market opportunity recommendation."""

    __tablename__ = "opportunity_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    thesis: Mapped[str] = mapped_column(String)
    expected_return_pct: Mapped[float] = mapped_column(Float)
    conviction: Mapped[float] = mapped_column(Float)
    horizon_days: Mapped[int] = mapped_column()
    catalysts: Mapped[List[str]] = mapped_column(JSON, default=list)
    risk_rating: Mapped[str] = mapped_column(String(32))