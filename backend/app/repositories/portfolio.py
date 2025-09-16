"""Portfolio repository helpers."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import TradeDisclosure


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