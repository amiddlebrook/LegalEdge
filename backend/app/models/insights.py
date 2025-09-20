"""SQLAlchemy models for alerts and opportunities."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from sqlalchemy import Boolean, DateTime, Float, JSON, String
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
    raised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
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


class AlertSubscription(TimestampMixin, Base):
    """Configurable alert subscription with delivery channels."""

    __tablename__ = "alert_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscriber_id: Mapped[str] = mapped_column(String(128), index=True)
    label: Mapped[str] = mapped_column(String(128))
    categories: Mapped[List[str]] = mapped_column(JSON, default=list)
    entities: Mapped[List[str]] = mapped_column(JSON, default=list)
    severities: Mapped[List[str]] = mapped_column(JSON, default=list)
    min_severity: Mapped[str | None] = mapped_column(String(32), nullable=True)
    channels: Mapped[List[Dict[str, str]]] = mapped_column(JSON, default=list)
    delivery_window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mute_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


