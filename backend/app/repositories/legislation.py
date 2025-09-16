"""Legislation repository helpers."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legislation import LegislativeBill


async def list_upcoming_legislation(
    session: AsyncSession,
    *,
    limit: int = 5,
) -> list[LegislativeBill]:
    """Return upcoming legislation ordered by next action date."""

    stmt = (
        select(LegislativeBill)
        .order_by(LegislativeBill.next_action_date.asc(), LegislativeBill.last_updated.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())