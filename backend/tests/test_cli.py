import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app import cli
from app.ingestion.persistence import NormalizationSummary
from app.schemas.ingestion import IngestionArtifact, IngestionBatch


@pytest.fixture
def anyio_backend():
    return "asyncio"


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


@pytest.mark.anyio
async def test_handle_connector_ingest_dry_run(monkeypatch):
    batches = [
        IngestionBatch(
            source='dummy',
            pulled_at=datetime.now(timezone.utc),
            artifacts=[],
        )
    ]

    class DummyManager:
        def __init__(self):
            self.poll_calls = 0
            self.resets = 0

        async def poll_once(self):
            self.poll_calls += 1
            return 1

        async def drain_batches(self):
            return batches

        def reset_seen(self):
            self.resets += 1

    manager = DummyManager()
    monkeypatch.setattr(cli, 'IngestionManager', lambda *args, **kwargs: manager)
    monkeypatch.setattr(cli, 'SessionLocal', DummySessionFactory({}))

    async def fake_persist(*args, **kwargs):
        raise AssertionError('persist_batches should not be called on dry run')

    monkeypatch.setattr(cli, 'persist_batches', fake_persist)

    await cli.handle_connector_ingest(runs=2, dry_run=True, reset_between_runs=True)

    assert manager.poll_calls == 2
    assert manager.resets == 1


@pytest.mark.anyio
async def test_handle_connector_ingest_persists_when_not_dry_run(monkeypatch):
    artifact = IngestionArtifact(
        artifact_type='legislation',
        source='congress.gov',
        external_id='hr-8890',
        jurisdiction='Federal',
        title='AI Governance Act',
        summary='Requires transparency.',
        stage='Committee',
        introduced_at=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
        committees=['House Energy & Commerce'],
        sectors=['Technology'],
        entities=['AIT'],
        metadata={},
    )
    batches = [IngestionBatch(source='congress.gov', pulled_at=datetime.now(timezone.utc), artifacts=[artifact])]

    class DummyManager:
        async def poll_once(self):
            return 1

        async def drain_batches(self):
            return batches

        def reset_seen(self):
            raise AssertionError('reset_seen should not be called')

    called: dict[str, object] = {}

    async def fake_persist(collected, session):
        called['persist_called'] = True
        called['batches'] = collected
        return NormalizationSummary(total_received=1, legislation_processed=0, filings_processed=1, trades_created=1)

    monkeypatch.setattr(cli, 'IngestionManager', lambda *args, **kwargs: DummyManager())
    monkeypatch.setattr(cli, 'persist_batches', fake_persist)
    monkeypatch.setattr(cli, 'SessionLocal', DummySessionFactory(called))

    await cli.handle_connector_ingest(runs=1, dry_run=False, reset_between_runs=False)

    assert called.get('persist_called') is True
    assert called.get('enter') and called.get('exit')
    assert called['batches'][0].artifacts[0].external_id == 'hr-8890'


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


def test_main_dispatches_connector_ingest(monkeypatch):
    called = {}

    async def fake_handler(runs, dry_run, reset_between_runs):
        called['args'] = (runs, dry_run, reset_between_runs)

    monkeypatch.setattr(
        cli,
        'parse_args',
        lambda: SimpleNamespace(command='ingest-connectors', runs=3, dry_run=True, reset_between_runs=False),
    )
    monkeypatch.setitem(cli.COMMAND_HANDLERS, 'ingest-connectors', fake_handler)

    async def runner(coro):
        await coro

    monkeypatch.setattr(asyncio, 'run', runner)

    cli.main()

    assert called['args'] == (3, True, False)


@pytest.mark.anyio
async def test_handle_export_portfolio_snapshot(monkeypatch, tmp_path):
    called = {}

    async def fake_export_portfolio_snapshot_csv(*, session=None, lookback_days, top_n):
        called['params'] = (lookback_days, top_n)
        return 'Metric,Value\nTotal,1'

    monkeypatch.setattr(cli, 'SessionLocal', DummySessionFactory({}))
    monkeypatch.setattr(cli, 'export_portfolio_snapshot_csv', fake_export_portfolio_snapshot_csv)

    output_file = tmp_path / 'snapshot.csv'
    await cli.handle_export_portfolio_snapshot(lookback_days=45, top_n=7, output=str(output_file))

    assert called['params'] == (45, 7)
    assert output_file.read_text() == 'Metric,Value\nTotal,1'


@pytest.mark.anyio
async def test_handle_export_member_trades(monkeypatch, tmp_path):
    called = {}

    async def fake_export_member_trade_history_csv(member, *, session=None, lookback_days, limit):
        called['params'] = (member, lookback_days, limit)
        return 'Member,Ticker\nTest,ABC'

    monkeypatch.setattr(cli, 'SessionLocal', DummySessionFactory({}))
    monkeypatch.setattr(cli, 'export_member_trade_history_csv', fake_export_member_trade_history_csv)

    output_file = tmp_path / 'member.csv'
    await cli.handle_export_member_trades('Sen. Test', lookback_days=90, limit=25, output=str(output_file))

    assert called['params'] == ('Sen. Test', 90, 25)
    assert output_file.read_text() == 'Member,Ticker\nTest,ABC'
