"""Alert feed endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import maybe_get_session
from app.schemas.alerts import (
    AlertDispatchPreview,
    AlertFeed,
    AlertSubscriptionCreate,
    AlertSubscriptionRead,
    AlertSubscriptionUpdate,
)
from app.services.alerts import (
    create_alert_subscription,
    deactivate_alert_subscription,
    dispatch_alert,
    get_alert_feed,
    get_alert_subscription_detail,
    list_configured_alert_subscriptions,
    preview_alert_dispatch,
    update_alert_subscription,
)


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertFeed, summary="Latest policy alerts")
async def list_alerts(
    limit: int = Query(default=5, ge=1, le=20),
    categories: list[str] | None = Query(default=None, description="Filter by alert categories"),
    severities: list[str] | None = Query(default=None, description="Filter by specific severity levels"),
    min_severity: str | None = Query(default=None, description="Return alerts at or above this severity"),
    entity: str | None = Query(default=None, description="Filter alerts mentioning a specific entity or ticker"),
    since_minutes: int | None = Query(default=None, ge=5, le=1440, description="Only include alerts raised within the past N minutes"),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> AlertFeed:
    """Return prioritized alerts for investors."""

    return await get_alert_feed(
        limit=limit,
        session=session,
        categories=categories,
        severities=severities,
        min_severity=min_severity,
        entity=entity,
        since_minutes=since_minutes,
    )




@router.post(
    '/subscriptions',
    response_model=AlertSubscriptionRead,
    status_code=201,
    summary='Create alert subscription',
)
async def create_subscription(
    payload: AlertSubscriptionCreate,
    session: AsyncSession | None = Depends(maybe_get_session),
) -> AlertSubscriptionRead:
    """Register a new alert subscription for a subscriber."""

    if session is None:
        raise HTTPException(status_code=503, detail='Database unavailable for subscription management')
    subscription = await create_alert_subscription(payload, session=session)
    await session.commit()
    return subscription


@router.get(
    '/subscriptions',
    response_model=list[AlertSubscriptionRead],
    summary='List alert subscriptions',
)
async def list_subscriptions(
    subscriber_id: str | None = Query(default=None, description='Filter by subscriber identifier'),
    include_inactive: bool = Query(default=False),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> list[AlertSubscriptionRead]:
    """Return configured alert subscriptions."""

    if session is None:
        raise HTTPException(status_code=503, detail='Database unavailable for subscription management')
    return await list_configured_alert_subscriptions(
        session=session,
        subscriber_id=subscriber_id,
        include_inactive=include_inactive,
    )


@router.get(
    '/subscriptions/{subscription_id}',
    response_model=AlertSubscriptionRead,
    summary='Get alert subscription',
)
async def get_subscription(
    subscription_id: int,
    session: AsyncSession | None = Depends(maybe_get_session),
) -> AlertSubscriptionRead:
    """Return a single alert subscription."""

    if session is None:
        raise HTTPException(status_code=503, detail='Database unavailable for subscription management')
    try:
        return await get_alert_subscription_detail(subscription_id, session=session)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put(
    '/subscriptions/{subscription_id}',
    response_model=AlertSubscriptionRead,
    summary='Update alert subscription',
)
async def update_subscription(
    subscription_id: int,
    payload: AlertSubscriptionUpdate,
    session: AsyncSession | None = Depends(maybe_get_session),
) -> AlertSubscriptionRead:
    """Update an existing alert subscription."""

    if session is None:
        raise HTTPException(status_code=503, detail='Database unavailable for subscription management')
    try:
        subscription = await update_alert_subscription(subscription_id, payload, session=session)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await session.commit()
    return subscription


@router.delete(
    '/subscriptions/{subscription_id}',
    status_code=204,
    summary='Deactivate alert subscription',
)
async def delete_subscription(
    subscription_id: int,
    session: AsyncSession | None = Depends(maybe_get_session),
) -> Response:
    """Soft delete a subscription."""

    if session is None:
        raise HTTPException(status_code=503, detail='Database unavailable for subscription management')
    try:
        await deactivate_alert_subscription(subscription_id, session=session)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await session.commit()
    return Response(status_code=204)


@router.get(
    '/dispatch/{alert_key}/preview',
    response_model=AlertDispatchPreview,
    summary='Preview alert dispatch targets',
)
async def preview_dispatch(
    alert_key: str,
    include_inactive: bool = Query(default=False),
    session: AsyncSession | None = Depends(maybe_get_session),
) -> AlertDispatchPreview:
    """Show which subscribers would receive a given alert."""

    if session is None:
        raise HTTPException(status_code=503, detail='Database unavailable for subscription management')
    try:
        return await preview_alert_dispatch(
            alert_key,
            session=session,
            include_inactive=include_inactive,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    '/dispatch/{alert_key}',
    response_model=AlertDispatchPreview,
    summary='Dispatch alert to subscribers',
)
async def dispatch_alert_now(
    alert_key: str,
    session: AsyncSession | None = Depends(maybe_get_session),
) -> AlertDispatchPreview:
    """Dispatch the alert and update subscription delivery metadata."""

    if session is None:
        raise HTTPException(status_code=503, detail='Database unavailable for subscription management')
    try:
        preview = await dispatch_alert(alert_key, session=session)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await session.commit()
    return preview
