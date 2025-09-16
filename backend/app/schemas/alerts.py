"""Alert and notification schemas."""
from datetime import datetime

from pydantic import BaseModel


class AlertMessage(BaseModel):
    """Alert surfaced to investors about legislative or trading events."""

    id: str
    category: str
    title: str
    description: str
    severity: str
    created_at: datetime
    related_entities: list[str]


class AlertFeed(BaseModel):
    """Container for alert messages."""

    generated_at: datetime
    alerts: list[AlertMessage]