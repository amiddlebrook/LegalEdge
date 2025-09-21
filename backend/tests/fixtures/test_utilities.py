"""Test utilities and fixtures for LegalEdge testing suite."""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Generator
from unittest.mock import Mock, MagicMock, AsyncMock
import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.session import get_db
from app.main import app
from app.models import Base


class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def generate_legislation_data(num_bills: int = 10) -> List[Dict[str, Any]]:
        """Generate test legislation data."""
        base_date = datetime.now() - timedelta(days=30)

        legislation_data = []
        for i in range(num_bills):
            bill = {
                "id": f"test-bill-{i"03d"}",
                "title": f"Test Bill {i} - {['AI Regulation', 'Healthcare Reform', 'Finance Bill', 'Environmental Act'][i % 4]}",
                "summary": f"This is a test bill {i} for testing purposes.",
                "status": ["introduced", "passed", "failed", "pending"][i % 4],
                "jurisdiction": ["federal", "california", "texas", "new_york"][i % 4],
                "bill_number": f"HB-{1000 + i}",
                "introduced_date": (base_date + timedelta(days=i)).date().isoformat(),
                "sponsors": [f"Rep. Test Sponsor {i % 3}"],
                "topics": [["artificial intelligence", "technology"], ["healthcare", "regulation"], ["finance", "banking"], ["environment", "climate"]][i % 4],
                "sentiment_score": round((i % 10 - 5) / 5.0, 2),  # Range from -1 to 1
                "enactment_probability": round(i % 100 / 100.0, 2),
                "impact_score": round((i % 10 + 1) * 0.8, 1),
                "full_text_url": f"https://example.com/test-bill-{i}"
            }
            legislation_data.append(bill)

        return legislation_data

    @staticmethod
    def generate_portfolio_data(num_portfolios: int = 5, num_users: int = 3) -> List[Dict[str, Any]]:
        """Generate test portfolio data."""
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "AMD", "INTC", "NFLX", "META"]

        portfolios = []
        for i in range(num_portfolios):
            portfolio = {
                "id": f"test-portfolio-{i"03d"}",
                "name": f"Test Portfolio {i}",
                "description": f"A test portfolio {i} for evaluation",
                "user_id": (i % num_users) + 1,
                "tickers": list(set(tickers[j % len(tickers)] for j in range(i + 3, i + 8))),  # 3-5 tickers
                "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "updated_at": (datetime.now() - timedelta(hours=i)).isoformat()
            }
            portfolios.append(portfolio)

        return portfolios

    @staticmethod
    def generate_alert_config_data(num_configs: int = 5) -> List[Dict[str, Any]]:
        """Generate test alert configuration data."""
        alert_configs = []
        for i in range(num_configs):
            config = {
                "id": f"test-alert-config-{i"03d"}",
                "name": f"Test Alert Config {i}",
                "description": f"Alert configuration {i} for testing",
                "keywords": [f"keyword_{j}" for j in range(i + 1, i + 4)],
                "jurisdictions": [["federal", "california"], ["texas", "new_york"], ["florida", "illinois"]][i % 3],
                "severity_threshold": ["low", "medium", "high"][i % 3],
                "notification_channels": [["email", "webhook"], ["email", "sms"], ["webhook", "sms", "email"]][i % 3],
                "user_id": (i % 3) + 1,
                "is_active": i % 4 != 0,  # 75% active
                "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "updated_at": (datetime.now() - timedelta(hours=i)).isoformat()
            }
            alert_configs.append(config)

        return alert_configs

    @staticmethod
    def generate_ml_training_data(data_type: str = "sentiment", num_samples: int = 100) -> Dict[str, Any]:
        """Generate ML training data for testing."""
        if data_type == "sentiment":
            texts = []
            labels = []
            scores = []

            sentiment_patterns = [
                ("positive", ["great", "excellent", "amazing", "good", "fantastic"], 0.8),
                ("negative", ["terrible", "awful", "bad", "horrible", "worst"], -0.7),
                ("neutral", ["okay", "fine", "alright", "moderate", "standard"], 0.1)
            ]

            for i in range(num_samples):
                sentiment, words, base_score = sentiment_patterns[i % 3]
                text = f"This {' '.join(words)} legislation is {' '.join(words)} for the industry."
                score = base_score + (i % 20 - 10) / 100.0  # Add some variation

                texts.append(text)
                labels.append(sentiment)
                scores.append(max(-1.0, min(1.0, score)))  # Clamp to [-1, 1]

            return {"texts": texts, "labels": labels, "scores": scores}

        elif data_type == "forecasting":
            return {
                "tickers": [f"TICKER_{i}" for i in range(num_samples // 10)],
                "features": [[float(j) for j in range(20)] for _ in range(num_samples)],
                "targets": [float(i % 100 + 50) for i in range(num_samples)]
            }

        return {}


class PerformanceTimer:
    """Utility for timing test performance."""

    def __init__(self):
        self.start_times = {}
        self.end_times = {}
        self.measurements = {}

    def start_timer(self, name: str):
        """Start a timer."""
        self.start_times[name] = time.time()

    def end_timer(self, name: str):
        """End a timer."""
        if name in self.start_times:
            self.end_times[name] = time.time()
            duration = self.end_times[name] - self.start_times[name]
            self.measurements[name] = duration
            return duration
        return None

    def get_measurement(self, name: str) -> Optional[float]:
        """Get a measurement."""
        return self.measurements.get(name)

    def get_all_measurements(self) -> Dict[str, float]:
        """Get all measurements."""
        return self.measurements.copy()

    def reset(self):
        """Reset all measurements."""
        self.start_times.clear()
        self.end_times.clear()
        self.measurements.clear()


class AsyncTestClient:
    """Async test client with utilities."""

    def __init__(self, client):
        self.client = client
        self.auth_headers = {}

    async def authenticate(self, email: str, password: str):
        """Authenticate and store token."""
        response = await self.client.post("/auth/login", data={
            "username": email,
            "password": password
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.auth_headers = {"Authorization": f"Bearer {token}"}
        return response

    async def make_authenticated_request(self, method: str, url: str, **kwargs):
        """Make authenticated request."""
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"].update(self.auth_headers)
        return await self.client.request(method, url, **kwargs)

    async def create_test_user(self, user_data: Dict[str, Any]):
        """Create a test user."""
        response = await self.client.post("/auth/register", json=user_data)
        if response.status_code == 201:
            await self.authenticate(user_data["email"], user_data["password"])
        return response


class DatabaseTestUtils:
    """Utilities for database testing."""

    @staticmethod
    async def create_test_database(engine):
        """Create test database tables."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_test_database(engine):
        """Drop test database tables."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def seed_test_data(session: AsyncSession, data_generators: List[Callable]):
        """Seed test database with data."""
        for generator in data_generators:
            data = generator()
            for item in data:
                # This would depend on the actual model structure
                # For now, just a placeholder
                pass
        await session.commit()

    @staticmethod
    async def cleanup_test_data(session: AsyncSession, model_classes: List):
        """Clean up test data."""
        for model_class in model_classes:
            await session.execute(f"DELETE FROM {model_class.__tablename__}")
        await session.commit()


class MockFactory:
    """Factory for creating various types of mocks."""

    @staticmethod
    def create_mock_model():
        """Create a mock ML model."""
        mock = Mock()
        mock.predict.return_value = {"prediction": 0.8, "confidence": 0.9}
        mock.evaluate.return_value = {"accuracy": 0.95, "f1_score": 0.93}
        return mock

    @staticmethod
    def create_mock_external_api():
        """Create a mock external API."""
        mock = Mock()
        mock.get.return_value = Mock(status_code=200, json=lambda: {"data": "test"})
        mock.post.return_value = Mock(status_code=201, json=lambda: {"id": "created"})
        return mock

    @staticmethod
    def create_mock_database():
        """Create a mock database session."""
        mock = AsyncMock()
        mock.commit.return_value = None
        mock.rollback.return_value = None
        mock.close.return_value = None
        return mock

    @staticmethod
    def create_mock_redis():
        """Create a mock Redis client."""
        mock = Mock()
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        mock.exists.return_value = False
        return mock

    @staticmethod
    def create_mock_celery():
        """Create a mock Celery app."""
        mock = Mock()
        mock_task = Mock()
        mock_task.id = "test-task-id"
        mock.send_task.return_value = mock_task
        return mock


class TestMetricsCollector:
    """Collect and analyze test metrics."""

    def __init__(self):
        self.metrics = {
            "test_execution_times": {},
            "test_results": {},
            "memory_usage": {},
            "coverage_data": {}
        }

    def record_test_execution_time(self, test_name: str, duration: float):
        """Record test execution time."""
        self.metrics["test_execution_times"][test_name] = duration

    def record_test_result(self, test_name: str, result: str, details: Optional[Dict] = None):
        """Record test result."""
        self.metrics["test_results"][test_name] = {
            "result": result,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }

    def record_memory_usage(self, test_name: str, memory_mb: float):
        """Record memory usage."""
        self.metrics["memory_usage"][test_name] = memory_mb

    def get_test_summary(self) -> Dict[str, Any]:
        """Get test execution summary."""
        execution_times = self.metrics["test_execution_times"]
        results = self.metrics["test_results"]

        return {
            "total_tests": len(results),
            "passed_tests": len([r for r in results.values() if r["result"] == "passed"]),
            "failed_tests": len([r for r in results.values() if r["result"] == "failed"]),
            "average_execution_time": sum(execution_times.values()) / len(execution_times) if execution_times else 0,
            "longest_test": max(execution_times.items(), key=lambda x: x[1]) if execution_times else None,
            "shortest_test": min(execution_times.items(), key=lambda x: x[1]) if execution_times else None,
        }

    def save_metrics(self, output_path: str):
        """Save metrics to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)

    def load_metrics(self, input_path: str) -> Dict[str, Any]:
        """Load metrics from file."""
        with open(input_path, 'r') as f:
            return json.load(f)


class BenchmarkUtils:
    """Utilities for benchmarking tests."""

    @staticmethod
    async def benchmark_async_function(func: Callable, *args, iterations: int = 10, **kwargs) -> Dict[str, Any]:
        """Benchmark an async function."""
        execution_times = []

        for _ in range(iterations):
            start_time = time.time()
            await func(*args, **kwargs)
            end_time = time.time()
            execution_times.append(end_time - start_time)

        return {
            "iterations": iterations,
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "avg_time": sum(execution_times) / len(execution_times),
            "median_time": sorted(execution_times)[len(execution_times) // 2],
            "std_dev": (sum((t - sum(execution_times) / len(execution_times)) ** 2 for t in execution_times) / len(execution_times)) ** 0.5
        }

    @staticmethod
    def benchmark_sync_function(func: Callable, *args, iterations: int = 10, **kwargs) -> Dict[str, Any]:
        """Benchmark a sync function."""
        execution_times = []

        for _ in range(iterations):
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            execution_times.append(end_time - start_time)

        return {
            "iterations": iterations,
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "avg_time": sum(execution_times) / len(execution_times),
            "median_time": sorted(execution_times)[len(execution_times) // 2],
            "std_dev": (sum((t - sum(execution_times) / len(execution_times)) ** 2 for t in execution_times) / len(execution_times)) ** 0.5
        }


class TestFileManager:
    """Manage test files and directories."""

    def __init__(self, base_dir: str = "test_output"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def create_test_file(self, filename: str, content: str = "") -> Path:
        """Create a test file."""
        file_path = self.base_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)

        return file_path

    def create_test_directory(self, dirname: str) -> Path:
        """Create a test directory."""
        dir_path = self.base_dir / dirname
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def cleanup(self):
        """Clean up test files."""
        import shutil
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)


# Pytest fixtures
@pytest.fixture
def test_data_generator():
    """Fixture for test data generator."""
    return TestDataGenerator()


@pytest.fixture
def performance_timer():
    """Fixture for performance timing."""
    return PerformanceTimer()


@pytest.fixture
def mock_factory():
    """Fixture for mock factory."""
    return MockFactory()


@pytest.fixture
def test_metrics_collector():
    """Fixture for test metrics collector."""
    return TestMetricsCollector()


@pytest.fixture
def benchmark_utils():
    """Fixture for benchmark utilities."""
    return BenchmarkUtils()


@pytest.fixture
def test_file_manager():
    """Fixture for test file manager."""
    manager = TestFileManager()
    yield manager
    manager.cleanup()


# Async fixtures
@pytest.fixture
async def async_test_client(client):
    """Fixture for async test client with utilities."""
    return AsyncTestClient(client)


# Database fixtures
@pytest.fixture
async def test_database():
    """Fixture for test database."""
    database_url = "sqlite+aiosqlite:///./test.db"
    engine = create_async_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# Mock fixtures
@pytest.fixture
def mock_model():
    """Fixture for mock ML model."""
    return MockFactory.create_mock_model()


@pytest.fixture
def mock_external_api():
    """Fixture for mock external API."""
    return MockFactory.create_mock_external_api()


@pytest.fixture
def mock_database():
    """Fixture for mock database."""
    return MockFactory.create_mock_database()


@pytest.fixture
def mock_redis():
    """Fixture for mock Redis."""
    return MockFactory.create_mock_redis()


@pytest.fixture
def mock_celery():
    """Fixture for mock Celery."""
    return MockFactory.create_mock_celery()
