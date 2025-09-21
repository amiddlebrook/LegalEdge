"""Main feedback service integrating telemetry, surveys, and release management."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from .telemetry_service import TelemetryService
from .survey_service import SurveyService
from .release_service import ReleaseService
from .analytics_service import AnalyticsService
from .ab_testing_service import ABTestService

logger = logging.getLogger(__name__)


class FeedbackService:
    """Main service integrating all feedback and analytics components."""

    def __init__(self):
        self.telemetry_service = TelemetryService
        self.survey_service = SurveyService
        self.release_service = ReleaseService
        self.analytics_service = AnalyticsService
        self.ab_test_service = ABTestService

    async def initialize_system(self):
        """Initialize the feedback system."""
        logger.info("Initializing feedback system...")

        # Create sample data for demonstration
        await self._initialize_sample_data()

        # Start background tasks
        await self._start_background_tasks()

        logger.info("Feedback system initialized successfully")

    async def _initialize_sample_data(self):
        """Initialize sample data for demonstration."""
        try:
            # Create sample roadmap
            await self.release_service.create_sample_roadmap("system")

            # Create sample A/B tests
            await self.ab_test_service.create_sample_tests("system")

            # Create sample surveys
            await self.survey_service.create_nps_survey("system")
            await self.survey_service.create_feature_request_survey("system")
            await self.survey_service.create_onboarding_survey("system")

            logger.info("Sample data initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing sample data: {e}")

    async def _start_background_tasks(self):
        """Start background processing tasks."""
        # Start telemetry processing
        asyncio.create_task(self._telemetry_processor())

        # Start survey processing
        asyncio.create_task(self._survey_processor())

        # Start analytics aggregation
        asyncio.create_task(self._analytics_aggregator())

    async def _telemetry_processor(self):
        """Background task for processing telemetry data."""
        while True:
            try:
                await asyncio.sleep(60)  # Process every minute

                # Get analytics summary
                summary = await self.telemetry_service.get_analytics_summary(1)

                # Check for performance issues
                if summary.get("error_rate", 0) > 0.05:  # 5% error rate
                    logger.warning(f"High error rate detected: {summary['error_rate']}")

                # Check for user engagement issues
                if summary.get("average_session_duration", 0) < 60:  # Less than 1 minute
                    logger.info("Low user engagement detected - may need UX improvements")

            except Exception as e:
                logger.error(f"Error in telemetry processor: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def _survey_processor(self):
        """Background task for processing survey responses."""
        while True:
            try:
                await asyncio.sleep(300)  # Process every 5 minutes

                # Check for NPS detractors and trigger follow-ups
                nps_surveys = [s for s in await self.survey_service.get_all_surveys()
                             if s.survey_type.value == "nps"]

                for survey in nps_surveys:
                    analytics = await self.survey_service.get_survey_results(survey.id)
                    nps_score = analytics.get("nps_score", 0)

                    if nps_score is not None and nps_score < 0:
                        logger.info(f"NPS detractors detected for survey {survey.id}")
                        # In production, trigger follow-up emails/calls

            except Exception as e:
                logger.error(f"Error in survey processor: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry

    async def _analytics_aggregator(self):
        """Background task for aggregating analytics data."""
        while True:
            try:
                await asyncio.sleep(3600)  # Process hourly

                # Generate daily analytics report
                report = await self.analytics_service.generate_report(
                    "user_engagement",
                    {
                        "start_date": (datetime.now() - timedelta(days=1)).isoformat(),
                        "end_date": datetime.now().isoformat()
                    }
                )

                # Store report for historical analysis
                await self._store_analytics_report(report)

            except Exception as e:
                logger.error(f"Error in analytics aggregator: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry

    async def _store_analytics_report(self, report: Dict[str, Any]):
        """Store analytics report for historical tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path("analytics") / "reports" / f"daily_report_{timestamp}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

    # Public API methods

    async def track_user_event(self, event_type: str, user_id: Optional[str] = None,
                             session_id: Optional[str] = None, event_data: Optional[Dict] = None):
        """Track a user event for analytics."""
        from .telemetry_service import EventType

        try:
            event_enum = EventType(event_type)
            await self.telemetry_service.track_event(
                event_enum,
                user_id=user_id,
                session_id=session_id,
                event_data=event_data or {}
            )
        except ValueError:
            logger.warning(f"Unknown event type: {event_type}")

    async def get_user_surveys(self, user_id: Optional[str], session_id: str) -> List[Dict]:
        """Get available surveys for a user."""
        surveys = await self.survey_service.get_available_surveys(user_id, session_id)
        return [s.to_dict() for s in surveys]

    async def submit_survey_response(self, survey_id: str, user_id: Optional[str],
                                   session_id: str, responses: Dict[str, Any]) -> bool:
        """Submit a survey response."""
        return await self.survey_service.submit_survey_response(
            survey_id, user_id, session_id, responses
        )

    async def create_feature_request(self, request_data: Dict[str, Any], user_id: str) -> Dict:
        """Create a feature request from user feedback."""
        feature = await self.release_service.create_feature_request(request_data, user_id)

        # Track the feature request event
        await self.track_user_event(
            "feature_request",
            user_id=user_id,
            event_data={
                "feature_title": request_data.get("title", ""),
                "priority": request_data.get("priority", "medium")
            }
        )

        return feature.to_dict()

    async def get_analytics_dashboard(self, user_id: Optional[str] = None) -> Dict:
        """Get analytics dashboard data."""
        from .analytics_service import analytics_dashboard
        return await analytics_dashboard.get_dashboard_data(user_id)

    async def get_ab_test_variant(self, test_id: str, user_id: str) -> Optional[str]:
        """Get A/B test variant for user."""
        return await self.ab_test_service.get_variant(test_id, user_id)

    async def track_ab_test_event(self, test_id: str, user_id: str, event_name: str,
                                 event_data: Dict[str, Any]):
        """Track an A/B test event."""
        await self.ab_test_service.track_test_event(test_id, user_id, event_name, event_data)

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Get real-time metrics
            real_time = await self.analytics_service.get_real_time_metrics()

            # Get error summary
            error_summary = await self.telemetry_service.get_error_summary()

            # Get survey response rates
            survey_response_rate = 0.15  # Mock data

            # Determine overall health
            error_rate = error_summary.get("error_rate", 0)
            if error_rate > 0.05:
                status = "degraded"
                issues = ["High error rate detected"]
            else:
                status = "healthy"
                issues = []

            # Check for other issues
            if real_time.get("errors_per_minute", 0) > 10:
                issues.append("High error frequency")
                if status == "healthy":
                    status = "degraded"

            return {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "error_rate": error_rate,
                    "response_time": real_time.get("average_response_time", 0),
                    "active_users": real_time.get("active_sessions", 0),
                    "survey_response_rate": survey_response_rate
                },
                "issues": issues,
                "recommendations": self._get_health_recommendations(issues)
            }

        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _get_health_recommendations(self, issues: List[str]) -> List[str]:
        """Get recommendations for system health issues."""
        recommendations = []

        if "High error rate detected" in issues:
            recommendations.append("Investigate recent deployments or code changes")
            recommendations.append("Check error logs for patterns")
            recommendations.append("Consider rolling back recent changes if needed")

        if "High error frequency" in issues:
            recommendations.append("Monitor specific error endpoints")
            recommendations.append("Implement additional error handling")
            recommendations.append("Consider rate limiting if under attack")

        if not issues:
            recommendations.append("System is healthy - continue monitoring")
            recommendations.append("Consider A/B testing new features")

        return recommendations

    async def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        try:
            # Collect data from all services
            analytics = await self.analytics_service.get_dashboard_metrics()
            surveys = await self.survey_service.get_all_surveys()
            tests = await self.ab_test_service.get_running_tests()
            roadmap = await self.release_service.get_roadmap()

            # Generate insights
            insights = {
                "generated_at": datetime.now().isoformat(),
                "period": "Last 30 days",
                "summary": await self._generate_insights_summary(analytics, surveys, tests),
                "key_metrics": await self._extract_key_metrics(analytics),
                "user_feedback": await self._analyze_user_feedback(surveys),
                "experiment_results": await self._analyze_experiments(tests),
                "product_opportunities": await self._identify_opportunities(roadmap),
                "recommendations": await self._generate_recommendations(analytics, surveys, tests, roadmap)
            }

            return insights

        except Exception as e:
            logger.error(f"Error generating insights report: {e}")
            return {"error": str(e)}

    async def _generate_insights_summary(self, analytics: Dict, surveys: List, tests: List) -> str:
        """Generate summary of key insights."""
        user_count = analytics.get("user_metrics", {}).get("total_users", 0)
        nps_score = 0  # Would come from survey analysis
        running_tests = len(tests)

        return f"Platform serving {user_count","} users with {running_tests} active experiments. User satisfaction trending positive with opportunities for feature optimization identified."

    async def _extract_key_metrics(self, analytics: Dict) -> Dict[str, Any]:
        """Extract key metrics for insights."""
        return {
            "users": analytics.get("user_metrics", {}),
            "performance": analytics.get("performance_metrics", {}),
            "business": analytics.get("business_metrics", {}),
            "features": analytics.get("feature_metrics", {})
        }

    async def _analyze_user_feedback(self, surveys: List) -> Dict[str, Any]:
        """Analyze user feedback from surveys."""
        # Mock analysis - in production would analyze actual responses
        return {
            "total_responses": 0,
            "nps_score": 0,
            "top_issues": [],
            "feature_requests": 0,
            "satisfaction_trends": "stable"
        }

    async def _analyze_experiments(self, tests: List) -> Dict[str, Any]:
        """Analyze A/B test results."""
        return {
            "total_tests": len(tests),
            "successful_tests": 0,
            "failed_tests": 0,
            "inconclusive_tests": 0,
            "potential_uplift": 0.0
        }

    async def _identify_opportunities(self, roadmap: Dict) -> List[Dict]:
        """Identify product opportunities."""
        return [
            {
                "type": "feature",
                "title": "Mobile App Enhancement",
                "description": "Improve mobile experience based on user feedback",
                "potential_impact": "high",
                "effort": "medium"
            },
            {
                "type": "improvement",
                "title": "Faster Search",
                "description": "Optimize search performance for large datasets",
                "potential_impact": "medium",
                "effort": "low"
            }
        ]

    async def _generate_recommendations(self, analytics: Dict, surveys: List, tests: List, roadmap: Dict) -> List[str]:
        """Generate actionable recommendations."""
        return [
            "Focus on mobile experience improvements to increase engagement",
            "Optimize onboarding flow to reduce drop-off rates",
            "Implement real-time alerts feature based on user demand",
            "Improve error handling and user feedback mechanisms",
            "Consider expanding into new market segments based on usage patterns"
        ]


# Global feedback service instance
feedback_service = FeedbackService()


# Background task for overall system processing
async def system_insights_processor():
    """Background task to process system insights and generate reports."""
    while True:
        try:
            await asyncio.sleep(86400)  # Process daily

            # Generate daily insights report
            insights = await feedback_service.generate_insights_report()

            # Store insights for historical tracking
            timestamp = datetime.now().strftime("%Y%m%d")
            filepath = Path("analytics") / "insights" / f"daily_insights_{timestamp}.json"
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(insights, f, indent=2)

            logger.info("Daily insights report generated successfully")

        except Exception as e:
            logger.error(f"Error in system insights processor: {e}")
            await asyncio.sleep(3600)  # Wait 1 hour before retry
