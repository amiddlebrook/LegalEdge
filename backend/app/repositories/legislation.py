"""Legislation repository helpers."""
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.legislation import LegislativeBill, LegislativeBillVersion
from app.utils.cache import cached, cache_invalidate, make_cache_key


async def list_upcoming_legislation(
    session: AsyncSession,
    *,
    limit: int = 5,
    jurisdiction: str | None = None,
    stage: str | None = None,
    sectors: List[str] | None = None,
    committees: List[str] | None = None,
    since_date: date | None = None,
) -> list[LegislativeBill]:
    """Return upcoming legislation with optional filters."""
    stmt = select(LegislativeBill)

    if jurisdiction:
        stmt = stmt.where(LegislativeBill.jurisdiction == jurisdiction)
    if stage:
        stmt = stmt.where(LegislativeBill.stage == stage)
    if sectors:
        stmt = stmt.where(or_(*[LegislativeBill.sectors.contains([sector]) for sector in sectors]))
    if committees:
        stmt = stmt.where(or_(*[LegislativeBill.committees.contains([committee]) for committee in committees]))
    if since_date:
        stmt = stmt.where(LegislativeBill.last_updated >= since_date)

    stmt = stmt.order_by(
        LegislativeBill.next_action_date.asc(),
        LegislativeBill.last_updated.desc()
    ).limit(limit)

    result = await session.execute(stmt)
    return list(result.scalars().all())


@cached(ttl=timedelta(minutes=15), key_prefix="legislation")
async def list_upcoming_legislation_cached(
    session: AsyncSession,
    *,
    limit: int = 5,
    jurisdiction: str | None = None,
    stage: str | None = None,
    sectors: List[str] | None = None,
    committees: List[str] | None = None,
    since_date: date | None = None,
) -> list[LegislativeBill]:
    """Cached version of list_upcoming_legislation."""
    return await list_upcoming_legislation(
        session,
        limit=limit,
        jurisdiction=jurisdiction,
        stage=stage,
        sectors=sectors,
        committees=committees,
        since_date=since_date,
    )


