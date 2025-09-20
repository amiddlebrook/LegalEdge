"""Alerts feed services."""
from datetime import datetime, timedelta, timezone
from typing import Iterable, List

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insights import AlertSubscription, PolicyAlert
from app.repositories.insights import get_alert_subscription, get_policy_alert_by_key, list_alert_subscriptions, list_alerts
from app.schemas.alerts import (
    AlertDispatchPreview,
    AlertDispatchTarget,
    AlertFeed,
    AlertMessage,
    AlertSubscriptionCreate,
    AlertSubscriptionRead,
    AlertSubscriptionUpdate,
    NotificationChannelConfig,
)


_SEVERITY_ORDER = ("low", "medium", "high", "critical")


def _normalize_filters(values: Iterable[str] | None) -> list[str] | None:
    if not values:
        return None
    normalized = [value.lower() for value in values if value]
    return normalized or None


def _severity_threshold(min_severity: str | None) -> int | None:
    if not min_severity:
        return None
    lookup = {name: index for index, name in enumerate(_SEVERITY_ORDER)}
    return lookup.get(min_severity.lower())


def _allowed_severities(threshold: int | None) -> list[str] | None:
    if threshold is None:
        return None
    return [name for index, name in enumerate(_SEVERITY_ORDER) if index >= threshold]


def _entity_matches(entities: Iterable[str], target: str | None) -> bool:
    if not target:
        return True
    target_upper = target.upper()
    return any((entity or '').upper() == target_upper for entity in entities or [])


def _filter_alerts(
    alerts: Iterable[AlertMessage],
    *,
    categories: list[str] | None,
    severities: list[str] | None,
    allowed_severities: list[str] | None,
    entity: str | None,
) -> list[AlertMessage]:
    filtered: list[AlertMessage] = []
    for alert in alerts:
        category = alert.category.lower()
        severity = alert.severity.lower()
        if categories and category not in categories:
            continue
        if severities and severity not in severities:
            continue
        if not severities and allowed_severities and severity not in allowed_severities:
            continue
        if not _entity_matches(alert.related_entities, entity):
            continue
        filtered.append(alert)
    return filtered


async def get_alert_feed(
    limit: int = 5,
    *,
    session: AsyncSession | None = None,
    categories: list[str] | None = None,
    severities: list[str] | None = None,
    min_severity: str | None = None,
    entity: str | None = None,
    since_minutes: int | None = None,
) -> AlertFeed:
    """Return prioritized alert messages for investors."""

    normalized_categories = _normalize_filters(categories)
    normalized_severities = _normalize_filters(severities)
    severity_floor = _severity_threshold(min_severity)
    allowed_severities = _allowed_severities(severity_floor) if not normalized_severities else None

    since = None
    if since_minutes:
        since = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)

    entity_filter = entity.upper() if entity else None

    if session is not None:
        try:
            alerts = await list_alerts(
                session,
                limit=limit,
                categories=normalized_categories,
                severities=normalized_severities,
                allowed_severities=allowed_severities,
                entity=entity_filter,
                since=since,
            )
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning('Failed to fetch alerts from DB: %s', exc)
        else:
            if alerts:
                feed = AlertFeed(
                    generated_at=alerts[0].raised_at,
                    alerts=[
                        AlertMessage(
                            id=alert.alert_key,
                            category=alert.category,
                            title=alert.title,
                            description=alert.description,
                            severity=alert.severity,
                            created_at=alert.raised_at,
                            related_entities=list(alert.related_entities or []),
                        )
                        for alert in alerts
                    ],
                )
                feed.applied_filters = _build_applied_filters(
                    categories,
                    severities,
                    min_severity,
                    entity,
                    since_minutes,
                )
                return feed

    return _fallback_feed(
        limit=limit,
        categories=normalized_categories,
        severities=normalized_severities,
        allowed_severities=allowed_severities,
        entity=entity_filter,
        since=since,
        original_filters=(categories, severities, min_severity, entity, since_minutes),
    )


