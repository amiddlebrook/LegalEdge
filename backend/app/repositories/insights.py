"""Alert and opportunity repositories."""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insights import AlertSubscription, OpportunityRecommendation, PolicyAlert


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
        lowered = [value.lower() for value in categories if value]
        if lowered:
            stmt = stmt.where(func.lower(PolicyAlert.category).in_(lowered))
    if severities:
        lowered = [value.lower() for value in severities if value]
        if lowered:
            stmt = stmt.where(func.lower(PolicyAlert.severity).in_(lowered))
    elif allowed_severities:
        lowered = [value.lower() for value in allowed_severities if value]
        if lowered:
            stmt = stmt.where(func.lower(PolicyAlert.severity).in_(lowered))
    if entity:
        stmt = stmt.where(PolicyAlert.related_entities.contains([entity]))
    if since is not None:
        stmt = stmt.where(PolicyAlert.raised_at >= since)

    stmt = stmt.order_by(PolicyAlert.raised_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_opportunities(
    session: AsyncSession,
    *,
    limit: int = 5,
    risk_ratings: list[str] | None = None,
    min_conviction: float | None = None,
    max_horizon_days: int | None = None,
) -> list[OpportunityRecommendation]:
    stmt = select(OpportunityRecommendation)

    if risk_ratings:
        lowered = [value.lower() for value in risk_ratings if value]
        if lowered:
            stmt = stmt.where(func.lower(OpportunityRecommendation.risk_rating).in_(lowered))
    if min_conviction is not None:
        stmt = stmt.where(OpportunityRecommendation.conviction >= min_conviction)
    if max_horizon_days is not None:
        stmt = stmt.where(OpportunityRecommendation.horizon_days <= max_horizon_days)

    stmt = stmt.order_by(OpportunityRecommendation.updated_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_alert_subscription(session: AsyncSession, subscription_id: int) -> AlertSubscription | None:
    """Return a single alert subscription if present."""

    result = await session.execute(
        select(AlertSubscription).where(AlertSubscription.id == subscription_id)
    )
    return result.scalar_one_or_none()


async def list_alert_subscriptions(
    session: AsyncSession,
    *,
    subscriber_id: str | None = None,
    include_inactive: bool = False,
) -> list[AlertSubscription]:
    """Return configured alert subscriptions, optionally filtered by subscriber."""

    stmt = select(AlertSubscription)
    if subscriber_id:
        stmt = stmt.where(AlertSubscription.subscriber_id == subscriber_id)
    if not include_inactive:
        stmt = stmt.where(AlertSubscription.is_active.is_(True))
    stmt = stmt.order_by(AlertSubscription.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_policy_alert_by_key(session: AsyncSession, alert_key: str) -> PolicyAlert | None:
    """Lookup a policy alert by key."""

    result = await session.execute(
        select(PolicyAlert).where(PolicyAlert.alert_key == alert_key)
    )
    return result.scalar_one_or_none()
