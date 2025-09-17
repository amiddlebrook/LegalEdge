"""Command line utilities for LegalEdge backend."""
from __future__ import annotations

import argparse
import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger

from app.db.session import SessionLocal
from app.ingestion.sample_data import seed_sample_data
from app.workflows.pipeline import run_daily_ingestion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='LegalEdge management CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    seed_parser = subparsers.add_parser('seed-sample-data', help='Seed the database with development fixtures')
    seed_parser.add_argument('--reset', action='store_true', help='Truncate tables before inserting samples')

    subparsers.add_parser('run-ingestion-once', help='Execute the ingestion workflow immediately')

    return parser.parse_args()


async def handle_seed(reset: bool) -> None:
    async with SessionLocal() as session:
        await seed_sample_data(session, reset=reset)
    logger.success('Seeded sample data%s', ' with reset' if reset else '')


async def handle_ingestion() -> None:
    await run_daily_ingestion(session_factory=SessionLocal)
    logger.success('Ingestion workflow completed')


COMMAND_HANDLERS: dict[str, Callable[..., Awaitable[Any] | Any]] = {
    'seed-sample-data': handle_seed,
    'run-ingestion-once': handle_ingestion,
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

    _dispatch(handler, **kwargs)


if __name__ == '__main__':
    main()
