"""Alert and notification schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator


class NotificationChannelConfig(BaseModel):
    """Delivery channel configuration for alert push notifications."""

    type: Literal['email', 'sms', 'webhook']
    target: str = Field(..., max_length=320)
    metadata: Dict[str, Any] | None = None
    is_verified: bool = False

    @field_validator('target')
    @classmethod
    def _normalize_target(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError('target must not be empty')
        return cleaned


class AlertSubscriptionBase(BaseModel):
    """Shared fields for alert subscription payloads."""

    label: str = Field(..., max_length=128)
    categories: List[str] | None = None
    entities: List[str] | None = None
    severities: List[str] | None = None
    min_severity: str | None = None
    channels: List[NotificationChannelConfig]
    delivery_window_start: datetime | None = None
    delivery_window_end: datetime | None = None
    mute_until: datetime | None = None

    @field_validator('categories', 'entities', 'severities', mode='before')
    @classmethod
    def _normalize_collection(cls, value):
        if value in (None, '', []):
            return None
        if isinstance(value, str):
            value = [value]
        normalized = sorted({str(item).strip() for item in value if str(item).strip()})
        return normalized or None

    @field_validator('min_severity')
    @classmethod
    def _normalize_min_severity(cls, value: str | None) -> str | None:
        return value.lower().strip() if value else None

    @field_validator('channels')
    @classmethod
    def _ensure_channels(cls, value: List[NotificationChannelConfig]) -> List[NotificationChannelConfig]:
        if not value:
            raise ValueError('at least one delivery channel is required')
        return value


class AlertSubscriptionCreate(AlertSubscriptionBase):
    """Payload to create a subscription."""

    subscriber_id: str = Field(..., max_length=128)


class AlertSubscriptionUpdate(BaseModel):
    """Partial update payload for subscriptions."""

    label: str | None = Field(default=None, max_length=128)
    categories: List[str] | None = None
    entities: List[str] | None = None
    severities: List[str] | None = None
    min_severity: str | None = None
    channels: List[NotificationChannelConfig] | None = None
    delivery_window_start: datetime | None = None
    delivery_window_end: datetime | None = None
    mute_until: datetime | None = None
    is_active: bool | None = None

    @field_validator('categories', 'entities', 'severities', mode='before')
    @classmethod
    def _normalize_collection(cls, value):
        if value in (None, '', []):
            return None
        if isinstance(value, str):
            value = [value]
        normalized = sorted({str(item).strip() for item in value if str(item).strip()})
        return normalized or None

    @field_validator('min_severity')
    @classmethod
    def _normalize_min_severity(cls, value: str | None) -> str | None:
        return value.lower().strip() if value else None

    @field_validator('channels')
    @classmethod
    def _validate_channels(cls, value: List[NotificationChannelConfig] | None) -> List[NotificationChannelConfig] | None:
        if value is None:
            return None
        if not value:
            raise ValueError('channels cannot be empty when supplied')
        return value


class AlertSubscriptionRead(AlertSubscriptionBase):
    """Subscription representation returned by the API."""

    id: int
    subscriber_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_notified_at: datetime | None = None


class AlertDispatchTarget(BaseModel):
    """Targeted notification based on subscription preferences."""

    subscription_id: int
    subscriber_id: str
    channel: NotificationChannelConfig
    reason: str | None = None


class AlertDispatchPreview(BaseModel):
    """Preview of alert deliveries for a specific alert message."""

    alert_key: str
    total_subscriptions: int
    total_channels: int
    targets: List[AlertDispatchTarget]


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
    applied_filters: Dict[str, Any] | None = None