def _fallback_feed(
    *,
    limit: int,
    categories: list[str] | None,
    severities: list[str] | None,
    allowed_severities: list[str] | None,
    entity: str | None,
    since: datetime | None,
    original_filters: tuple[list[str] | None, list[str] | None, str | None, str | None, int | None],
) -> AlertFeed:
    now = datetime.now(timezone.utc)
    fallback_alerts = [
        AlertMessage(
            id='alert-hr1001',
            category='Legislation',
            title='House committee advances AI Accountability and Transparency Act',
            description='Committee markup scheduled for next week; compliance vendors projected to see increased demand.',
            severity='high',
            created_at=now,
            related_entities=['HR-1001', 'REGN'],
        ),
        AlertMessage(
            id='alert-s4242',
            category='Congressional Trades',
            title='Sen. Jane Doe discloses AIQ accumulation',
            description='Recent Form 4 filing indicates BUY activity aligned with procurement legislation.',
            severity='medium',
            created_at=now,
            related_entities=['S.4242', 'AIQ'],
        ),
        AlertMessage(
            id='alert-privacy',
            category='State Policy',
            title='California privacy task force proposes stricter AI audit language',
            description='Draft proposal includes quarterly audit requirements impacting data processors.',
            severity='medium',
            created_at=now,
            related_entities=['CA-Privacy-Board', 'CSPN'],
        ),
    ]

    filtered = _filter_alerts(
        fallback_alerts,
        categories=categories,
        severities=severities,
        allowed_severities=allowed_severities,
        entity=entity,
    )

    if since is not None:
        filtered = [alert for alert in filtered if alert.created_at >= since]

    alerts = (filtered or fallback_alerts)[:limit]
    feed = AlertFeed(generated_at=alerts[0].created_at, alerts=alerts)
    feed.applied_filters = _build_applied_filters(*original_filters)
    return feed


def _build_applied_filters(
    categories: list[str] | None,
    severities: list[str] | None,
    min_severity: str | None,
    entity: str | None,
    since_minutes: int | None,
) -> dict[str, object] | None:
    filters = {
        "categories": categories,
        "severities": severities,
        "min_severity": min_severity,
        "entity": entity,
        "since_minutes": since_minutes,
    }
    compact = {key: value for key, value in filters.items() if value}
    return compact or None


_SEVERITY_INDEX = {name: index for index, name in enumerate(_SEVERITY_ORDER)}


def _normalize_preference_list(values: list[str] | None, *, make_lower: bool = False, make_upper: bool = False) -> list[str]:
    if not values:
        return []
    cleaned: list[str] = []
    for item in values:
        if not item:
            continue
        token = item.strip()
        if not token:
            continue
        if make_lower:
            token = token.lower()
        if make_upper:
            token = token.upper()
        cleaned.append(token)
    return sorted({token for token in cleaned})


def _serialize_channels(channels: list[NotificationChannelConfig]) -> list[dict[str, object]]:
    return [channel.model_dump() for channel in channels]


def _deserialize_channels(subscription: AlertSubscription) -> list[NotificationChannelConfig]:
    raw = subscription.channels or []
    return [NotificationChannelConfig.model_validate(channel) for channel in raw]


def _subscription_to_schema(subscription: AlertSubscription) -> AlertSubscriptionRead:
    return AlertSubscriptionRead(
        id=subscription.id,
        subscriber_id=subscription.subscriber_id,
        label=subscription.label,
        categories=subscription.categories or None,
        entities=subscription.entities or None,
        severities=subscription.severities or None,
        min_severity=subscription.min_severity,
        channels=_deserialize_channels(subscription),
        delivery_window_start=subscription.delivery_window_start,
        delivery_window_end=subscription.delivery_window_end,
        mute_until=subscription.mute_until,
        is_active=subscription.is_active,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
        last_notified_at=subscription.last_notified_at,
    )


def _severity_index(value: str | None) -> int:
    if not value:
        return -1
    return _SEVERITY_INDEX.get(value.lower(), -1)


def _subscription_matches_alert(subscription: AlertSubscription, alert: PolicyAlert) -> tuple[bool, str | None]:
    if not subscription.is_active:
        return False, 'subscription inactive'

    now = datetime.now(timezone.utc)

    if subscription.mute_until and subscription.mute_until > now:
        return False, 'subscription muted'

    if subscription.delivery_window_start and now < subscription.delivery_window_start:
        return False, 'before delivery window'

    if subscription.delivery_window_end and now > subscription.delivery_window_end:
        return False, 'after delivery window'

    category = alert.category.lower()
    if subscription.categories and category not in subscription.categories:
        return False, 'category filtered'

    severity = alert.severity.lower()
    if subscription.severities and severity not in {value.lower() for value in subscription.severities}:
        return False, 'severity filtered'

    if subscription.min_severity:
        if _severity_index(severity) < _severity_index(subscription.min_severity):
            return False, 'below severity threshold'

    if subscription.entities:
        alert_entities = {entity.upper() for entity in alert.related_entities or []}
        subscription_entities = {entity.upper() for entity in subscription.entities}
        if not alert_entities.intersection(subscription_entities):
            return False, 'entity filtered'

    return True, 'matched subscription filters'


async def create_alert_subscription(
    payload: AlertSubscriptionCreate,
    *,
    session: AsyncSession,
) -> AlertSubscriptionRead:
    """Persist a new alert subscription."""

    subscription = AlertSubscription(
        subscriber_id=payload.subscriber_id.strip(),
        label=payload.label.strip(),
        categories=_normalize_preference_list(payload.categories, make_lower=True),
        entities=_normalize_preference_list(payload.entities, make_upper=True),
        severities=_normalize_preference_list(payload.severities, make_lower=True),
        min_severity=payload.min_severity.lower().strip() if payload.min_severity else None,
        channels=_serialize_channels(payload.channels),
        delivery_window_start=payload.delivery_window_start,
        delivery_window_end=payload.delivery_window_end,
        mute_until=payload.mute_until,
    )
    session.add(subscription)
    await session.flush()
    await session.refresh(subscription)
    return _subscription_to_schema(subscription)


