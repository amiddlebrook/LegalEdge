"""Metrics and monitoring configuration."""
import time
from contextlib import contextmanager
from typing import Generator

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil

# Define metrics
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active database connections'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Current memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Current CPU usage percentage'
)

DB_CONNECTION_POOL_SIZE = Gauge(
    'db_connection_pool_size',
    'Database connection pool size'
)

CACHE_HIT_RATIO = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio (0.0 to 1.0)'
)


class MetricsCollector:
    """Collect and expose application metrics."""

    def __init__(self):
        self.start_time = time.time()

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float) -> None:
        """Record an HTTP request."""
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def update_connection_count(self, count: int) -> None:
        """Update active connection count."""
        ACTIVE_CONNECTIONS.set(count)

    def update_system_metrics(self) -> None:
        """Update system-level metrics."""
        # Memory usage
        memory = psutil.virtual_memory()
        MEMORY_USAGE.set(memory.used)

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        CPU_USAGE.set(cpu_percent)

    def update_db_metrics(self, pool_size: int, active_connections: int) -> None:
        """Update database metrics."""
        DB_CONNECTION_POOL_SIZE.set(pool_size)
        ACTIVE_CONNECTIONS.set(active_connections)

    def update_cache_metrics(self, hits: int, misses: int) -> None:
        """Update cache metrics."""
        total = hits + misses
        if total > 0:
            CACHE_HIT_RATIO.set(hits / total)


# Global metrics collector
metrics_collector = MetricsCollector()


@contextmanager
def timer(metric: Histogram, method: str, endpoint: str) -> Generator[None, None, None]:
    """Context manager to time operations."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        metric.labels(method=method, endpoint=endpoint).observe(duration)


def start_metrics_server(port: int = 9090) -> None:
    """Start the Prometheus metrics server."""
    start_http_server(port)
    print(f"Metrics server started on port {port}")


def get_uptime() -> float:
    """Get application uptime in seconds."""
    return time.time() - metrics_collector.start_time


def get_health_status() -> dict:
    """Get application health status."""
    return {
        "status": "healthy",
        "uptime_seconds": get_uptime(),
        "timestamp": time.time(),
    }
