"""Analytics dashboard for user behavior and platform insights."""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsMetric:
    """Analytics metric data structure."""
    name: str
    value: float
    change_percent: float
    change_direction: str  # "up", "down", "stable"
    timeframe: str  # "daily", "weekly", "monthly"
    category: str  # "user", "performance", "business", "technical"


@dataclass
class UserSegment:
    """User segment data structure."""
    id: str
    name: str
    description: str
    user_count: int
    percentage: float
    characteristics: Dict[str, Any]
    behavior_patterns: Dict[str, Any]


class AnalyticsService:
    """Service for collecting and analyzing platform analytics."""

    def __init__(self):
        self.metrics_cache = {}
        self.cache_timeout = 300  # 5 minutes

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get key metrics for the analytics dashboard."""
        return {
            "user_metrics": await self.get_user_metrics(),
            "performance_metrics": await self.get_performance_metrics(),
            "business_metrics": await self.get_business_metrics(),
            "feature_metrics": await self.get_feature_metrics(),
            "last_updated": datetime.now().isoformat()
        }

    async def get_user_metrics(self) -> Dict[str, Any]:
        """Get user-related analytics."""
        # In production, this would query actual data
        # For now, return realistic mock data

        current_date = datetime.now()
        previous_period = current_date - timedelta(days=30)

        return {
            "total_users": 15420,
            "active_users": 8930,
            "new_users_today": 45,
            "user_retention": {
                "day_1": 0.78,
                "day_7": 0.62,
                "day_30": 0.45
            },
            "user_segments": await self.get_user_segments(),
            "geographic_distribution": {
                "United States": 0.68,
                "Canada": 0.12,
                "United Kingdom": 0.08,
                "Germany": 0.06,
                "Other": 0.06
            },
            "device_types": {
                "Desktop": 0.62,
                "Mobile": 0.28,
                "Tablet": 0.10
            }
        }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance-related analytics."""
        return {
            "average_load_time": 1.2,  # seconds
            "error_rate": 0.012,  # 1.2%
            "uptime_percentage": 99.8,
            "api_response_time": 0.15,  # seconds
            "database_query_time": 0.08,  # seconds
            "cache_hit_rate": 0.94,
            "concurrent_users": 234,
            "requests_per_second": 45
        }

    async def get_business_metrics(self) -> Dict[str, Any]:
        """Get business-related analytics."""
        return {
            "monthly_recurring_revenue": 456780,
            "average_revenue_per_user": 29.60,
            "churn_rate": 0.034,  # 3.4%
            "customer_lifetime_value": 354,
            "conversion_rate": 0.156,  # 15.6%
            "trial_to_paid_conversion": 0.28,
            "plan_distribution": {
                "Free": 0.65,
                "Pro": 0.28,
                "Enterprise": 0.07
            }
        }

    async def get_feature_metrics(self) -> Dict[str, Any]:
        """Get feature usage analytics."""
        return {
            "feature_usage": {
                "dashboard": 0.89,
                "portfolio_analysis": 0.67,
                "alerts": 0.54,
                "legislation_search": 0.43,
                "reports": 0.34,
                "api_access": 0.12
            },
            "top_features": [
                {"name": "Portfolio Analysis", "usage": 0.89, "trend": "up"},
                {"name": "Real-time Alerts", "usage": 0.76, "trend": "up"},
                {"name": "Legislation Search", "usage": 0.65, "trend": "stable"},
                {"name": "Custom Reports", "usage": 0.54, "trend": "down"},
                {"name": "API Integration", "usage": 0.43, "trend": "up"}
            ],
            "feature_requests": 23,
            "recently_added": ["Advanced Filtering", "Bulk Operations", "Export API"]
        }

    async def get_user_segments(self) -> List[UserSegment]:
        """Get user segmentation data."""
        return [
            UserSegment(
                id="power_users",
                name="Power Users",
                description="Highly engaged users with advanced features",
                user_count=2340,
                percentage=0.15,
                characteristics={
                    "avg_session_time": 24,  # minutes
                    "features_used": 8.5,
                    "alerts_created": 12.3
                },
                behavior_patterns={
                    "daily_usage": True,
                    "api_usage": True,
                    "multiple_portfolios": True
                }
            ),
            UserSegment(
                id="casual_users",
                name="Casual Users",
                description="Regular users with moderate engagement",
                user_count=5670,
                percentage=0.37,
                characteristics={
                    "avg_session_time": 8,  # minutes
                    "features_used": 3.2,
                    "alerts_created": 2.1
                },
                behavior_patterns={
                    "weekly_usage": True,
                    "basic_features": True,
                    "single_portfolio": True
                }
            ),
            UserSegment(
                id="trial_users",
                name="Trial Users",
                description="New users evaluating the platform",
                user_count=5410,
                percentage=0.35,
                characteristics={
                    "avg_session_time": 12,  # minutes
                    "features_used": 4.8,
                    "alerts_created": 1.5
                },
                behavior_patterns={
                    "recent_signup": True,
                    "feature_exploration": True,
                    "help_usage": True
                }
            ),
            UserSegment(
                id="at_risk_users",
                name="At-Risk Users",
                description="Users showing signs of churn",
                user_count=2000,
                percentage=0.13,
                characteristics={
                    "avg_session_time": 3,  # minutes
                    "features_used": 1.8,
                    "last_login_days": 18
                },
                behavior_patterns={
                    "infrequent_usage": True,
                    "no_alerts": True,
                    "single_session": True
                }
            )
        ]

    async def get_conversion_funnel(self) -> Dict[str, Any]:
        """Get user conversion funnel data."""
        return {
            "stages": [
                {"name": "Landing Page", "visitors": 10000, "conversion_rate": 1.0},
                {"name": "Sign Up", "visitors": 1200, "conversion_rate": 0.12},
                {"name": "Complete Onboarding", "visitors": 890, "conversion_rate": 0.74},
                {"name": "Create Portfolio", "visitors": 670, "conversion_rate": 0.75},
                {"name": "Set Up Alerts", "visitors": 450, "conversion_rate": 0.67},
                {"name": "Upgrade to Pro", "visitors": 125, "conversion_rate": 0.28}
            ],
            "drop_off_points": [
                {"stage": "Sign Up", "drop_off_rate": 0.88},
                {"stage": "Complete Onboarding", "drop_off_rate": 0.26},
                {"stage": "Create Portfolio", "drop_off_rate": 0.25}
            ]
        }

    async def get_cohort_analysis(self) -> Dict[str, Any]:
        """Get user cohort analysis."""
        return {
            "cohorts": [
                {
                    "name": "January 2024",
                    "size": 1200,
                    "retention": {
                        "week_1": 0.85,
                        "week_4": 0.72,
                        "week_12": 0.58,
                        "week_26": 0.45
                    }
                },
                {
                    "name": "February 2024",
                    "size": 980,
                    "retention": {
                        "week_1": 0.89,
                        "week_4": 0.76,
                        "week_12": 0.62,
                        "week_26": 0.48
                    }
                }
            ],
            "average_retention": {
                "week_1": 0.87,
                "week_4": 0.74,
                "week_12": 0.60,
                "week_26": 0.47
            }
        }

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time platform metrics."""
        return {
            "current_time": datetime.now().isoformat(),
            "active_sessions": 234,
            "requests_per_minute": 156,
            "errors_per_minute": 2,
            "average_response_time": 0.145,
            "top_pages": [
                {"page": "/dashboard", "views": 45},
                {"page": "/portfolios", "views": 23},
                {"page": "/legislation/search", "views": 18},
                {"page": "/alerts", "views": 12}
            ],
            "recent_errors": [
                {"error": "API timeout", "count": 3, "last_seen": "2 minutes ago"},
                {"error": "Database connection", "count": 1, "last_seen": "5 minutes ago"}
            ]
        }

    async def get_feature_analytics(self, feature_name: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific feature."""
        # Mock data for demonstration
        return {
            "feature_name": feature_name,
            "usage_statistics": {
                "total_uses": 15420,
                "unique_users": 8930,
                "average_uses_per_user": 1.7,
                "usage_trend": "up"  # up, down, stable
            },
            "user_satisfaction": {
                "rating": 4.2,
                "feedback_count": 234,
                "common_issues": ["UI confusion", "Performance slow", "Missing features"]
            },
            "performance_metrics": {
                "average_load_time": 1.2,
                "error_rate": 0.02,
                "crash_rate": 0.005
            },
            "business_impact": {
                "revenue_attribution": 0.15,
                "conversion_lift": 0.23,
                "retention_effect": 0.12
            }
        }

    async def generate_report(self, report_type: str, date_range: Dict[str, str],
                            filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate custom analytics report."""
        report_configs = {
            "user_engagement": {
                "title": "User Engagement Report",
                "metrics": ["daily_active_users", "session_duration", "feature_usage"],
                "charts": ["user_growth", "engagement_trends"]
            },
            "performance_monitoring": {
                "title": "Performance Monitoring Report",
                "metrics": ["response_times", "error_rates", "uptime"],
                "charts": ["performance_trends", "error_analysis"]
            },
            "business_metrics": {
                "title": "Business Metrics Report",
                "metrics": ["revenue", "conversion", "churn"],
                "charts": ["revenue_trends", "conversion_funnel"]
            }
        }

        if report_type not in report_configs:
            return {"error": "Invalid report type"}

        config = report_configs[report_type]

        return {
            "report_id": f"report_{int(datetime.now().timestamp())}",
            "title": config["title"],
            "generated_at": datetime.now().isoformat(),
            "date_range": date_range,
            "filters": filters or {},
            "data": await self._generate_report_data(report_type, date_range, filters),
            "summary": await self._generate_report_summary(report_type),
            "recommendations": await self._generate_recommendations(report_type)
        }

    async def _generate_report_data(self, report_type: str, date_range: Dict[str, str],
                                  filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate actual report data."""
        # Mock data generation
        return {
            "metrics": {},
            "charts": {},
            "tables": []
        }

    async def _generate_report_summary(self, report_type: str) -> str:
        """Generate report summary."""
        summaries = {
            "user_engagement": "User engagement shows steady growth with increasing feature adoption.",
            "performance_monitoring": "System performance remains stable with 99.8% uptime.",
            "business_metrics": "Revenue growth continues with improving conversion rates."
        }
        return summaries.get(report_type, "Report summary not available.")

    async def _generate_recommendations(self, report_type: str) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = {
            "user_engagement": [
                "Focus on improving onboarding experience",
                "Add more interactive tutorials",
                "Enhance mobile experience"
            ],
            "performance_monitoring": [
                "Optimize database queries",
                "Implement better caching strategy",
                "Monitor API rate limits"
            ],
            "business_metrics": [
                "Target high-value user segments",
                "Improve trial conversion flow",
                "Expand enterprise features"
            ]
        }
        return recommendations.get(report_type, [])


class AnalyticsDashboard:
    """Interactive analytics dashboard."""

    def __init__(self):
        self.analytics_service = AnalyticsService()

    async def get_dashboard_data(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get complete dashboard data."""
        return {
            "header": {
                "title": "LegalEdge Analytics Dashboard",
                "subtitle": "Real-time insights into platform performance and user behavior",
                "last_updated": datetime.now().isoformat()
            },
            "metrics": await self.analytics_service.get_dashboard_metrics(),
            "real_time": await self.analytics_service.get_real_time_metrics(),
            "quick_actions": [
                {"name": "Generate Report", "action": "generate_report"},
                {"name": "Export Data", "action": "export_data"},
                {"name": "Schedule Alert", "action": "schedule_alert"},
                {"name": "View Details", "action": "view_details"}
            ]
        }

    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific insights."""
        return {
            "user_id": user_id,
            "engagement_score": 0.78,
            "feature_usage": await self.analytics_service.get_feature_analytics("dashboard"),
            "session_history": [],
            "recommendations": [
                "Try the new portfolio analysis feature",
                "Set up custom alerts for your industry",
                "Join the community forum"
            ]
        }

    async def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance monitoring insights."""
        metrics = await self.analytics_service.get_performance_metrics()

        insights = {
            "status": "healthy" if metrics["uptime_percentage"] > 99 else "degraded",
            "alerts": [],
            "recommendations": []
        }

        if metrics["error_rate"] > 0.05:
            insights["alerts"].append({
                "type": "warning",
                "message": "High error rate detected",
                "metric": f"Error Rate: {metrics['error_rate']:.1%}"
            })

        if metrics["average_load_time"] > 2.0:
            insights["alerts"].append({
                "type": "warning",
                "message": "Slow page load times",
                "metric": f"Average Load Time: {metrics['average_load_time']:.1f}s"
            })

        if metrics["uptime_percentage"] < 99.5:
            insights["alerts"].append({
                "type": "error",
                "message": "Low uptime detected",
                "metric": f"Uptime: {metrics['uptime_percentage']:.1f}%"
            })

        return insights

    async def export_analytics(self, export_type: str, date_range: Dict[str, str]) -> str:
        """Export analytics data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_type == "json":
            data = await self.analytics_service.get_dashboard_metrics()
            filename = f"analytics_export_{timestamp}.json"

            filepath = Path("analytics") / "exports" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return str(filepath)

        elif export_type == "csv":
            # Generate CSV export
            filename = f"analytics_export_{timestamp}.csv"
            # Implementation would generate CSV data
            return filename

        else:
            raise ValueError(f"Unsupported export type: {export_type}")


# Global analytics dashboard instance
analytics_dashboard = AnalyticsDashboard()
