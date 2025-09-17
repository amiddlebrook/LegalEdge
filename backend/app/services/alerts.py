"""Alerts feed services."""
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.insights import list_alerts
from app.schemas.alerts import AlertFeed, AlertMessage


async def get_alert_feed(
    limit: int = 5,
    *,
    session: AsyncSession | None = None,
) -> AlertFeed:
    logger.debug('Generating alert feed (limit=%s)', limit)
    """Return prioritized alert messages for investors."""

    if session is not None:
        try:
            alerts = await list_alerts(session, limit=limit)
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning('Failed to fetch alerts from DB: %s', exc)
        else:
            if alerts:
                return AlertFeed(
                    generated_at=alerts[0].created_at,
                    alerts=[
                        AlertMessage(
                            id=alert.alert_key,
                            category=alert.category,
                            title=alert.title,
                            description=alert.description,
                            severity=alert.severity,
                            created_at=alert.created_at,
                            related_entities=list(alert.related_entities or []),
                        )
                        for alert in alerts
                    ],
                )

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

    return AlertFeed(generated_at=now, alerts=fallback_alerts[:limit])