"""Load testing suite for LegalEdge platform."""

from locust import HttpUser, task, between, tag
from locust.contrib.fasthttp import FastHttpUser
import json
import random
import string
from datetime import datetime


class LegalEdgeUser(HttpUser):
    """Base user class for LegalEdge load testing."""

    wait_time = between(1, 5)

    def on_start(self):
        """Setup when user starts."""
        self.registered = False
        self.token = None
        self.user_id = None
        self.portfolio_ids = []
        self.alert_config_ids = []

    def _generate_random_string(self, length=8):
        """Generate random string."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _register_user(self):
        """Register a new user."""
        username = f"loadtest_{self._generate_random_string()}"
        email = f"{username}@example.com"

        user_data = {
            "email": email,
            "username": username,
            "password": "password123",
            "full_name": f"Load Test User {username}"
        }

        response = self.client.post("/auth/register", json=user_data)
        if response.status_code == 201:
            self.registered = True
            # Login to get token
            login_response = self.client.post("/auth/login", data={
                "username": email,
                "password": "password123"
            })
            if login_response.status_code == 200:
                self.token = login_response.json()["access_token"]
                self.user_id = response.json()["id"]
            return True
        return False

    def _ensure_authenticated(self):
        """Ensure user is authenticated."""
        if not self.registered:
            return self._register_user()
        return True


class AuthLoadUser(LegalEdgeUser):
    """Load testing for authentication endpoints."""

    @tag("auth")
    @task(3)
    def register_user(self):
        """Load test user registration."""
        username = f"loadtest_{self._generate_random_string()}"
        email = f"{username}@example.com"

        user_data = {
            "email": email,
            "username": username,
            "password": "password123",
            "full_name": f"Load Test User {username}"
        }

        with self.client.post("/auth/register", json=user_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 400:
                # User already exists - that's ok for load testing
                response.success()

    @tag("auth")
    @task(5)
    def login_user(self):
        """Load test user login."""
        # Use existing user credentials
        login_data = {
            "username": "loadtest_admin@example.com",  # This should be pre-created
            "password": "password123"
        }

        with self.client.post("/auth/login", data=login_data, catch_response=True) as response:
            if response.status_code in [200, 401]:  # 401 is ok for load testing
                response.success()

    @tag("auth")
    @task(2)
    def get_current_user(self):
        """Load test getting current user."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.get("/auth/me", headers=headers, catch_response=True) as response:
                if response.status_code in [200, 401]:
                    response.success()

    @tag("auth")
    @task(1)
    def refresh_token(self):
        """Load test token refresh."""
        if self._ensure_authenticated():
            # Get refresh token (simulated - in real test would need to store it)
            refresh_data = {"refresh_token": "dummy_refresh_token"}
            with self.client.post("/auth/refresh", json=refresh_data, catch_response=True) as response:
                if response.status_code in [200, 401]:
                    response.success()