async def update_alert_subscription(
    subscription_id: int,
    payload: AlertSubscriptionUpdate,
    *,
    session: AsyncSession,
) -> AlertSubscriptionRead:
    """Update an existing subscription."""

    subscription = await get_alert_subscription(session, subscription_id)
    if subscription is None:
        raise ValueError('subscription not found')

    if payload.label is not None:
        subscription.label = payload.label.strip()
    if payload.categories is not None:
        subscription.categories = _normalize_preference_list(payload.categories, make_lower=True)
    if payload.entities is not None:
        subscription.entities = _normalize_preference_list(payload.entities, make_upper=True)
    if payload.severities is not None:
        subscription.severities = _normalize_preference_list(payload.severities, make_lower=True)
    if payload.min_severity is not None:
        subscription.min_severity = payload.min_severity.lower().strip() if payload.min_severity else None
    if payload.channels is not None:
        subscription.channels = _serialize_channels(payload.channels)
    if payload.delivery_window_start is not None:
        subscription.delivery_window_start = payload.delivery_window_start
    if payload.delivery_window_end is not None:
        subscription.delivery_window_end = payload.delivery_window_end
    if payload.mute_until is not None:
        subscription.mute_until = payload.mute_until
    if payload.is_active is not None:
        subscription.is_active = payload.is_active

    await session.flush()
    await session.refresh(subscription)
    return _subscription_to_schema(subscription)


async def list_configured_alert_subscriptions(
    *,
    session: AsyncSession,
    subscriber_id: str | None = None,
    include_inactive: bool = False,
) -> list[AlertSubscriptionRead]:
    """Return subscriptions matching optional filters."""

    subscriptions = await list_alert_subscriptions(
        session,
        subscriber_id=subscriber_id,
        include_inactive=include_inactive,
    )
    return [_subscription_to_schema(item) for item in subscriptions]


async def deactivate_alert_subscription(
    subscription_id: int,
    *,
    session: AsyncSession,
) -> None:
    """Soft delete a subscription by marking it inactive."""

    subscription = await get_alert_subscription(session, subscription_id)
    if subscription is None:
        raise ValueError('subscription not found')
    subscription.is_active = False
    await session.flush()


async def preview_alert_dispatch(
    alert_key: str,
    *,
    session: AsyncSession,
    include_inactive: bool = False,
) -> AlertDispatchPreview:
    """Preview which subscriptions would receive the given alert."""

    alert = await get_policy_alert_by_key(session, alert_key)
    if alert is None:
        raise ValueError('alert not found')

    subscriptions = await list_alert_subscriptions(
        session,
        include_inactive=include_inactive,
    )

    targets: list[AlertDispatchTarget] = []
    matched_subscription_ids: set[int] = set()

    for subscription in subscriptions:
        should_notify, reason = _subscription_matches_alert(subscription, alert)
        if not should_notify:
            continue
        channels = _deserialize_channels(subscription)
        if not channels:
            continue
        matched_subscription_ids.add(subscription.id)
        for channel in channels:
            targets.append(
                AlertDispatchTarget(
                    subscription_id=subscription.id,
                    subscriber_id=subscription.subscriber_id,
                    channel=channel,
                    reason=reason,
                )
            )

    return AlertDispatchPreview(
        alert_key=alert.alert_key,
        total_subscriptions=len(matched_subscription_ids),
        total_channels=len(targets),
        targets=targets,
    )


async def dispatch_alert(
    alert_key: str,
    *,
    session: AsyncSession,
) -> AlertDispatchPreview:
    """Dispatch an alert to matching subscriptions and update last notified timestamps."""

    preview = await preview_alert_dispatch(alert_key, session=session)
    if not preview.targets:
        return preview

    now = datetime.now(timezone.utc)
    updated_ids: set[int] = set()

    for target in preview.targets:
        if target.subscription_id in updated_ids:
            continue
        subscription = await get_alert_subscription(session, target.subscription_id)
        if subscription is None:
            continue
        subscription.last_notified_at = now
        updated_ids.add(subscription.id)

    await session.flush()
    return preview


async def get_alert_subscription_detail(
    subscription_id: int,
    *,
    session: AsyncSession,
) -> AlertSubscriptionRead:
    """Return a single subscription as a schema object."""

    subscription = await get_alert_subscription(session, subscription_id)
    if subscription is None:
        raise ValueError('subscription not found')
    return _subscription_to_schema(subscription)
