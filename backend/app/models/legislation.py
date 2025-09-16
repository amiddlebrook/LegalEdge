"""SQLAlchemy models for legislative data."""
from __future__ import annotations

from datetime import date, datetime
from typing import List

from sqlalchemy import Date, DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LegislativeBill(TimestampMixin, Base):
    """Normalized legislative artifact."""

    __tablename__ = "legislative_bills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bill_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    stage: Mapped[str] = mapped_column(String(128))
    jurisdiction: Mapped[str] = mapped_column(String(128), index=True)
    committees: Mapped[List[str]] = mapped_column(JSON, default=list)
    sectors: Mapped[List[str]] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(String)
    next_action_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    probability_of_enactment: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    def __repr__(self) -> str:
        return f"LegislativeBill(bill_id={self.bill_id!r}, stage={self.stage!r})"