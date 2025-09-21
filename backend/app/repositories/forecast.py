"""Forecast repository helpers."""
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forecast import ForecastSignal


async def list_sector_forecast(
    session: AsyncSession,
    *,
    sector: str,
    limit: int = 10,
    ticker: str | None = None,
    min_confidence: float | None = None,
    since_date: date | None = None,
) -> list[ForecastSignal]:
    """Return forecast signals filtered by sector and optional parameters."""
    stmt = select(ForecastSignal).where(ForecastSignal.sector == sector)

    if ticker:
        stmt = stmt.where(ForecastSignal.ticker == ticker)
    if min_confidence is not None:
        stmt = stmt.where(ForecastSignal.confidence >= min_confidence)
    if since_date:
        stmt = stmt.where(ForecastSignal.generated_on >= since_date)

    stmt = stmt.order_by(
        ForecastSignal.generated_on.desc(),
        ForecastSignal.confidence.desc()
    ).limit(limit)

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_forecast_signal(
    session: AsyncSession,
    *,
    signal_id: int,
) -> ForecastSignal | None:
    """Get a specific forecast signal by ID."""
    stmt = select(ForecastSignal).where(ForecastSignal.id == signal_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_forecast_signals_by_ticker(
    session: AsyncSession,
    *,
    ticker: str,
    limit: int = 10,
    sector: str | None = None,
) -> list[ForecastSignal]:
    """Get forecast signals for a specific ticker."""
    stmt = select(ForecastSignal).where(ForecastSignal.ticker == ticker)

    if sector:
        stmt = stmt.where(ForecastSignal.sector == sector)

    stmt = stmt.order_by(ForecastSignal.generated_on.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_forecast_signal(
    session: AsyncSession,
    *,
    sector: str,
    ticker: str,
    thesis: str,
    expected_return_pct: float,
    confidence: float,
    catalysts: List[str],
    horizon_days: int = 30,
    generated_on: date,
) -> ForecastSignal:
    """Create a new forecast signal."""
    signal = ForecastSignal(
        sector=sector,
        ticker=ticker,
        thesis=thesis,
        expected_return_pct=expected_return_pct,
        confidence=confidence,
        catalysts=catalysts,
        horizon_days=horizon_days,
        generated_on=generated_on,
    )
    session.add(signal)
    await session.flush()
    await session.refresh(signal)
    return signal


async def update_forecast_signal(
    session: AsyncSession,
    *,
    signal_id: int,
    **updates,
) -> ForecastSignal | None:
    """Update an existing forecast signal."""
    stmt = (
        update(ForecastSignal)
        .where(ForecastSignal.id == signal_id)
        .values(**updates, updated_at=datetime.now(timezone.utc))
    )
    result = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return await get_forecast_signal(session, signal_id=signal_id)
    return None


async def delete_forecast_signal(
    session: AsyncSession,
    *,
    signal_id: int,
) -> bool:
    """Delete a forecast signal."""
    stmt = delete(ForecastSignal).where(ForecastSignal.id == signal_id)
    result = await session.execute(stmt)
    return result.rowcount > 0


async def bulk_upsert_forecast_signals(
    session: AsyncSession,
    *,
    signals: List[dict],
) -> List[ForecastSignal]:
    """Bulk upsert forecast signals."""
    created_signals = []
    for signal_data in signals:
        # Check if signal exists for this sector/ticker/date
        existing = await session.execute(
            select(ForecastSignal).where(
                and_(
                    ForecastSignal.sector == signal_data['sector'],
                    ForecastSignal.ticker == signal_data['ticker'],
                    ForecastSignal.generated_on == signal_data['generated_on'],
                )
            )
        )
        existing_signal = existing.scalar_one_or_none()

        if existing_signal:
            # Update existing signal
            signal = await update_forecast_signal(
                session, signal_id=existing_signal.id, **signal_data
            )
        else:
            # Create new signal
            signal = await create_forecast_signal(session, **signal_data)
        created_signals.append(signal)
    return created_signals


async def get_latest_forecast_date(
    session: AsyncSession,
    *,
    sector: str | None = None,
) -> date | None:
    """Get the latest forecast generation date."""
    stmt = select(func.max(ForecastSignal.generated_on))

    if sector:
        stmt = stmt.where(ForecastSignal.sector == sector)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_forecast_stats(
    session: AsyncSession,
    *,
    sector: str | None = None,
) -> dict:
    """Get statistics about forecast signals."""
    stmt = select(
        func.count(ForecastSignal.id).label('total_signals'),
        func.count(func.distinct(ForecastSignal.ticker)).label('unique_tickers'),
        func.avg(ForecastSignal.confidence).label('avg_confidence'),
        func.avg(ForecastSignal.expected_return_pct).label('avg_expected_return'),
        func.max(ForecastSignal.generated_on).label('latest_date'),
    )

    if sector:
        stmt = stmt.where(ForecastSignal.sector == sector)

    result = await session.execute(stmt)
    row = result.first()

    return {
        'total_signals': row.total_signals or 0,
        'unique_tickers': row.unique_tickers or 0,
        'avg_confidence': float(row.avg_confidence or 0),
        'avg_expected_return': float(row.avg_expected_return or 0),
        'latest_date': row.latest_date,
    }