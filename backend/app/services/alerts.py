"""Alerts feed service stubs."""
from datetime import datetime, timezone

from loguru import logger

from app.schemas.alerts import AlertFeed, AlertMessage


async def get_alert_feed(limit: int = 5) -> AlertFeed:
    logger.debug('Generating alert feed (limit=%s)', limit)
    """Return prioritized alert messages for investors."""

    now = datetime.now(timezone.utc)
    alerts = [
        AlertMessage(
            id="alert-hr1001",
            category="Legislation",
            title="House committee advances AI Accountability and Transparency Act",
            description=(
                "Committee markup scheduled for next week; compliance vendors projected to see increased demand."
            ),
            severity="high",
            created_at=now,
            related_entities=["HR-1001", "REGN"],
        ),
        AlertMessage(
            id="alert-s4242",
            category="Congressional Trades",
            title="Sen. Jane Doe discloses AIQ accumulation",
            description="Recent Form 4 filing indicates BUY activity aligned with procurement legislation.",
            severity="medium",
            created_at=now,
            related_entities=["S.4242", "AIQ"],
        ),
        AlertMessage(
            id="alert-privacy",
            category="State Policy",
            title="California privacy task force proposes stricter AI audit language",
            description="Draft proposal includes quarterly audit requirements impacting data processors.",
            severity="medium",
            created_at=now,
            related_entities=["CA-Privacy-Board", "CSPN"],
        ),
    ]

    return AlertFeed(generated_at=now, alerts=alerts[:limit])