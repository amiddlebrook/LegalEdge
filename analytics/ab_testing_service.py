"""A/B testing framework for iterative product improvements."""

import json
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import asyncio
import hashlib

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """A/B test status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestType(Enum):
    """Type of A/B test."""
    UI_CHANGE = "ui_change"
    FEATURE_FLAG = "feature_flag"
    ALGORITHM_CHANGE = "algorithm_change"
    PRICING_TEST = "pricing_test"
    COPY_TEST = "copy_test"
    WORKFLOW_TEST = "workflow_test"


class MetricType(Enum):
    """Types of metrics to track."""
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    REVENUE = "revenue"
    PERFORMANCE = "performance"
    USABILITY = "usability"


@dataclass
class Variant:
    """A/B test variant."""
    id: str
    name: str
    description: str
    configuration: Dict[str, Any]
    percentage: float  # Traffic allocation (0-100)
    is_control: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert variant to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "configuration": self.configuration,
            "percentage": self.percentage,
            "is_control": self.is_control
        }


@dataclass
class ABTest:
    """A/B test configuration."""
    id: str
    name: str
    description: str
    test_type: TestType
    status: TestStatus
    hypothesis: str
    variants: List[Variant]
    primary_metric: MetricType
    secondary_metrics: List[MetricType]
    target_audience: Optional[Dict[str, Any]] = None
    minimum_sample_size: int = 1000
    minimum_duration_days: int = 7
    confidence_level: float = 0.95
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert test to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "test_type": self.test_type.value,
            "status": self.status.value,
            "hypothesis": self.hypothesis,
            "variants": [v.to_dict() for v in self.variants],
            "primary_metric": self.primary_metric.value,
            "secondary_metrics": [m.value for m in self.secondary_metrics],
            "target_audience": self.target_audience,
            "minimum_sample_size": self.minimum_sample_size,
            "minimum_duration_days": self.minimum_duration_days,
            "confidence_level": self.confidence_level,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "results": self.results,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by
        }


class ABTestManager:
    """Manages A/B tests and experiments."""

    def __init__(self):
        self.active_tests: Dict[str, ABTest] = {}
        self.test_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {test_id: variant_id}
        self.test_results: Dict[str, Dict[str, Any]] = {}

    async def create_test(self, test_data: Dict[str, Any], created_by: str) -> ABTest:
        """Create a new A/B test."""
        test_id = str(uuid.uuid4())

        # Validate variants
        variants = []
        total_percentage = 0

        for i, v_data in enumerate(test_data["variants"]):
            variant = Variant(
                id=str(uuid.uuid4()),
                name=v_data["name"],
                description=v_data["description"],
                configuration=v_data["configuration"],
                percentage=v_data["percentage"],
                is_control=v_data.get("is_control", i == 0)  # First variant is control by default
            )
            variants.append(variant)
            total_percentage += variant.percentage

        if abs(total_percentage - 100) > 0.1:  # Allow small rounding errors
            raise ValueError(f"Variant percentages must sum to 100%, got {total_percentage}")

        test = ABTest(
            id=test_id,
            name=test_data["name"],
            description=test_data["description"],
            test_type=TestType(test_data["test_type"]),
            status=TestStatus.DRAFT,
            hypothesis=test_data["hypothesis"],
            variants=variants,
            primary_metric=MetricType(test_data["primary_metric"]),
            secondary_metrics=[MetricType(m) for m in test_data.get("secondary_metrics", [])],
            target_audience=test_data.get("target_audience"),
            minimum_sample_size=test_data.get("minimum_sample_size", 1000),
            minimum_duration_days=test_data.get("minimum_duration_days", 7),
            confidence_level=test_data.get("confidence_level", 0.95),
            created_at=datetime.now(),
            created_by=created_by
        )

        self.active_tests[test_id] = test
        await self._save_test(test)
        return test

    async def start_test(self, test_id: str) -> bool:
        """Start an A/B test."""
        if test_id not in self.active_tests:
            return False

        test = self.active_tests[test_id]
        if test.status != TestStatus.DRAFT:
            return False

        test.status = TestStatus.RUNNING
        test.start_date = datetime.now()
        test.updated_at = datetime.now()

        await self._update_test(test)
        await self._initialize_test_tracking(test)
        return True

    def get_variant_for_user(self, test_id: str, user_id: str) -> Optional[str]:
        """Get the variant assignment for a user in a test."""
        if test_id not in self.active_tests:
            return None

        test = self.active_tests[test_id]
        if test.status != TestStatus.RUNNING:
            return None

        # Check if user already has an assignment
        user_assignments = self.test_assignments.get(user_id, {})
        if test_id in user_assignments:
            return user_assignments[test_id]

        # Assign variant based on percentages
        variant_id = self._assign_variant(test.variants, user_id)
        user_assignments[test_id] = variant_id
        self.test_assignments[user_id] = user_assignments

        return variant_id

    def _assign_variant(self, variants: List[Variant], user_id: str) -> str:
        """Assign user to variant based on percentages."""
        # Create deterministic assignment based on user ID
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        random_value = user_hash % 100

        cumulative_percentage = 0
        for variant in variants:
            cumulative_percentage += variant.percentage
            if random_value < cumulative_percentage:
                return variant.id

        # Fallback to first variant
        return variants[0].id

    async def track_event(self, test_id: str, user_id: str, event_name: str, event_data: Dict[str, Any]):
        """Track an event for A/B test analysis."""
        variant_id = self.get_variant_for_user(test_id, user_id)
        if not variant_id:
            return

        # Store event data for analysis
        event_key = f"{test_id}:{variant_id}:{event_name}"
        if event_key not in self.test_results:
            self.test_results[event_key] = []

        self.test_results[event_key].append({
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "event_data": event_data
        })

        await self._save_event_data(test_id, variant_id, event_name, event_data)

    async def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get results for an A/B test."""
        if test_id not in self.active_tests:
            return {"error": "Test not found"}

        test = self.active_tests[test_id]
        if test_id not in self.test_results:
            return {"message": "No results available yet"}

        # Calculate basic statistics
        results = {
            "test_id": test_id,
            "test_name": test.name,
            "status": test.status.value,
            "start_date": test.start_date.isoformat() if test.start_date else None,
            "duration_days": (datetime.now() - test.start_date).days if test.start_date else 0,
            "sample_size": 0,
            "variants": {},
            "statistical_significance": None,
            "winner": None,
            "recommendations": []
        }

        # Analyze results by variant
        for variant in test.variants:
            variant_results = {}
            for event_name in self.test_results:
                if event_name.startswith(f"{test_id}:{variant.id}:"):
                    events = self.test_results[event_name]
                    variant_results[event_name.split(":")[-1]] = {
                        "event_count": len(events),
                        "unique_users": len(set(e["user_id"] for e in events)),
                        "conversion_rate": len(events) / max(1, len(set(e["user_id"] for e in events)))
                    }

            results["variants"][variant.name] = {
                "id": variant.id,
                "is_control": variant.is_control,
                "results": variant_results,
                "sample_size": variant_results.get("conversion", {}).get("unique_users", 0)
            }

        results["sample_size"] = sum(v["sample_size"] for v in results["variants"].values())

        # Determine if test should be concluded
        if results["sample_size"] >= test.minimum_sample_size:
            results["statistical_significance"] = await self._calculate_significance(test, results)
            results["winner"] = await self._determine_winner(test, results)
            results["recommendations"] = await self._generate_recommendations(test, results)

        return results

    async def _calculate_significance(self, test: ABTest, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical significance of test results."""
        # This would implement proper statistical testing
        # For demonstration, return mock significance data
        return {
            "primary_metric": {
                "p_value": 0.03,
                "confidence_level": 0.95,
                "significant": True
            },
            "secondary_metrics": {}
        }

    async def _determine_winner(self, test: ABTest, results: Dict[str, Any]) -> Optional[str]:
        """Determine the winning variant."""
        significance = results.get("statistical_significance", {})
        if significance.get("primary_metric", {}).get("significant", False):
            # Find variant with highest conversion rate for primary metric
            best_variant = None
            best_rate = 0

            for variant_name, variant_data in results["variants"].items():
                rate = variant_data["results"].get("conversion", {}).get("conversion_rate", 0)
                if rate > best_rate:
                    best_rate = rate
                    best_variant = variant_name

            return best_variant

        return None

    async def _generate_recommendations(self, test: ABTest, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if results["sample_size"] < test.minimum_sample_size:
            recommendations.append("Continue test to reach minimum sample size")

        if results.get("statistical_significance", {}).get("primary_metric", {}).get("significant", False):
            winner = results.get("winner")
            if winner:
                recommendations.append(f"Implement winning variant: {winner}")
                recommendations.append("Roll out changes to all users")
                recommendations.append("Monitor post-launch metrics")
            else:
                recommendations.append("Results inconclusive - extend test or redesign")
        else:
            recommendations.append("Continue test - results not yet significant")

        return recommendations

    async def conclude_test(self, test_id: str, conclusion: str, implemented: bool = False):
        """Conclude an A/B test."""
        if test_id not in self.active_tests:
            return False

        test = self.active_tests[test_id]
        test.status = TestStatus.COMPLETED
        test.end_date = datetime.now()
        test.updated_at = datetime.now()

        # Store final results
        final_results = await self.get_test_results(test_id)
        final_results["conclusion"] = conclusion
        final_results["implemented"] = implemented
        final_results["concluded_at"] = datetime.now().isoformat()

        await self._update_test(test)
        await self._save_test_results(test_id, final_results)

        return True

    async def _initialize_test_tracking(self, test: ABTest):
        """Initialize tracking for a new test."""
        # Create tracking tables/structures for the test
        pass

    async def _save_test(self, test: ABTest):
        """Save test to storage."""
        filepath = Path("analytics") / "tests" / f"{test.id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(test.to_dict(), f, indent=2)

    async def _update_test(self, test: ABTest):
        """Update test in storage."""
        await self._save_test(test)

    async def _save_event_data(self, test_id: str, variant_id: str, event_name: str, event_data: Dict[str, Any]):
        """Save event data for analysis."""
        filepath = Path("analytics") / "test_events" / f"{test_id}_{variant_id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Load existing events
        existing_events = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing_events = json.load(f)

        # Add new event
        event_entry = {
            "event_name": event_name,
            "timestamp": datetime.now().isoformat(),
            "event_data": event_data
        }
        existing_events.append(event_entry)

        with open(filepath, 'w') as f:
            json.dump(existing_events, f, indent=2)

    async def _save_test_results(self, test_id: str, results: Dict[str, Any]):
        """Save test results."""
        filepath = Path("analytics") / "test_results" / f"{test_id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)


# Global A/B test manager instance
ab_test_manager = ABTestManager()


class ABTestService:
    """Service for managing A/B tests and experiments."""

    @staticmethod
    async def create_feature_test(test_data: Dict[str, Any], created_by: str) -> ABTest:
        """Create a feature A/B test."""
        return await ab_test_manager.create_test(test_data, created_by)

    @staticmethod
    async def create_ui_test(test_data: Dict[str, Any], created_by: str) -> ABTest:
        """Create a UI A/B test."""
        return await ab_test_manager.create_test(test_data, created_by)

    @staticmethod
    async def get_variant(test_id: str, user_id: str) -> Optional[str]:
        """Get variant assignment for user."""
        return ab_test_manager.get_variant_for_user(test_id, user_id)

    @staticmethod
    async def track_test_event(test_id: str, user_id: str, event_name: str, event_data: Dict[str, Any]):
        """Track an event for A/B test analysis."""
        await ab_test_manager.track_event(test_id, user_id, event_name, event_data)

    @staticmethod
    async def get_test_results(test_id: str) -> Dict[str, Any]:
        """Get A/B test results."""
        return await ab_test_manager.get_test_results(test_id)

    @staticmethod
    async def conclude_test(test_id: str, conclusion: str, implemented: bool = False):
        """Conclude an A/B test."""
        return await ab_test_manager.conclude_test(test_id, conclusion, implemented)

    @staticmethod
    async def create_sample_tests(created_by: str):
        """Create sample A/B tests for demonstration."""
        tests = [
            {
                "name": "New Dashboard Layout",
                "description": "Test new dashboard layout for improved user engagement",
                "test_type": "ui_change",
                "hypothesis": "The new dashboard layout will increase user engagement by 20%",
                "variants": [
                    {
                        "name": "Control",
                        "description": "Current dashboard layout",
                        "configuration": {"layout": "current"},
                        "percentage": 50,
                        "is_control": True
                    },
                    {
                        "name": "New Layout",
                        "description": "New dashboard layout with improved organization",
                        "configuration": {"layout": "new"},
                        "percentage": 50,
                        "is_control": False
                    }
                ],
                "primary_metric": "engagement",
                "secondary_metrics": ["performance", "usability"],
                "target_audience": {"user_type": "active"},
                "created_by": created_by
            },
            {
                "name": "Simplified Onboarding",
                "description": "Test simplified onboarding flow to improve conversion",
                "test_type": "workflow_test",
                "hypothesis": "Simplified onboarding will increase trial-to-paid conversion by 15%",
                "variants": [
                    {
                        "name": "Current Onboarding",
                        "description": "Current multi-step onboarding",
                        "configuration": {"steps": 5},
                        "percentage": 50,
                        "is_control": True
                    },
                    {
                        "name": "Simplified Onboarding",
                        "description": "Streamlined 3-step onboarding",
                        "configuration": {"steps": 3},
                        "percentage": 50,
                        "is_control": False
                    }
                ],
                "primary_metric": "conversion",
                "secondary_metrics": ["engagement", "retention"],
                "target_audience": {"user_type": "trial"},
                "created_by": created_by
            }
        ]

        created_tests = []
        for test_data in tests:
            test = await ab_test_manager.create_test(test_data, created_by)
            created_tests.append(test)

        # Start the tests
        for test in created_tests:
            await ab_test_manager.start_test(test.id)

        return created_tests

    @staticmethod
    async def get_all_tests() -> List[ABTest]:
        """Get all A/B tests."""
        return list(ab_test_manager.active_tests.values())

    @staticmethod
    async def get_running_tests() -> List[ABTest]:
        """Get currently running tests."""
        return [test for test in ab_test_manager.active_tests.values()
                if test.status == TestStatus.RUNNING]
