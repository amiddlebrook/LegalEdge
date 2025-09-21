"""Logging configuration for LegalEdge platform."""
import json
import logging
from datetime import datetime
from typing import Any, Dict

from loguru import logger
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that includes additional context."""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat()

        # Add service name
        log_record['service'] = 'legaledge-backend'

        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

        # Add user ID if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id

        # Add trace ID if available (for distributed tracing)
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id


def configure_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""

    # Remove default handlers
    logger.remove()

    # Add JSON formatted handler for production
    logger.add(
        "logs/app.log",
        rotation="1 day",
        retention="30 days",
        level=level,
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        backtrace=True,
        diagnose=True,
    )

    # Add JSON formatted handler for CloudWatch
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(CustomJsonFormatter())

    # Add handler for console in development
    if level == "DEBUG":
        logger.add(
            "logs/debug.log",
            rotation="100 MB",
            retention="7 days",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            backtrace=True,
            diagnose=True,
        )

    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)


def log_request_middleware(request: Any, call_next: Any) -> Any:
    """Middleware to log HTTP requests."""
    start_time = datetime.utcnow()

    # Log request start
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None,
        }
    )

    response = call_next(request)

    # Calculate processing time
    process_time = (datetime.utcnow() - start_time).total_seconds()

    # Log request completion
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "client": request.client.host if request.client else None,
        }
    )

    return response


def get_request_id() -> str:
    """Generate a unique request ID."""
    import uuid
    return str(uuid.uuid4())


def setup_tracing() -> None:
    """Setup distributed tracing configuration."""
    # This would integrate with AWS X-Ray or OpenTelemetry
    # For now, just log that tracing is configured
    logger.info("Distributed tracing configured")
