"""Background task definitions for LegalEdge."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

from celery import Task
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.ingestion import IngestionManager, get_default_connectors, persist_batches
from app.ml.forecaster import get_forecaster
from app.ml.legislation_pipeline import get_pipeline
from app.schemas.legislation import BillImpactRequest
from app.services.alerts import get_alert_feed
from app.services.forecasting import build_sector_forecast
from app.services.legislation import analyze_legislation, get_upcoming_legislation
from app.services.portfolio import aggregate_signals


class DatabaseTask(Task):
    """Base task class with database session management."""

    _session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create database session factory."""
        if self._session_factory is None:
            self._session_factory = SessionLocal
        return self._session_factory

    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        return self.session_factory()


@celery_app.task(base=DatabaseTask, name='app.workers.tasks.ingestion.run_daily_ingestion_task')
def run_daily_ingestion_task() -> Dict[str, Any]:
    """Celery task for running daily ingestion pipelines."""
    async def _run_ingestion() -> Dict[str, Any]:
        logger.info('Starting Celery-managed ingestion pipelines')

        # Create ingestion manager
        manager = IngestionManager(get_default_connectors())

        # Poll connectors
        enqueued = await manager.poll_once()
        logger.info(f'Ingestion connectors queued {enqueued} artifacts across {len(manager.connectors)} sources')

        if enqueued:
            # Get database session and persist
            async with DatabaseTask().get_session() as session:
                batches = await manager.drain_batches()
                summary = await persist_batches(batches, session=session)

                return {
                    'status': 'success',
                    'artifacts_enqueued': enqueued,
                    'batches_processed': len(batches),
                    'legislation_processed': summary.legislation_processed,
                    'created': summary.created,
                    'updated': summary.updated,
                    'errors': summary.errors,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }
        else:
            return {
                'status': 'success',
                'artifacts_enqueued': 0,
                'batches_processed': 0,
                'legislation_processed': 0,
                'created': 0,
                'updated': 0,
                'errors': [],
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

    # Run the async function
    return asyncio.run(_run_ingestion())


@celery_app.task(base=DatabaseTask, name='app.workers.tasks.ml.retrain_legislation_models_task')
def retrain_legislation_models_task() -> Dict[str, Any]:
    """Celery task for retraining legislation ML models."""
    async def _retrain() -> Dict[str, Any]:
        logger.info('Starting Celery-managed legislation model retraining')

        try:
            pipeline = get_pipeline()
            await pipeline.retrain()

            return {
                'status': 'success',
                'model_type': 'legislation',
                'action': 'retrained',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f'Failed to retrain legislation models: {e}')
            return {
                'status': 'error',
                'model_type': 'legislation',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

    return asyncio.run(_retrain())


@celery_app.task(base=DatabaseTask, name='app.workers.tasks.ml.retrain_forecasting_models_task')
def retrain_forecasting_models_task() -> Dict[str, Any]:
    """Celery task for retraining forecasting ML models."""
    async def _retrain() -> Dict[str, Any]:
        logger.info('Starting Celery-managed forecasting model retraining')

        try:
            forecaster = get_forecaster()
            await forecaster.retrain()

            return {
                'status': 'success',
                'model_type': 'forecasting',
                'action': 'retrained',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f'Failed to retrain forecasting models: {e}')
            return {
                'status': 'error',
                'model_type': 'forecasting',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

    return asyncio.run(_retrain())


@celery_app.task(base=DatabaseTask, name='app.workers.tasks.ml.generate_market_snapshots_task')
def generate_market_snapshots_task() -> Dict[str, Any]:
    """Celery task for generating market snapshots."""
    async def _generate() -> Dict[str, Any]:
        logger.info('Starting Celery-managed market snapshot generation')

        async with DatabaseTask().get_session() as session:
            try:
                # Get sample bills for analysis
                bills = await get_upcoming_legislation(limit=10, session=session)

                snapshots = []
                for bill in bills:
                    try:
                        request = BillImpactRequest(
                            bill_id=bill.bill_id,
                            sector=bill.sectors[0] if bill.sectors else 'General',
                            analysis_type='full'
                        )

                        # Generate comprehensive snapshot
                        analysis = await analyze_legislation(request, session=session)
                        sector_forecast = await build_sector_forecast(
                            bill.sectors[0] if bill.sectors else 'Technology',
                            session=session
                        )
                        signals = await aggregate_signals(limit=3, session=session)

                        snapshot = {
                            'bill_id': bill.bill_id,
                            'analysis': analysis.model_dump(),
                            'sector_forecast': sector_forecast.model_dump(),
                            'signals': [signal.model_dump() for signal in signals],
                            'generated_at': datetime.now(timezone.utc).isoformat(),
                        }
                        snapshots.append(snapshot)

                    except Exception as e:
                        logger.warning(f'Failed to generate snapshot for {bill.bill_id}: {e}')
                        continue

                return {
                    'status': 'success',
                    'snapshots_generated': len(snapshots),
                    'total_bills_processed': len(bills),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }

            except Exception as e:
                logger.error(f'Failed to generate market snapshots: {e}')
                return {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }

    return asyncio.run(_generate())


@celery_app.task(base=DatabaseTask, name='app.workers.tasks.alerts.process_pending_alerts_task')
def process_pending_alerts_task() -> Dict[str, Any]:
    """Celery task for processing pending alerts."""
    async def _process() -> Dict[str, Any]:
        logger.info('Starting Celery-managed alert processing')

        async with DatabaseTask().get_session() as session:
            try:
                # Get recent alerts
                feed = await get_alert_feed(limit=50, session=session)

                # Process alerts (this would normally dispatch notifications)
                processed_count = len(feed.alerts)
                alert_ids = [alert.id for alert in feed.alerts]

                return {
                    'status': 'success',
                    'alerts_processed': processed_count,
                    'alert_ids': alert_ids,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }

            except Exception as e:
                logger.error(f'Failed to process pending alerts: {e}')
                return {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }

    return asyncio.run(_process())


@celery_app.task(base=DatabaseTask, name='app.workers.tasks.cleanup.cleanup_old_audit_logs_task')
def cleanup_old_audit_logs_task(days_to_keep: int = 90) -> Dict[str, Any]:
    """Celery task for cleaning up old audit logs."""
    async def _cleanup() -> Dict[str, Any]:
        logger.info(f'Starting Celery-managed audit log cleanup (keeping {days_to_keep} days)')

        async with DatabaseTask().get_session() as session:
            try:
                from app.models.auth import AuditLog
                from sqlalchemy import delete
                from datetime import timedelta

                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

                # Delete old audit logs
                result = await session.execute(
                    delete(AuditLog).where(AuditLog.created_at < cutoff_date)
                )

                deleted_count = result.rowcount
                await session.commit()

                return {
                    'status': 'success',
                    'audit_logs_deleted': deleted_count,
                    'cutoff_date': cutoff_date.isoformat(),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }

            except Exception as e:
                logger.error(f'Failed to cleanup audit logs: {e}')
                return {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }

    return asyncio.run(_cleanup())
