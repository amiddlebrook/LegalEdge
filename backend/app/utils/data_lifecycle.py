"""Data retention and lifecycle management policies."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


logger = logging.getLogger(__name__)


class DataRetentionManager:
    """Manage data retention policies and cleanup."""

    def __init__(self):
        self.retention_policies = {
            'legislative_bills': {
                'retention_days': 365 * 7,  # 7 years
                'archive_after_days': 365 * 2,  # Archive after 2 years
                'table_name': 'legislative_bills'
            },
            'legislative_bill_versions': {
                'retention_days': 365 * 10,  # 10 years
                'archive_after_days': 365 * 3,  # Archive after 3 years
                'table_name': 'legislative_bill_versions'
            },
            'forecast_signals': {
                'retention_days': 365 * 5,  # 5 years
                'archive_after_days': 365,  # Archive after 1 year
                'table_name': 'forecast_signals'
            },
            'trade_disclosures': {
                'retention_days': 365 * 10,  # 10 years (legal requirement)
                'archive_after_days': 365 * 2,  # Archive after 2 years
                'table_name': 'trade_disclosures'
            },
            'audit_logs': {
                'retention_days': 365 * 7,  # 7 years (compliance)
                'archive_after_days': None,  # Never archive
                'table_name': 'audit_logs'
            },
            'user_sessions': {
                'retention_days': 90,  # 90 days
                'archive_after_days': 30,  # Archive after 30 days
                'table_name': 'user_sessions'
            }
        }

    async def cleanup_expired_data(self, session: AsyncSession) -> Dict[str, int]:
        """Remove data that has exceeded retention policies."""
        results = {}
        now = datetime.utcnow()

        for table_name, policy in self.retention_policies.items():
            try:
                # Calculate cutoff date
                cutoff_date = now - timedelta(days=policy['retention_days'])

                # Execute cleanup query
                query = text(f"""
                    DELETE FROM {table_name}
                    WHERE created_at < :cutoff_date
                    AND (:archive_after_days IS NULL OR created_at < :archive_date)
                """)

                result = await session.execute(query, {
                    'cutoff_date': cutoff_date,
                    'archive_date': now - timedelta(days=policy['archive_after_days'])
                    if policy['archive_after_days'] else None
                })

                deleted_count = result.rowcount
                results[table_name] = deleted_count

                logger.info(f"Cleaned up {deleted_count} records from {table_name}")

            except Exception as e:
                logger.error(f"Error cleaning up {table_name}: {e}")
                results[table_name] = 0

        return results

    async def archive_old_data(self, session: AsyncSession) -> Dict[str, int]:
        """Archive old data to cold storage."""
        results = {}
        now = datetime.utcnow()

        for table_name, policy in self.retention_policies.items():
            if policy['archive_after_days'] is None:
                continue

            try:
                # Calculate archive date
                archive_date = now - timedelta(days=policy['archive_after_days'])

                # Archive query (would move to S3/archive table)
                query = text(f"""
                    INSERT INTO {table_name}_archive
                    SELECT * FROM {table_name}
                    WHERE created_at < :archive_date
                """)

                result = await session.execute(query, {'archive_date': archive_date})
                archived_count = result.rowcount

                # Remove from main table after archiving
                delete_query = text(f"""
                    DELETE FROM {table_name}
                    WHERE created_at < :archive_date
                """)

                await session.execute(delete_query, {'archive_date': archive_date})

                results[table_name] = archived_count

                logger.info(f"Archived {archived_count} records from {table_name}")

            except Exception as e:
                logger.error(f"Error archiving {table_name}: {e}")
                results[table_name] = 0

        return results

    async def generate_retention_report(self, session: AsyncSession) -> Dict[str, Any]:
        """Generate a report on data retention status."""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'policies': self.retention_policies,
            'record_counts': {},
            'upcoming_cleanup': {}
        }

        now = datetime.utcnow()

        # Get record counts for each table
        for table_name, policy in self.retention_policies.items():
            try:
                query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = await session.execute(query)
                count = result.scalar()
                report['record_counts'][table_name] = count

            except Exception as e:
                logger.error(f"Error counting records in {table_name}: {e}")
                report['record_counts'][table_name] = 0

        # Calculate upcoming cleanup
        for table_name, policy in self.retention_policies.items():
            cleanup_date = now + timedelta(days=policy['retention_days'])
            report['upcoming_cleanup'][table_name] = cleanup_date.isoformat()

        return report


class CostMonitor:
    """Monitor and optimize AWS costs."""

    def __init__(self):
        self.budgets = {
            'development': 500,  # $500/month
            'staging': 1000,     # $1000/month
            'production': 5000   # $5000/month
        }

        self.cost_optimization_rules = {
            'rds': {
                'threshold': 1000,  # $1000/month
                'recommendations': [
                    'Consider RDS reserved instances',
                    'Review read replica necessity',
                    'Check for over-provisioned instances'
                ]
            },
            'ecs': {
                'threshold': 800,   # $800/month
                'recommendations': [
                    'Implement auto-scaling policies',
                    'Use Fargate Spot instances where possible',
                    'Optimize task definitions'
                ]
            },
            's3': {
                'threshold': 200,   # $200/month
                'recommendations': [
                    'Implement lifecycle policies',
                    'Use appropriate storage classes',
                    'Clean up incomplete multipart uploads'
                ]
            }
        }

    async def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary from CloudWatch or AWS Cost Explorer."""
        # This would integrate with AWS Cost Explorer API
        return {
            'total_monthly_cost': 0,  # Placeholder
            'service_breakdown': {},
            'cost_trends': [],
            'budget_status': {}
        }

    async def check_budget_alerts(self) -> List[Dict[str, Any]]:
        """Check for budget overruns and generate alerts."""
        alerts = []
        cost_summary = await self.get_cost_summary()

        for environment, budget in self.budgets.items():
            if environment in cost_summary['budget_status']:
                usage = cost_summary['budget_status'][environment]
                if usage > budget * 0.8:  # 80% threshold
                    alerts.append({
                        'environment': environment,
                        'budget': budget,
                        'current_usage': usage,
                        'percentage': (usage / budget) * 100,
                        'severity': 'warning' if usage > budget * 0.9 else 'info'
                    })

        return alerts

    async def generate_optimization_recommendations(self) -> Dict[str, List[str]]:
        """Generate cost optimization recommendations."""
        recommendations = {}
        cost_summary = await self.get_cost_summary()

        for service, config in self.cost_optimization_rules.items():
            if service in cost_summary['service_breakdown']:
                monthly_cost = cost_summary['service_breakdown'][service]
                if monthly_cost > config['threshold']:
                    recommendations[service] = config['recommendations']

        return recommendations