async def get_legislative_bill(
    session: AsyncSession,
    *,
    bill_id: str,
) -> LegislativeBill | None:
    """Get a specific legislative bill by ID."""
    stmt = select(LegislativeBill).where(LegislativeBill.bill_id == bill_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


@cached(ttl=timedelta(minutes=30), key_prefix="legislation")
async def get_legislative_bill_cached(
    session: AsyncSession,
    *,
    bill_id: str,
) -> LegislativeBill | None:
    """Cached version of get_legislative_bill."""
    return await get_legislative_bill(session, bill_id=bill_id)


async def get_legislative_bills_by_sector(
    session: AsyncSession,
    *,
    sector: str,
    limit: int = 20,
    min_confidence: float | None = None,
) -> list[LegislativeBill]:
    """Get legislative bills filtered by sector."""
    stmt = select(LegislativeBill).where(
        LegislativeBill.sectors.contains([sector])
    )

    if min_confidence is not None:
        stmt = stmt.where(LegislativeBill.probability_of_enactment >= min_confidence)

    stmt = stmt.order_by(LegislativeBill.last_updated.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@cached(ttl=timedelta(minutes=15), key_prefix="legislation")
async def get_legislative_bills_by_sector_cached(
    session: AsyncSession,
    *,
    sector: str,
    limit: int = 20,
    min_confidence: float | None = None,
) -> list[LegislativeBill]:
    """Cached version of get_legislative_bills_by_sector."""
    return await get_legislative_bills_by_sector(
        session, sector=sector, limit=limit, min_confidence=min_confidence
    )


async def create_legislative_bill(
    session: AsyncSession,
    *,
    bill_id: str,
    title: str,
    stage: str,
    jurisdiction: str,
    committees: List[str],
    sectors: List[str],
    summary: str,
    next_action_date: date | None = None,
    sentiment_score: float | None = None,
    probability_of_enactment: float | None = None,
) -> LegislativeBill:
    """Create a new legislative bill."""
    bill = LegislativeBill(
        bill_id=bill_id,
        title=title,
        stage=stage,
        jurisdiction=jurisdiction,
        committees=committees,
        sectors=sectors,
        summary=summary,
        next_action_date=next_action_date,
        sentiment_score=sentiment_score,
        probability_of_enactment=probability_of_enactment,
        last_updated=datetime.now(timezone.utc),
    )
    session.add(bill)
    await session.flush()
    await session.refresh(bill)
    return bill


@cache_invalidate("legislation:*")
async def create_legislative_bill_with_cache_invalidation(
    session: AsyncSession,
    *,
    bill_id: str,
    title: str,
    stage: str,
    jurisdiction: str,
    committees: List[str],
    sectors: List[str],
    summary: str,
    next_action_date: date | None = None,
    sentiment_score: float | None = None,
    probability_of_enactment: float | None = None,
) -> LegislativeBill:
    """Create a legislative bill with cache invalidation."""
    return await create_legislative_bill(
        session,
        bill_id=bill_id,
        title=title,
        stage=stage,
        jurisdiction=jurisdiction,
        committees=committees,
        sectors=sectors,
        summary=summary,
        next_action_date=next_action_date,
        sentiment_score=sentiment_score,
        probability_of_enactment=probability_of_enactment,
    )


async def update_legislative_bill(
    session: AsyncSession,
    *,
    bill_id: str,
    **updates,
) -> LegislativeBill | None:
    """Update an existing legislative bill."""
    stmt = (
        update(LegislativeBill)
        .where(LegislativeBill.bill_id == bill_id)
        .values(**updates, updated_at=datetime.now(timezone.utc))
    )
    result = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return await get_legislative_bill(session, bill_id=bill_id)
    return None


@cache_invalidate("legislation:*")
async def update_legislative_bill_with_cache_invalidation(
    session: AsyncSession,
    *,
    bill_id: str,
    **updates,
) -> LegislativeBill | None:
    """Update a legislative bill with cache invalidation."""
    return await update_legislative_bill(session, bill_id=bill_id, **updates)


async def delete_legislative_bill(
    session: AsyncSession,
    *,
    bill_id: str,
) -> bool:
    """Delete a legislative bill."""
    stmt = delete(LegislativeBill).where(LegislativeBill.bill_id == bill_id)
    result = await session.execute(stmt)
    return result.rowcount > 0


@cache_invalidate("legislation:*")
async def delete_legislative_bill_with_cache_invalidation(
    session: AsyncSession,
    *,
    bill_id: str,
) -> bool:
    """Delete a legislative bill with cache invalidation."""
    return await delete_legislative_bill(session, bill_id=bill_id)


async def bulk_upsert_legislative_bills(
    session: AsyncSession,
    *,
    bills: List[dict],
) -> List[LegislativeBill]:
    """Bulk upsert legislative bills."""
    created_bills = []
    for bill_data in bills:
        bill = await get_legislative_bill(session, bill_id=bill_data['bill_id'])
        if bill:
            # Update existing bill
            bill = await update_legislative_bill(session, bill_id=bill_data['bill_id'], **bill_data)
        else:
            # Create new bill
            bill = await create_legislative_bill(session, **bill_data)
        created_bills.append(bill)
    return created_bills


@cache_invalidate("legislation:*")
async def bulk_upsert_legislative_bills_with_cache_invalidation(
    session: AsyncSession,
    *,
    bills: List[dict],
) -> List[LegislativeBill]:
    """Bulk upsert legislative bills with cache invalidation."""
    return await bulk_upsert_legislative_bills(session, bills=bills)


async def get_legislative_bill_versions(
    session: AsyncSession,
    *,
    bill_id: str,
    limit: int = 10,
) -> list[LegislativeBillVersion]:
    """Get version history for a legislative bill."""
    stmt = (
        select(LegislativeBillVersion)
        .where(LegislativeBillVersion.bill_id == bill_id)
        .order_by(LegislativeBillVersion.version.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


@cached(ttl=timedelta(minutes=60), key_prefix="legislation_versions")
async def get_legislative_bill_versions_cached(
    session: AsyncSession,
    *,
    bill_id: str,
    limit: int = 10,
) -> list[LegislativeBillVersion]:
    """Cached version of get_legislative_bill_versions."""
    return await get_legislative_bill_versions(session, bill_id=bill_id, limit=limit)


async def create_legislative_bill_version(
    session: AsyncSession,
    *,
    bill_id: str,
    version: int,
    payload: dict,
) -> LegislativeBillVersion:
    """Create a new version snapshot of a legislative bill."""
    bill_version = LegislativeBillVersion(
        bill_id=bill_id,
        version=version,
        payload=payload,
    )
    session.add(bill_version)
    await session.flush()
    await session.refresh(bill_version)
    return bill_version


async def get_legislation_stats(
    session: AsyncSession,
) -> dict:
    """Get statistics about legislative bills."""
    stmt = select(
        func.count(LegislativeBill.id).label('total_bills'),
        func.count(func.distinct(LegislativeBill.jurisdiction)).label('jurisdictions'),
        func.count(func.distinct(func.json_each(LegislativeBill.sectors))).label('sectors'),
        func.avg(LegislativeBill.probability_of_enactment).label('avg_probability'),
    )
    result = await session.execute(stmt)
    row = result.first()

    return {
        'total_bills': row.total_bills or 0,
        'jurisdictions': row.jurisdictions or 0,
        'sectors': row.sectors or 0,
        'avg_probability': float(row.avg_probability or 0),
    }


@cached(ttl=timedelta(minutes=10), key_prefix="legislation_stats")
async def get_legislation_stats_cached(
    session: AsyncSession,
) -> dict:
    """Cached version of get_legislation_stats."""
    return await get_legislation_stats(session)