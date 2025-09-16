"""Forecast repository helpers."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forecast import ForecastSignal


async def list_sector_forecast(
    session: AsyncSession,
    *,
    sector: str,
    limit: int = 10,
) -> list[ForecastSignal]:
    """Return forecast signals filtered by sector."""

    stmt = (
        select(ForecastSignal)
        .where(ForecastSignal.sector == sector)
        .order_by(ForecastSignal.generated_on.desc(), ForecastSignal.confidence.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())