"""Command line utilities for LegalEdge backend."""
from __future__ import annotations

import argparse
import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger

from app.db.session import SessionLocal
from app.ingestion import IngestionManager, get_default_connectors, persist_batches
from app.ingestion.sample_data import seed_sample_data
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

    return parser.parse_args()


async def handle_seed(reset: bool) -> None:
    async with SessionLocal() as session:
        await seed_sample_data(session, reset=reset)
    logger.success('Seeded sample data%s', ' with reset' if reset else '')


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

    _dispatch(handler, **kwargs)


if __name__ == '__main__':
    main()
