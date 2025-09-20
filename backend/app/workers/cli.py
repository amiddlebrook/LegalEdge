"""Background worker management commands."""
from __future__ import annotations

import asyncio
import sys
from typing import Any

from app.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal
from app.workers.tasks import run_daily_ingestion_task


async def run_worker():
    """Run a Celery worker."""
    print("Starting LegalEdge Celery worker...")
    print("Press Ctrl+C to stop")

    try:
        # Set environment for worker
        import os
        os.environ.setdefault('C_FORCE_ROOT', '1')

        # Run worker
        celery_app.start(['worker', '--loglevel=info'])

    except KeyboardInterrupt:
        print("\nStopping worker...")
    except Exception as e:
        print(f"Error running worker: {e}")
        sys.exit(1)


async def run_beat():
    """Run Celery beat scheduler."""
    print("Starting LegalEdge Celery beat scheduler...")
    print("Press Ctrl+C to stop")

    try:
        # Run beat scheduler
        celery_app.start(['beat', '--loglevel=info'])

    except KeyboardInterrupt:
        print("\nStopping beat scheduler...")
    except Exception as e:
        print(f"Error running beat scheduler: {e}")
        sys.exit(1)


async def run_flower():
    """Run Flower monitoring interface."""
    print("Starting LegalEdge Flower monitoring interface...")
    print("Open http://localhost:5555 in your browser")
    print("Press Ctrl+C to stop")

    try:
        # Run Flower
        celery_app.start(['flower', '--port=5555', '--broker=redis://localhost:6379/0'])

    except KeyboardInterrupt:
        print("\nStopping Flower...")
    except Exception as e:
        print(f"Error running Flower: {e}")
        sys.exit(1)


async def run_manual_task(task_name: str, **kwargs):
    """Run a specific task manually."""
    print(f"Running task: {task_name}")

    try:
        # Map task names to functions
        task_map = {
            'ingestion': run_daily_ingestion_task,
            'retrain_legislation': 'app.workers.tasks.ml.retrain_legislation_models_task',
            'retrain_forecasting': 'app.workers.tasks.ml.retrain_forecasting_models_task',
        }

        if task_name in task_map:
            if task_name == 'ingestion':
                # Run ingestion task synchronously
                result = run_daily_ingestion_task.delay()
                print(f"Task queued: {result.id}")
            else:
                # Run other tasks
                task_func = celery_app.tasks[task_map[task_name]]
                result = task_func.delay()
                print(f"Task queued: {result.id}")
        else:
            print(f"Unknown task: {task_name}")
            print("Available tasks:", list(task_map.keys()))

    except Exception as e:
        print(f"Error running task: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("LegalEdge Worker Management")
        print("Usage:")
        print("  python -m app.workers.cli worker    - Run Celery worker")
        print("  python -m app.workers.cli beat      - Run Celery beat scheduler")
        print("  python -m app.workers.cli flower    - Run Flower monitoring")
        print("  python -m app.workers.cli task <name> - Run specific task")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'worker':
        asyncio.run(run_worker())
    elif command == 'beat':
        asyncio.run(run_beat())
    elif command == 'flower':
        asyncio.run(run_flower())
    elif command == 'task':
        if len(sys.argv) < 3:
            print("Please specify a task name")
            sys.exit(1)
        task_name = sys.argv[2]
        asyncio.run(run_manual_task(task_name))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
