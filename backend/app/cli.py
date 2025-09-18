"""Command line utilities for LegalEdge backend."""
from __future__ import annotations

import argparse
import asyncio
import inspect
from pathlib import Path
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger

from app.db.session import SessionLocal
from app.ingestion import IngestionManager, get_default_connectors, persist_batches
from app.ingestion.sample_data import seed_sample_data
from app.services.portfolio import export_member_trade_history_csv, export_portfolio_snapshot_csv, export_conflicts_csv
from app.workflows.pipeline import run_daily_ingestion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='LegalEdge management CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    seed_parser = subparsers.add_parser('seed-sample-data', help='Seed the database with development fixtures')
    seed_parser.add_argument('--reset', action='store_true', help='Truncate tables before inserting samples')

    subparsers.add_parser('run-ingestion-once', help='Execute the ingestion workflow immediately')

    ingest_parser = subparsers.add_parser('ingest-connectors', help='Run ingestion connectors and optionally persist outputs')
    ingest_parser.add_argument('--runs', type=int, default=1, help='Number of polling cycles to execute (default: 1)')
    ingest_parser.add_argument('--dry-run', action='store_true', help='Fetch artifacts without persisting to the database')
    ingest_parser.add_argument('--reset-between-runs', action='store_true', help='Reset connector dedupe state between runs for backfills')

    snapshot_parser = subparsers.add_parser('export-portfolio-snapshot', help='Export portfolio snapshot analytics to CSV')
    snapshot_parser.add_argument('--lookback-days', type=int, default=30, help='Number of days to include (default: 30)')
    snapshot_parser.add_argument('--top-n', type=int, default=5, help='Number of tickers to include (default: 5)')
    snapshot_parser.add_argument('--output', type=str, default='portfolio_snapshot.csv', help='Destination CSV path')

    member_parser = subparsers.add_parser('export-member-trades', help='Export member trade history to CSV')
    member_parser.add_argument('member', type=str, help='Member name (e.g., "Sen. Jane Doe")')
    member_parser.add_argument('--lookback-days', type=int, default=180, help='Number of days to include (default: 180)')
    member_parser.add_argument('--limit', type=int, default=50, help='Maximum trades to export (default: 50)')
    member_parser.add_argument('--output', type=str, default='member_trades.csv', help='Destination CSV path')
    conflicts_parser = subparsers.add_parser('export-conflicts', help='Export conflict insights to CSV')
    conflicts_parser.add_argument('--limit', type=int, default=50, help='Maximum number of conflicts to export (default: 50)')
    conflicts_parser.add_argument('--output', type=str, default='conflicts.csv', help='Destination CSV path')


    return parser.parse_args()


async def handle_seed(reset: bool) -> None:
    async with SessionLocal() as session:
        await seed_sample_data(session, reset=reset)
    logger.success('Seeded sample data%s', ' with reset' if reset else '')



async def handle_export_portfolio_snapshot(lookback_days: int, top_n: int, output: str) -> None:
    async with SessionLocal() as session:
        csv_content = await export_portfolio_snapshot_csv(
            session=session,
            lookback_days=lookback_days,
            top_n=top_n,
        )
    Path(output).write_text(csv_content, encoding='utf-8')
    logger.success('Portfolio snapshot exported to %s', output)



async def handle_export_conflicts(limit: int, output: str) -> None:
    async with SessionLocal() as session:
        csv_content = await export_conflicts_csv(session=session, limit=limit)
    Path(output).write_text(csv_content, encoding='utf-8')
    logger.success('Conflict insights exported to %s', output)

async def handle_export_member_trades(member: str, lookback_days: int, limit: int, output: str) -> None:
    async with SessionLocal() as session:
        csv_content = await export_member_trade_history_csv(
            member,
            session=session,
            lookback_days=lookback_days,
            limit=limit,
        )
    Path(output).write_text(csv_content, encoding='utf-8')
    logger.success('Member trade history exported to %s', output)


async def handle_connector_ingest(
    runs: int = 1,
    dry_run: bool = False,
    reset_between_runs: bool = False,
) -> None:
    """Run connectors and optionally persist results."""

    manager = IngestionManager(get_default_connectors())
    runs = max(1, runs)
    total_enqueued = 0

    for index in range(runs):
        if index > 0 and reset_between_runs:
            manager.reset_seen()
        total_enqueued += await manager.poll_once()

    batches = await manager.drain_batches()
    if dry_run or not batches:
        logger.info(
            'Connector poll produced %s artifacts across %s sources%s',
            total_enqueued,
            len(batches),
            ' (dry-run)' if dry_run else '',
        )
        return

    async with SessionLocal() as session:
        summary = await persist_batches(batches, session=session)

    logger.success(
        'Connector ingest persisted %s artifacts (%s created, %s updated, %s skipped)',
        summary.legislation_processed,
        summary.created,
        summary.updated,
        summary.skipped,
    )


async def handle_ingestion() -> None:
    await run_daily_ingestion(session_factory=SessionLocal)
    logger.success('Ingestion workflow completed')


COMMAND_HANDLERS: dict[str, Callable[..., Awaitable[Any] | Any]] = {
    'seed-sample-data': handle_seed,
    'run-ingestion-once': handle_ingestion,
    'ingest-connectors': handle_connector_ingest,
}


def _run_coroutine(coro: Awaitable[Any]) -> Any:
    """Execute an awaitable, tolerating asyncio.run monkeypatching in tests."""

    runner = getattr(asyncio, 'run')
    if inspect.iscoroutinefunction(runner):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            asyncio.set_event_loop(None)
            loop.close()
    return runner(coro)


def _dispatch(handler: Callable[..., Awaitable[Any] | Any], **kwargs: Any) -> Any:
    result = handler(**kwargs)
    if inspect.isawaitable(result):
        return _run_coroutine(result)
    return result


def main() -> None:
    args = parse_args()
    command = args.command
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        raise SystemExit(f'Unknown command: {command}')

    kwargs: dict[str, Any] = {}
    if command == 'seed-sample-data':
        kwargs['reset'] = args.reset
    elif command == 'ingest-connectors':
        kwargs['runs'] = args.runs
        kwargs['dry_run'] = args.dry_run
        kwargs['reset_between_runs'] = args.reset_between_runs
    elif command == 'export-portfolio-snapshot':
        kwargs['lookback_days'] = args.lookback_days
        kwargs['top_n'] = args.top_n
        kwargs['output'] = args.output
    elif command == 'export-member-trades':
        kwargs['member'] = args.member
        kwargs['lookback_days'] = args.lookback_days
        kwargs['limit'] = args.limit
        kwargs['output'] = args.output
    elif command == 'export-conflicts':
        kwargs['limit'] = args.limit
        kwargs['output'] = args.output

    _dispatch(handler, **kwargs)


if __name__ == '__main__':
    main()