class LegislationLoadUser(LegalEdgeUser):
    """Load testing for legislation endpoints."""

    @tag("legislation")
    @task(4)
    def list_legislation(self):
        """Load test listing legislation."""
        params = {
            "limit": random.randint(10, 50),
            "offset": random.randint(0, 100)
        }

        with self.client.get("/legislation/", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()

    @tag("legislation")
    @task(3)
    def search_legislation(self):
        """Load test searching legislation."""
        search_terms = [
            "artificial intelligence",
            "healthcare",
            "finance",
            "technology",
            "regulation",
            "environment"
        ]

        params = {
            "query": random.choice(search_terms),
            "jurisdiction": random.choice(["federal", "california", "texas", "new_york"]),
            "limit": random.randint(10, 30)
        }

        with self.client.get("/legislation/search", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()

    @tag("legislation")
    @task(2)
    def get_legislation_by_topics(self):
        """Load test getting legislation by topics."""
        topics_list = [
            ["artificial intelligence", "technology"],
            ["healthcare", "regulation"],
            ["finance", "banking"],
            ["environment", "climate"],
            ["education", "funding"]
        ]

        topics = random.choice(topics_list)
        with self.client.get(f"/legislation/topics/{','.join(topics)}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()

    @tag("legislation")
    @task(2)
    def get_legislation_by_jurisdiction(self):
        """Load test getting legislation by jurisdiction."""
        jurisdictions = ["federal", "california", "texas", "new_york", "florida"]

        with self.client.get(f"/legislation/jurisdiction/{random.choice(jurisdictions)}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()


class PortfolioLoadUser(LegalEdgeUser):
    """Load testing for portfolio endpoints."""

    @tag("portfolio")
    @task(3)
    def create_portfolio(self):
        """Load test creating portfolios."""
        if self._ensure_authenticated():
            portfolio_data = {
                "name": f"Load Test Portfolio {self._generate_random_string()}",
                "description": f"Portfolio for load testing by user {self.user_id}",
                "tickers": random.sample(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "AMD", "INTC"], random.randint(3, 8))
            }

            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.post("/portfolios/", json=portfolio_data, headers=headers, catch_response=True) as response:
                if response.status_code in [201, 400]:  # 400 might be validation error
                    response.success()

    @tag("portfolio")
    @task(4)
    def list_portfolios(self):
        """Load test listing portfolios."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.get("/portfolios/", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()

    @tag("portfolio")
    @task(2)
    def get_portfolio(self):
        """Load test getting individual portfolios."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            # Get random portfolio ID (in real test, would need to track created portfolios)
            portfolio_id = f"load-test-portfolio-{random.randint(1, 1000)}"
            with self.client.get(f"/portfolios/{portfolio_id}", headers=headers, catch_response=True) as response:
                if response.status_code in [200, 404]:  # 404 is ok for load testing
                    response.success()

    @tag("portfolio")
    @task(1)
    def update_portfolio(self):
        """Load test updating portfolios."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            # Update random portfolio ID
            portfolio_id = f"load-test-portfolio-{random.randint(1, 1000)}"

            update_data = {
                "name": f"Updated Portfolio {self._generate_random_string()}",
                "description": "Updated via load test",
                "tickers": random.sample(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"], random.randint(2, 6))
            }

            with self.client.put(f"/portfolios/{portfolio_id}", json=update_data, headers=headers, catch_response=True) as response:
                if response.status_code in [200, 404, 400]:
                    response.success()


class AlertsLoadUser(LegalEdgeUser):
    """Load testing for alerts endpoints."""

    @tag("alerts")
    @task(3)
    def create_alert_config(self):
        """Load test creating alert configurations."""
        if self._ensure_authenticated():
            alert_config_data = {
                "name": f"Load Test Alert {self._generate_random_string()}",
                "description": f"Alert configuration for load testing by user {self.user_id}",
                "keywords": random.sample(["artificial intelligence", "healthcare", "finance", "technology", "regulation"], random.randint(2, 5)),
                "jurisdictions": random.sample(["federal", "california", "texas", "new_york", "florida"], random.randint(1, 3)),
                "severity_threshold": random.choice(["low", "medium", "high"]),
                "notification_channels": random.sample(["email", "webhook", "sms"], random.randint(1, 3))
            }

            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.post("/alerts/config", json=alert_config_data, headers=headers, catch_response=True) as response:
                if response.status_code in [201, 400]:
                    response.success()

    @tag("alerts")
    @task(4)
    def get_alerts_feed(self):
        """Load test getting alerts feed."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {
                "limit": random.randint(10, 50),
                "offset": random.randint(0, 100)
            }

            with self.client.get("/alerts/feed", params=params, headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()

    @tag("alerts")
    @task(2)
    def get_alert_configs(self):
        """Load test getting alert configurations."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.get("/alerts/config", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()

    @tag("alerts")
    @task(1)
    def update_alert_config(self):
        """Load test updating alert configurations."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            # Update random config ID
            config_id = f"load-test-alert-config-{random.randint(1, 1000)}"

            update_data = {
                "name": f"Updated Alert Config {self._generate_random_string()}",
                "description": "Updated via load test",
                "keywords": random.sample(["artificial intelligence", "healthcare", "finance"], random.randint(2, 4)),
                "jurisdictions": random.sample(["federal", "california", "texas"], random.randint(1, 2)),
                "severity_threshold": random.choice(["low", "medium", "high"]),
                "notification_channels": random.sample(["email", "webhook", "sms"], random.randint(1, 3))
            }

            with self.client.put(f"/alerts/config/{config_id}", json=update_data, headers=headers, catch_response=True) as response:
                if response.status_code in [200, 404, 400]:
                    response.success()


class DashboardLoadUser(LegalEdgeUser):
    """Load testing for dashboard endpoints."""

    @tag("dashboard")
    @task(4)
    def get_dashboard_overview(self):
        """Load test getting dashboard overview."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.get("/dashboard/overview", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()

    @tag("dashboard")
    @task(3)
    def get_coverage_metrics(self):
        """Load test getting coverage metrics."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.get("/dashboard/coverage", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()

    @tag("dashboard")
    @task(2)
    def get_opportunities(self):
        """Load test getting opportunities."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {
                "limit": random.randint(10, 50),
                "min_confidence": random.uniform(0.5, 0.9)
            }

            with self.client.get("/dashboard/opportunities", params=params, headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()

    @tag("dashboard")
    @task(1)
    def get_forecasts(self):
        """Load test getting forecasts."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            tickers = random.sample(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"], random.randint(1, 3))
            params = {
                "tickers": ",".join(tickers),
                "days_ahead": random.randint(7, 90)
            }

            with self.client.get("/dashboard/forecasts", params=params, headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()


class HealthCheckLoadUser(LegalEdgeUser):
    """Load testing for health check endpoints."""

    @tag("health")
    @task(5)
    def health_check(self):
        """Load test health check endpoint."""
        with self.client.get("/health/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()

    @tag("health")
    @task(3)
    def readiness_check(self):
        """Load test readiness check endpoint."""
        with self.client.get("/health/readiness", catch_response=True) as response:
            if response.status_code == 200:
                response.success()

    @tag("health")
    @task(2)
    def liveness_check(self):
        """Load test liveness check endpoint."""
        with self.client.get("/health/liveness", catch_response=True) as response:
            if response.status_code == 200:
                response.success()


class MixedWorkloadUser(LegalEdgeUser):
    """Mixed workload user that performs various operations."""

    @tag("mixed")
    @task(2)
    def mixed_auth_operations(self):
        """Perform mixed authentication operations."""
        if random.random() < 0.6:  # 60% register
            self.register_user()
        else:  # 40% login
            self.login_user()

    @tag("mixed")
    @task(3)
    def mixed_legislation_operations(self):
        """Perform mixed legislation operations."""
        operations = [
            self.list_legislation,
            self.search_legislation,
            self.get_legislation_by_topics,
            self.get_legislation_by_jurisdiction
        ]
        random.choice(operations)()

    @tag("mixed")
    @task(2)
    def mixed_portfolio_operations(self):
        """Perform mixed portfolio operations."""
        if self._ensure_authenticated():
            operations = [
                lambda: self.create_portfolio(),
                lambda: self.list_portfolios(),
                lambda: self.get_portfolio(),
                lambda: self.update_portfolio()
            ]
            random.choice(operations)()

    @tag("mixed")
    @task(1)
    def mixed_alerts_operations(self):
        """Perform mixed alerts operations."""
        if self._ensure_authenticated():
            operations = [
                lambda: self.create_alert_config(),
                lambda: self.get_alerts_feed(),
                lambda: self.get_alert_configs(),
                lambda: self.update_alert_config()
            ]
            random.choice(operations)()

    @tag("mixed")
    @task(1)
    def health_operations(self):
        """Perform health check operations."""
        operations = [
            self.health_check,
            self.readiness_check,
            self.liveness_check
        ]
        random.choice(operations)()


# Performance testing scenarios
class PerformanceUser(FastHttpUser):
    """High-performance user for stress testing."""

    wait_time = between(0.1, 0.5)  # Very fast requests

    @task
    def stress_test_health(self):
        """Stress test health endpoints."""
        self.client.get("/health/")


class SpikeUser(LegalEdgeUser):
    """User for spike testing."""

    wait_time = between(0.01, 0.1)  # Very fast

    @task
    def spike_test_search(self):
        """Spike test search functionality."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"query": "artificial intelligence", "limit": 10}
            self.client.get("/legislation/search", params=params, headers=headers)


# Load testing scenarios
class IngestionLoadUser(LegalEdgeUser):
    """Load testing for ingestion system."""

    @tag("ingestion")
    @task
    def simulate_data_ingestion(self):
        """Simulate high-volume data ingestion."""
        # This would typically trigger background ingestion tasks
        # For load testing, we simulate the API calls that would trigger ingestion

        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}

            # Simulate triggering ingestion for multiple sources
            sources = ["congress_gov", "sec_forms", "news_feeds", "state_portals"]

            for source in sources:
                with self.client.post(f"/ingestion/trigger/{source}", headers=headers, catch_response=True) as response:
                    if response.status_code in [200, 202, 404]:  # 404 ok for load testing
                        response.success()


class AlertsLoadUser(LegalEdgeUser):
    """Load testing for alerts system."""

    @tag("alerts")
    @task
    def simulate_alert_generation(self):
        """Simulate high-volume alert generation."""
        if self._ensure_authenticated():
            headers = {"Authorization": f"Bearer {self.token}"}

            # Simulate generating alerts for different categories
            categories = ["legislation", "market", "portfolio", "system"]

            for category in categories:
                alert_data = {
                    "title": f"Load Test Alert {category}",
                    "message": f"Simulated alert for {category} testing",
                    "severity": random.choice(["low", "medium", "high"]),
                    "category": category,
                    "user_id": self.user_id
                }

                with self.client.post("/alerts/generate", json=alert_data, headers=headers, catch_response=True) as response:
                    if response.status_code in [201, 400]:  # 400 ok for load testing
                        response.success()
