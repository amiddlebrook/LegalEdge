"""Common base classes for ingestion connectors."""
from __future__ import annotations

import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import Iterable

from loguru import logger

from app.schemas.ingestion import IngestionArtifact


class RateLimiter:
    """Simple token bucket style rate limiter for connector calls."""

    def __init__(self, *, calls_per_minute: int) -> None:
        if calls_per_minute <= 0:
            raise ValueError("calls_per_minute must be greater than zero")
        self._interval = 60.0 / float(calls_per_minute)
        self._last_call: float = 0.0

    async def acquire(self) -> None:
        """Await until a call is allowed."""

        now = time.monotonic()
        wait_time = self._interval - (now - self._last_call)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self._last_call = time.monotonic()


class BasePollingConnector(ABC):
    """Base class for polling connectors with rate limiting and jitter."""

    source_name: str
    poll_interval_seconds: float
    calls_per_minute: int

    def __init__(self) -> None:
        if not getattr(self, 'source_name', None):
            raise ValueError('Connector must define source_name')
        if getattr(self, 'poll_interval_seconds', 0) <= 0:
            raise ValueError('Connector must define poll_interval_seconds > 0')
        if getattr(self, 'calls_per_minute', 0) <= 0:
            raise ValueError('Connector must define calls_per_minute > 0')
        self._rate_limiter = RateLimiter(calls_per_minute=self.calls_per_minute)

    async def poll(self) -> list[IngestionArtifact]:
        """Fetch a normalized batch of artifacts with rate limiting."""

        await self._rate_limiter.acquire()
        try:
            batch = await self._fetch()
        except Exception as exc:  # pragma: no cover - defensive fall back
            logger.warning('Connector %s failed to fetch: %s', self.source_name, exc)
            return []

        if not batch:
            return []

        jitter = random.uniform(0.05, 0.2)
        await asyncio.sleep(jitter)  # avoid hammering downstream services
        return list(batch)

    @abstractmethod
    async def _fetch(self) -> Iterable[IngestionArtifact]:
        """Implementation specific fetch returning normalized artifacts."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source={self.source_name!r})"


__all__ = ['BasePollingConnector', 'RateLimiter']
