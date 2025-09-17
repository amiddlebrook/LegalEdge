"""Alerts feed services."""
from datetime import datetime, timedelta, timezone
from typing import Iterable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.insights import list_alerts
from app.schemas.alerts import AlertFeed, AlertMessage


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
