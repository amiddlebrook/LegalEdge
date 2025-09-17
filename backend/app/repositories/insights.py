"""Alert and opportunity repositories."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insights import OpportunityRecommendation, PolicyAlert


async def list_alerts(session: AsyncSession, *, limit: int = 5) -> list[PolicyAlert]:
    stmt = (
        select(PolicyAlert)
        .order_by(PolicyAlert.created_at.desc())
        .limit(limit)
    )
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