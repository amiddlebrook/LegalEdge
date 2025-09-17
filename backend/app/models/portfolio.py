"""SQLAlchemy models for congressional portfolio trades."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TradeDisclosure(TimestampMixin, Base):
    """Financial disclosure by a congressional member."""

    __tablename__ = "trade_disclosures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filing_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(64), default='sec.filings')
    member: Mapped[str] = mapped_column(String(256), index=True)
    chamber: Mapped[str] = mapped_column(String(32), index=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    transaction_type: Mapped[str] = mapped_column(String(32))
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    amount_range: Mapped[str] = mapped_column(String(64))
    related_bill: Mapped[str | None] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"TradeDisclosure(member={self.member!r}, ticker={self.ticker!r})"
