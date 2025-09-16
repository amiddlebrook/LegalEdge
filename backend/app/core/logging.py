"""Logging configuration for LegalEdge services."""
import logging
from typing import Iterable

from loguru import logger


class InterceptHandler(logging.Handler):
    """Redirect standard logging records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def configure_logging(extra_loggers: Iterable[str] | None = None) -> None:
    """Wire standard logging modules into Loguru."""

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
    targets = {"uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"}
    if extra_loggers:
        targets.update(extra_loggers)

    for name in targets:
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False

    logger.debug("Loguru intercept configured for %s", ", ".join(sorted(targets)))