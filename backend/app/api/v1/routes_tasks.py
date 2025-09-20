"""Background task management API endpoints."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.db.session import get_session
from app.services.auth import get_current_superuser
from app.workers.tasks import run_daily_ingestion_task

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


@router.get("/status", summary="Get task queue status")
async def get_task_status() -> Dict[str, Any]:
    """Get the current status of background task queues."""
    try:
        # Get active tasks
        inspect = celery_app.control.inspect()

        active_tasks = inspect.active() or {}
        scheduled_tasks = inspect.scheduled() or {}
        reserved_tasks = inspect.reserved() or {}

        return {
            "status": "healthy",
            "active_tasks": len(active_tasks),
            "scheduled_tasks": len(scheduled_tasks),
            "reserved_tasks": len(reserved_tasks),
            "worker_status": "active" if active_tasks else "idle",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Task queue unavailable: {str(e)}"
        )


@router.post("/ingestion/run", summary="Manually trigger ingestion")
async def trigger_ingestion(
    current_user=Depends(get_current_superuser)
) -> Dict[str, Any]:
    """Manually trigger the ingestion pipeline."""
    try:
        task = run_daily_ingestion_task.delay()
        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Ingestion task has been queued",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue ingestion task: {str(e)}"
        )


@router.get("/ingestion/history", summary="Get ingestion task history")
async def get_ingestion_history(
    limit: int = 10,
    current_user=Depends(get_current_superuser)
) -> List[Dict[str, Any]]:
    """Get recent ingestion task results."""
    # This would typically query a task results database
    # For now, return a placeholder response
    return [
        {
            "task_id": "placeholder",
            "status": "completed",
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:05:00Z",
            "result": {
                "artifacts_enqueued": 0,
                "batches_processed": 0,
                "legislation_processed": 0,
            }
        }
    ]


@router.post("/models/retrain/legislation", summary="Retrain legislation models")
async def retrain_legislation_models(
    current_user=Depends(get_current_superuser)
) -> Dict[str, Any]:
    """Manually trigger legislation model retraining."""
    try:
        task = celery_app.tasks['app.workers.tasks.ml.retrain_legislation_models_task'].delay()
        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Legislation model retraining has been queued",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue retraining task: {str(e)}"
        )


@router.post("/models/retrain/forecasting", summary="Retrain forecasting models")
async def retrain_forecasting_models(
    current_user=Depends(get_current_superuser)
) -> Dict[str, Any]:
    """Manually trigger forecasting model retraining."""
    try:
        task = celery_app.tasks['app.workers.tasks.ml.retrain_forecasting_models_task'].delay()
        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Forecasting model retraining has been queued",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue retraining task: {str(e)}"
        )


@router.get("/scheduled", summary="Get scheduled tasks")
async def get_scheduled_tasks(
    current_user=Depends(get_current_superuser)
) -> Dict[str, Any]:
    """Get information about scheduled background tasks."""
    from app.celery_app import beat_schedule

    return {
        "scheduled_tasks": [
            {
                "name": name,
                "schedule": str(schedule) if hasattr(schedule, '__str__') else schedule,
                "task": task_config["task"]
            }
            for name, task_config in beat_schedule.items()
        ]
    }
