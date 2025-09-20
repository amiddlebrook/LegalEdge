"""Celery configuration for LegalEdge background tasks."""
from __future__ import annotations

import os
from datetime import timedelta
from typing import Any, Dict

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Redis configuration for Celery
broker_url = settings.redis_url
result_backend = settings.redis_url

# Celery configuration
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False

# Task routing
task_routes = {
    'app.workers.tasks.ingestion.*': {'queue': 'ingestion'},
    'app.workers.tasks.ml.*': {'queue': 'ml_processing'},
    'app.workers.tasks.alerts.*': {'queue': 'alerts'},
    'app.workers.tasks.cleanup.*': {'queue': 'maintenance'},
}

# Periodic task schedule
beat_schedule: Dict[str, Dict[str, Any]] = {
    'ingestion-daily': {
        'task': 'app.workers.tasks.ingestion.run_daily_ingestion_task',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'ml-retrain-legislation': {
        'task': 'app.workers.tasks.ml.retrain_legislation_models_task',
        'schedule': timedelta(hours=12),  # Every 12 hours
    },
    'ml-retrain-forecasting': {
        'task': 'app.workers.tasks.ml.retrain_forecasting_models_task',
        'schedule': timedelta(hours=6),  # Every 6 hours
    },
    'alerts-process-pending': {
        'task': 'app.workers.tasks.alerts.process_pending_alerts_task',
        'schedule': timedelta(minutes=5),  # Every 5 minutes
    },
    'cleanup-old-data': {
        'task': 'app.workers.tasks.cleanup.cleanup_old_audit_logs_task',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    'generate-market-snapshots': {
        'task': 'app.workers.tasks.ml.generate_market_snapshots_task',
        'schedule': crontab(minute=30, hour='*/2'),  # Every 2 hours at :30
    },
}

# Task time limits
task_time_limit = 3600  # 1 hour
task_soft_time_limit = 3000  # 50 minutes

# Result expiration
result_expires = timedelta(days=7)

# Worker settings
worker_log_color = True
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Error handling
task_reject_on_worker_lost = True
task_acks_late = True
worker_cancel_long_running_tasks_on_connection_loss = True

# Create Celery app instance
celery_app = Celery('legaledge')
celery_app.config_from_object(__name__)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    'app.workers.tasks',
])

if __name__ == '__main__':
    celery_app.start()
