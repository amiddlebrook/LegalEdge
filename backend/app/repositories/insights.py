"""Alert and opportunity repositories."""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insights import OpportunityRecommendation, PolicyAlert


async def list_alerts(
    session: AsyncSession,
    *,
    limit: int = 5,
    categories: list[str] | None = None,
    severities: list[str] | None = None,
    allowed_severities: list[str] | None = None,
    entity: str | None = None,
    since: datetime | None = None,
) -> list[PolicyAlert]:
    stmt = select(PolicyAlert)

    if categories:
        stmt = stmt.where(func.lower(PolicyAlert.category).in_(categories))
    if severities:
        stmt = stmt.where(func.lower(PolicyAlert.severity).in_(severities))
    elif allowed_severities:
        stmt = stmt.where(func.lower(PolicyAlert.severity).in_(allowed_severities))
    if entity:
        stmt = stmt.where(PolicyAlert.related_entities.contains([entity]))
    if since is not None:
        stmt = stmt.where(PolicyAlert.raised_at >= since)

    stmt = stmt.order_by(PolicyAlert.raised_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_opportunities(session: AsyncSession, *, limit: int = 5) -> list[OpportunityRecommendation]:
    stmt = (
        select(OpportunityRecommendation)
        .order_by(OpportunityRecommendation.updated_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())

