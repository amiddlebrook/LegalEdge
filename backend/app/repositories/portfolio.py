"""Portfolio repository helpers."""
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import TradeDisclosure
from app.models.legislation import LegislativeBill


async def list_recent_trades(
    session: AsyncSession,
    *,
    limit: int = 10,
) -> list[TradeDisclosure]:
    """Return recent trade disclosures."""

    stmt = (
        select(TradeDisclosure)
        .order_by(TradeDisclosure.transaction_date.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_trade_disclosures_with_bills(
    session: AsyncSession,
    *,
    limit: int = 20,
    since: datetime | None = None,
) -> list[tuple[TradeDisclosure, LegislativeBill | None]]:
    """Return recent trade disclosures alongside related legislation when available."""

    stmt = select(TradeDisclosure, LegislativeBill).join(
        LegislativeBill, TradeDisclosure.related_bill == LegislativeBill.bill_id, isouter=True
    ).order_by(TradeDisclosure.transaction_date.desc(), TradeDisclosure.id.desc()).limit(limit)
    if since is not None:
        stmt = stmt.where(TradeDisclosure.transaction_date >= since)
    result = await session.execute(stmt)
    return list(result.all())
