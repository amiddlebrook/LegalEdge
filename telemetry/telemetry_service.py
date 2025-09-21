"""Telemetry system for tracking user behavior and platform analytics."""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import text

from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of telemetry events."""
    PAGE_VIEW = "page_view"
    BUTTON_CLICK = "button_click"
    FEATURE_USE = "feature_use"
    ERROR = "error"
    PERFORMANCE = "performance"
    SEARCH = "search"
    FILTER = "filter"
    EXPORT = "export"
    SHARE = "share"
    ALERT_CREATE = "alert_create"
    PORTFOLIO_CREATE = "portfolio_create"
    LEGISLATION_VIEW = "legislation_view"
    DASHBOARD_LOAD = "dashboard_load"
    API_CALL = "api_call"
    SESSION_START = "session_start"
    SESSION_END = "session_end"


class UserAction(Enum):
    """User actions for analytics."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    FILTER = "filter"
    EXPORT = "export"
    SHARE = "share"
    NAVIGATE = "navigate"


@dataclass
class TelemetryEvent:
    """Telemetry event data structure."""
    event_type: EventType
    user_id: Optional[str]
    session_id: str
    timestamp: datetime
    event_data: Dict[str, Any]
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    page_url: Optional[str] = None
    user_action: Optional[UserAction] = None
    feature_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "event_data": self.event_data,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "page_url": self.page_url,
            "user_action": self.user_action.value if self.user_action else None,
            "feature_name": self.feature_name,
            "metadata": self.metadata
        }


class TelemetryCollector:
    """Collects and processes telemetry data."""

    def __init__(self):
        self.events: List[TelemetryEvent] = []
        self.batch_size = 100
        self.flush_interval = 30  # seconds

    async def collect_event(self, event: TelemetryEvent):
        """Collect a single telemetry event."""
        self.events.append(event)

        # Auto-flush if batch size reached
        if len(self.events) >= self.batch_size:
            await self.flush_events()

    async def flush_events(self):
        """Flush collected events to storage."""
        if not self.events:
            return

        try:
            # Process events in batches
            events_to_process = self.events.copy()
            self.events.clear()

            # Group events by type for efficient processing
            events_by_type = {}
            for event in events_to_process:
                event_type = event.event_type.value
                if event_type not in events_by_type:
                    events_by_type[event_type] = []
                events_by_type[event_type].append(event)

            # Process each event type
            for event_type, events in events_by_type.items():
                await self._process_event_type(event_type, events)

        except Exception as e:
            logger.error(f"Error flushing telemetry events: {e}")
            # Re-add events for retry
            self.events.extend(events_to_process)

    async def _process_event_type(self, event_type: str, events: List[TelemetryEvent]):
        """Process events of a specific type."""
        if event_type == EventType.ERROR.value:
            await self._process_error_events(events)
        elif event_type == EventType.PERFORMANCE.value:
            await self._process_performance_events(events)
        elif event_type == EventType.FEATURE_USE.value:
            await self._process_feature_use_events(events)
        else:
            # Store in database
            await self._store_events(events)

    async def _process_error_events(self, events: List[TelemetryEvent]):
        """Process error events for alerting and analysis."""
        for event in events:
            error_data = event.event_data
            error_message = error_data.get("message", "Unknown error")
            error_stack = error_data.get("stack", "")

            # Log critical errors
            if error_data.get("severity") == "critical":
                logger.critical(f"Critical error: {error_message}", extra={
                    "user_id": event.user_id,
                    "session_id": event.session_id,
                    "stack_trace": error_stack
                })

            # Store error for analysis
            await self._store_error_event(event)

    async def _process_performance_events(self, events: List[TelemetryEvent]):
        """Process performance metrics."""
        for event in events:
            performance_data = event.event_data
            load_time = performance_data.get("load_time")
            page_url = event.page_url

            if load_time and load_time > 5000:  # 5 seconds
                logger.warning(f"Slow page load: {load_time}ms for {page_url}")

    async def _process_feature_use_events(self, events: List[TelemetryEvent]):
        """Process feature usage analytics."""
        # Aggregate feature usage for product analytics
        feature_usage = {}
        for event in events:
            feature_name = event.feature_name or "unknown"
            if feature_name not in feature_usage:
                feature_usage[feature_name] = 0
            feature_usage[feature_name] += 1

        # Store feature usage analytics
        await self._store_feature_analytics(feature_usage)

    async def _store_events(self, events: List[TelemetryEvent]):
        """Store events in database."""
        # In a real implementation, this would use proper async database operations
        # For now, we'll use a simple file-based approach for demonstration
        events_data = [event.to_dict() for event in events]

        # Store in JSON file (in production, use proper database)
        await self._store_events_to_file(events_data)

    async def _store_events_to_file(self, events_data: List[Dict]):
        """Store events to file for demonstration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"telemetry_events_{timestamp}.json"

        filepath = Path("telemetry") / filename
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(events_data, f, indent=2)

    async def _store_error_event(self, event: TelemetryEvent):
        """Store error event for analysis."""
        # Implementation would store in error tracking system
        pass

    async def _store_feature_analytics(self, feature_usage: Dict[str, int]):
        """Store feature usage analytics."""
        # Implementation would update analytics database
        pass


# Global telemetry collector instance
telemetry_collector = TelemetryCollector()


class TelemetryService:
    """Service for handling telemetry operations."""

    @staticmethod
    async def track_event(
        event_type: EventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        page_url: Optional[str] = None,
        user_action: Optional[UserAction] = None,
        feature_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track a telemetry event."""
        if session_id is None:
            session_id = TelemetryService._generate_session_id()

        event = TelemetryEvent(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_data=event_data or {},
            user_agent=user_agent,
            ip_address=ip_address,
            page_url=page_url,
            user_action=user_action,
            feature_name=feature_name,
            metadata=metadata
        )

        await telemetry_collector.collect_event(event)

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID."""
        timestamp = str(time.time()).encode()
        return hashlib.md5(timestamp).hexdigest()[:16]

    @staticmethod
    async def get_analytics_summary(days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for the specified period."""
        # In a real implementation, this would query the database
        # For demonstration, return mock data
        return {
            "period_days": days,
            "total_events": 0,
            "unique_users": 0,
            "top_features": [],
            "error_rate": 0.0,
            "average_session_duration": 0,
            "popular_pages": []
        }

    @staticmethod
    async def get_feature_usage() -> Dict[str, int]:
        """Get feature usage statistics."""
        # Mock data for demonstration
        return {
            "dashboard": 150,
            "portfolio": 89,
            "alerts": 67,
            "legislation": 45,
            "search": 123
        }

    @staticmethod
    async def get_error_summary() -> Dict[str, Any]:
        """Get error summary for monitoring."""
        return {
            "total_errors": 0,
            "critical_errors": 0,
            "error_rate": 0.0,
            "top_errors": []
        }


