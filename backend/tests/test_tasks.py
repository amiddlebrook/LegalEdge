import asyncio

import pytest

from app.core.tasks import RecurringTaskManager


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_recurring_task_runs_multiple_times():
    calls = []

    async def _stub():
        calls.append(asyncio.get_event_loop().time())

    manager = RecurringTaskManager(_stub, interval_seconds=0.05, run_immediately=False)
    await manager.start()
    await asyncio.sleep(0.16)
    await manager.stop()

    # At least two runs should have occurred during the sleep window.
    assert len(calls) >= 2

def test_recurring_task_requires_interval():
    try:
        RecurringTaskManager(lambda: None)  # type: ignore[arg-type]
    except ValueError as exc:
        assert "interval" in str(exc)
    else:
        assert False, "Expected ValueError when interval is missing"
