"""Locust configuration file for load testing."""

import os
from locust import HttpUser
from tests.load.test_load_scenarios import (
    AuthLoadUser,
    LegislationLoadUser,
    PortfolioLoadUser,
    AlertsLoadUser,
    DashboardLoadUser,
    HealthCheckLoadUser,
    MixedWorkloadUser,
    PerformanceUser,
    SpikeUser,
    IngestionLoadUser
)


# Load test configuration
HOST = os.getenv("LOCUST_HOST", "http://localhost:8000")
USERS = int(os.getenv("LOCUST_USERS", "100"))
HATCH_RATE = int(os.getenv("LOCUST_HATCH_RATE", "10"))
RUN_TIME = os.getenv("LOCUST_RUN_TIME", "5m")


# User classes for different load testing scenarios
USER_CLASSES = [
    AuthLoadUser,
    LegislationLoadUser,
    PortfolioLoadUser,
    AlertsLoadUser,
    DashboardLoadUser,
    HealthCheckLoadUser,
    MixedWorkloadUser,
    PerformanceUser,
    SpikeUser,
    IngestionLoadUser
]


# Load testing scenarios with different configurations
SCENARIOS = {
    "smoke_test": {
        "users": 5,
        "hatch_rate": 1,
        "run_time": "30s",
        "user_classes": [HealthCheckLoadUser, AuthLoadUser]
    },

    "authentication_load": {
        "users": 50,
        "hatch_rate": 5,
        "run_time": "2m",
        "user_classes": [AuthLoadUser]
    },

    "legislation_load": {
        "users": 100,
        "hatch_rate": 10,
        "run_time": "3m",
        "user_classes": [LegislationLoadUser]
    },

    "portfolio_load": {
        "users": 75,
        "hatch_rate": 8,
        "run_time": "2m",
        "user_classes": [PortfolioLoadUser]
    },

    "alerts_load": {
        "users": 60,
        "hatch_rate": 6,
        "run_time": "2m",
        "user_classes": [AlertsLoadUser]
    },

    "mixed_workload": {
        "users": 200,
        "hatch_rate": 20,
        "run_time": "5m",
        "user_classes": [MixedWorkloadUser]
    },

    "performance_test": {
        "users": 500,
        "hatch_rate": 50,
        "run_time": "1m",
        "user_classes": [PerformanceUser]
    },

    "spike_test": {
        "users": 1000,
        "hatch_rate": 100,
        "run_time": "30s",
        "user_classes": [SpikeUser]
    },

    "ingestion_load": {
        "users": 30,
        "hatch_rate": 3,
        "run_time": "10m",
        "user_classes": [IngestionLoadUser]
    },

    "comprehensive_load": {
        "users": 300,
        "hatch_rate": 30,
        "run_time": "10m",
        "user_classes": USER_CLASSES
    }
}


def get_scenario_config(scenario_name: str = None):
    """Get configuration for a specific scenario."""
    if scenario_name and scenario_name in SCENARIOS:
        return SCENARIOS[scenario_name]
    return {
        "users": USERS,
        "hatch_rate": HATCH_RATE,
        "run_time": RUN_TIME,
        "user_classes": USER_CLASSES
    }
