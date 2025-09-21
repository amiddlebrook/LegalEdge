"""Portfolio repository helpers."""
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.portfolio import TradeDisclosure
from app.models.legislation import LegislativeBill


async def list_recent_trades(
    session: AsyncSession,
    *,
    limit: int = 10,
    member: str | None = None,
    chamber: str | None = None,
    ticker: str | None = None,
    since_date: datetime | None = None,
) -> list[TradeDisclosure]:
    """Return recent trade disclosures with optional filters."""
    stmt = select(TradeDisclosure)

    if member:
        stmt = stmt.where(TradeDisclosure.member == member)
    if chamber:
        stmt = stmt.where(TradeDisclosure.chamber == chamber)
    if ticker:
        stmt = stmt.where(TradeDisclosure.ticker == ticker)
    if since_date:
        stmt = stmt.where(TradeDisclosure.transaction_date >= since_date)

    stmt = stmt.order_by(TradeDisclosure.transaction_date.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_trade_disclosures_with_bills(
    session: AsyncSession,
    *,
    limit: int = 20,
    since: datetime | None = None,
    member: str | None = None,
    chamber: str | None = None,
    ticker: str | None = None,
) -> list[tuple[TradeDisclosure, LegislativeBill | None]]:
    """Return recent trade disclosures alongside related legislation."""
    stmt = select(TradeDisclosure, LegislativeBill).join(
        LegislativeBill, TradeDisclosure.related_bill == LegislativeBill.bill_id, isouter=True
    )

    if since is not None:
        stmt = stmt.where(TradeDisclosure.transaction_date >= since)
    if member:
        stmt = stmt.where(TradeDisclosure.member == member)
    if chamber:
        stmt = stmt.where(TradeDisclosure.chamber == chamber)
    if ticker:
        stmt = stmt.where(TradeDisclosure.ticker == ticker)

    stmt = stmt.order_by(
        TradeDisclosure.transaction_date.desc(),
        TradeDisclosure.id.desc()
    ).limit(limit)
    result = await session.execute(stmt)
    return list(result.all())


async def get_trade_disclosure(
    session: AsyncSession,
    *,
    disclosure_id: int,
) -> TradeDisclosure | None:
    """Get a specific trade disclosure by ID."""
    stmt = select(TradeDisclosure).where(TradeDisclosure.id == disclosure_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_trade_disclosure_by_key(
    session: AsyncSession,
    *,
    member: str,
    ticker: str,
    transaction_date: datetime,
) -> TradeDisclosure | None:
    """Get a trade disclosure by unique key combination."""
    stmt = select(TradeDisclosure).where(
        and_(
            TradeDisclosure.member == member,
            TradeDisclosure.ticker == ticker,
            TradeDisclosure.transaction_date == transaction_date,
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_trade_disclosure(
    session: AsyncSession,
    *,
    member: str,
    chamber: str,
    ticker: str,
    transaction_type: str,
    transaction_date: datetime,
    amount_range: str,
    related_bill: str | None = None,
) -> TradeDisclosure:
    """Create a new trade disclosure."""
    disclosure = TradeDisclosure(
        member=member,
        chamber=chamber,
        ticker=ticker,
        transaction_type=transaction_type,
        transaction_date=transaction_date,
        amount_range=amount_range,
        related_bill=related_bill,
    )
    session.add(disclosure)
    await session.flush()
    await session.refresh(disclosure)
    return disclosure


async def update_trade_disclosure(
    session: AsyncSession,
    *,
    disclosure_id: int,
    **updates,
) -> TradeDisclosure | None:
    """Update an existing trade disclosure."""
    stmt = (
        update(TradeDisclosure)
        .where(TradeDisclosure.id == disclosure_id)
        .values(**updates, updated_at=datetime.now(timezone.utc))
    )
    result = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return await get_trade_disclosure(session, disclosure_id=disclosure_id)
    return None


async def delete_trade_disclosure(
    session: AsyncSession,
    *,
    disclosure_id: int,
) -> bool:
    """Delete a trade disclosure."""
    stmt = delete(TradeDisclosure).where(TradeDisclosure.id == disclosure_id)
    result = await session.execute(stmt)
    return result.rowcount > 0


async def bulk_upsert_trade_disclosures(
    session: AsyncSession,
    *,
    disclosures: List[dict],
) -> List[TradeDisclosure]:
    """Bulk upsert trade disclosures."""
    created_disclosures = []
    for disclosure_data in disclosures:
        # Check if disclosure exists by unique key
        existing = await get_trade_disclosure_by_key(
            session,
            member=disclosure_data['member'],
            ticker=disclosure_data['ticker'],
            transaction_date=disclosure_data['transaction_date'],
        )

        if existing:
            # Update existing disclosure
            disclosure = await update_trade_disclosure(
                session, disclosure_id=existing.id, **disclosure_data
            )
        else:
            # Create new disclosure
            disclosure = await create_trade_disclosure(session, **disclosure_data)
        created_disclosures.append(disclosure)
    return created_disclosures


async def get_trades_by_member(
    session: AsyncSession,
    *,
    member: str,
    limit: int = 50,
    since: datetime | None = None,
) -> list[TradeDisclosure]:
    """Get all trades for a specific member."""
    stmt = select(TradeDisclosure).where(TradeDisclosure.member == member)

    if since:
        stmt = stmt.where(TradeDisclosure.transaction_date >= since)

    stmt = stmt.order_by(TradeDisclosure.transaction_date.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_trades_by_ticker(
    session: AsyncSession,
    *,
    ticker: str,
    limit: int = 50,
    since: datetime | None = None,
) -> list[TradeDisclosure]:
    """Get all trades for a specific ticker."""
    stmt = select(TradeDisclosure).where(TradeDisclosure.ticker == ticker)

    if since:
        stmt = stmt.where(TradeDisclosure.transaction_date >= since)

    stmt = stmt.order_by(TradeDisclosure.transaction_date.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_portfolio_conflicts(
    session: AsyncSession,
    *,
    limit: int = 10,
    min_amount_range: str | None = None,
) -> list[dict]:
    """Get potential portfolio conflicts from trade disclosures."""
    # This is a simplified implementation - in reality you'd want more complex logic
    stmt = select(
        TradeDisclosure.member,
        TradeDisclosure.ticker,
        func.count(TradeDisclosure.id).label('trade_count'),
        func.max(TradeDisclosure.transaction_date).label('latest_trade'),
    ).group_by(TradeDisclosure.member, TradeDisclosure.ticker)

    if min_amount_range:
        stmt = stmt.where(TradeDisclosure.amount_range == min_amount_range)

    stmt = stmt.order_by(func.count(TradeDisclosure.id).desc()).limit(limit)
    result = await session.execute(stmt)
    return [
        {
            'member': row.member,
            'ticker': row.ticker,
            'trade_count': row.trade_count,
            'latest_trade': row.latest_trade,
        }
        for row in result.all()
    ]


async def get_trade_stats(
    session: AsyncSession,
    *,
    since: datetime | None = None,
) -> dict:
    """Get statistics about trade disclosures."""
    stmt = select(
        func.count(TradeDisclosure.id).label('total_trades'),
        func.count(func.distinct(TradeDisclosure.member)).label('unique_members'),
        func.count(func.distinct(TradeDisclosure.ticker)).label('unique_tickers'),
        func.count(func.distinct(TradeDisclosure.chamber)).label('chambers'),
        func.max(TradeDisclosure.transaction_date).label('latest_trade'),
    )

    if since:
        stmt = stmt.where(TradeDisclosure.transaction_date >= since)

    result = await session.execute(stmt)
    row = result.first()

    return {
        'total_trades': row.total_trades or 0,
        'unique_members': row.unique_members or 0,
        'unique_tickers': row.unique_tickers or 0,
        'chambers': row.chambers or 0,
        'latest_trade': row.latest_trade,
    }
