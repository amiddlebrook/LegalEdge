import asyncio
from types import SimpleNamespace

import pytest

from app import cli


@pytest.fixture
def anyio_backend():
    return 'asyncio'


class DummySession:
    def __init__(self, called):
        self.called = called

    async def __aenter__(self):
        self.called['enter'] = True
        return object()

    async def __aexit__(self, exc_type, exc, tb):
        self.called['exit'] = True


class DummySessionFactory:
    def __init__(self, called):
        self.called = called

    def __call__(self):
        return DummySession(self.called)


@pytest.mark.anyio
async def test_handle_seed_uses_session_factory(monkeypatch):
    called: dict[str, bool] = {}

    async def fake_seed(session, reset):
        called['seed'] = reset

    monkeypatch.setattr(cli, 'SessionLocal', DummySessionFactory(called))
    monkeypatch.setattr(cli, 'seed_sample_data', fake_seed)

    await cli.handle_seed(reset=True)

    assert called['seed'] is True
    assert called['enter'] and called['exit']


@pytest.mark.anyio
async def test_handle_ingestion_passes_session_factory(monkeypatch):
    called = {}

    async def fake_run(session_factory=None, session=None):
        called['factory_used'] = session_factory is cli.SessionLocal

    monkeypatch.setattr(cli, 'SessionLocal', DummySessionFactory({}))
    monkeypatch.setattr(cli, 'run_daily_ingestion', fake_run)

    await cli.handle_ingestion()

    assert called['factory_used'] is True


def test_main_dispatches_seed(monkeypatch):
    called = {}

    async def fake_handler(reset):
        called['reset'] = reset

    monkeypatch.setattr(cli, 'parse_args', lambda: SimpleNamespace(command='seed-sample-data', reset=False))
    monkeypatch.setitem(cli.COMMAND_HANDLERS, 'seed-sample-data', fake_handler)

    async def runner(coro):
        await coro

    monkeypatch.setattr(asyncio, 'run', runner)

    cli.main()

    assert called['reset'] is False


def test_main_dispatches_ingestion(monkeypatch):
    called = {}

    async def fake_handler():
        called['ingestion'] = True

    monkeypatch.setattr(cli, 'parse_args', lambda: SimpleNamespace(command='run-ingestion-once'))
    monkeypatch.setitem(cli.COMMAND_HANDLERS, 'run-ingestion-once', fake_handler)

    async def runner(coro):
        await coro

    monkeypatch.setattr(asyncio, 'run', runner)

    cli.main()

    assert called['ingestion'] is True