class DataLifecycleManager:
    """Manage the complete data lifecycle from ingestion to deletion."""

    def __init__(self):
        self.retention_manager = DataRetentionManager()
        self.cost_monitor = CostMonitor()

    async def run_daily_maintenance(self, session: AsyncSession) -> Dict[str, Any]:
        """Run daily data maintenance tasks."""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'cleanup_results': {},
            'archive_results': {},
            'retention_report': {},
            'cost_alerts': [],
            'optimization_recommendations': {}
        }

        try:
            # Clean up expired data
            results['cleanup_results'] = await self.retention_manager.cleanup_expired_data(session)

            # Archive old data
            results['archive_results'] = await self.retention_manager.archive_old_data(session)

            # Generate retention report
            results['retention_report'] = await self.retention_manager.generate_retention_report(session)

            # Check cost alerts
            results['cost_alerts'] = await self.cost_monitor.check_budget_alerts()

            # Get optimization recommendations
            results['optimization_recommendations'] = await self.cost_monitor.generate_optimization_recommendations()

            logger.info("Daily maintenance completed successfully")

        except Exception as e:
            logger.error(f"Error during daily maintenance: {e}")
            results['error'] = str(e)

        return results

    async def get_compliance_status(self, session: AsyncSession) -> Dict[str, Any]:
        """Get compliance status for data retention."""
        report = await self.retention_manager.generate_retention_report(session)

        compliance_status = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }

        # Check for any data retention violations
        for table_name, policy in self.retention_manager.retention_policies.items():
            if table_name in report['record_counts']:
                record_count = report['record_counts'][table_name]
                # This is a simplified check - in reality you'd check specific records
                if record_count > 1000000:  # Arbitrary threshold
                    compliance_status['violations'].append({
                        'table': table_name,
                        'issue': 'High record count - consider archiving',
                        'record_count': record_count
                    })
                    compliance_status['compliant'] = False

        if compliance_status['compliant']:
            compliance_status['recommendations'].append(
                "All data retention policies are compliant"
            )

        return compliance_status


# Global instances
data_lifecycle_manager = DataLifecycleManager()


async def run_data_maintenance():
    """Scheduled task to run data maintenance."""
    logger.info("Starting scheduled data maintenance")

    async with AsyncSession(settings.database_url) as session:
        results = await data_lifecycle_manager.run_daily_maintenance(session)

        # Log results
        logger.info(f"Maintenance completed: {results}")

        # In a real implementation, you'd send alerts for critical issues
        cost_alerts = results.get('cost_alerts', [])
        if any(alert['severity'] == 'warning' for alert in cost_alerts):
            logger.warning(f"Budget alerts detected: {cost_alerts}")


async def check_compliance():
    """Check compliance status."""
    logger.info("Checking compliance status")

    async with AsyncSession(settings.database_url) as session:
        compliance_status = await data_lifecycle_manager.get_compliance_status(session)

        logger.info(f"Compliance status: {compliance_status}")

        return compliance_status
