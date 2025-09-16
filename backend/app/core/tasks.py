"""Recurring background task utilities."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


class RecurringTaskManager:
    """Manage a recurring coroutine execution lifecycle."""

    def __init__(
        self,
        coroutine: Callable[[], Awaitable[None]],
        *,
        interval_minutes: float | None = None,
        interval_seconds: float | None = None,
        run_immediately: bool = True,
    ) -> None:
        if interval_seconds is None and interval_minutes is None:
            raise ValueError("Either interval_seconds or interval_minutes must be provided")

        self._interval = (
            interval_seconds
            if interval_seconds is not None
            else float(interval_minutes or 0) * 60.0
        )
        if self._interval <= 0:
            raise ValueError("Interval must be greater than zero")

        self._coroutine = coroutine
        self._run_immediately = run_immediately
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Kick off the recurring execution loop."""

        if self._task is not None and not self._task.done():
            return

        self._stop_event.clear()
        self._task = asyncio.create_task(self._runner())

    async def stop(self) -> None:
        """Signal the task to stop and await shutdown."""

        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None

    async def _runner(self) -> None:
        if self._run_immediately:
            await self._maybe_call()

        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._interval)
            except asyncio.TimeoutError:
                await self._maybe_call()

    async def _maybe_call(self) -> None:
        try:
            await self._coroutine()
        except Exception:  # pragma: no cover - log hook for observability later
            # Silence exceptions for now; logging will be injected when observability is configured.
            pass