# Background task for periodic telemetry processing
async def telemetry_processor():
    """Background task to process telemetry data."""
    while True:
        try:
            await asyncio.sleep(telemetry_collector.flush_interval)
            await telemetry_collector.flush_events()
        except Exception as e:
            logger.error(f"Error in telemetry processor: {e}")
            await asyncio.sleep(60)  # Wait before retry


# Utility functions for easy telemetry tracking
def track_page_view(user_id: Optional[str], page_url: str, session_id: Optional[str] = None):
    """Track page view event."""
    asyncio.create_task(TelemetryService.track_event(
        EventType.PAGE_VIEW,
        user_id=user_id,
        session_id=session_id,
        page_url=page_url,
        user_action=UserAction.READ
    ))


def track_button_click(user_id: Optional[str], button_name: str, page_url: str, session_id: Optional[str] = None):
    """Track button click event."""
    asyncio.create_task(TelemetryService.track_event(
        EventType.BUTTON_CLICK,
        user_id=user_id,
        session_id=session_id,
        page_url=page_url,
        event_data={"button_name": button_name},
        user_action=UserAction.READ
    ))


def track_feature_use(user_id: Optional[str], feature_name: str, session_id: Optional[str] = None):
    """Track feature usage event."""
    asyncio.create_task(TelemetryService.track_event(
        EventType.FEATURE_USE,
        user_id=user_id,
        session_id=session_id,
        feature_name=feature_name,
        user_action=UserAction.READ
    ))


def track_error(user_id: Optional[str], error_message: str, error_stack: str = "", severity: str = "error"):
    """Track error event."""
    asyncio.create_task(TelemetryService.track_event(
        EventType.ERROR,
        user_id=user_id,
        event_data={
            "message": error_message,
            "stack": error_stack,
            "severity": severity
        }
    ))


def track_performance(user_id: Optional[str], metric_name: str, value: float, page_url: str = ""):
    """Track performance metric."""
    asyncio.create_task(TelemetryService.track_event(
        EventType.PERFORMANCE,
        user_id=user_id,
        event_data={
            "metric_name": metric_name,
            "value": value
        },
        page_url=page_url
    ))
