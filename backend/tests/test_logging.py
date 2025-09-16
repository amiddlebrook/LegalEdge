import logging

from app.core.logging import InterceptHandler, configure_logging
from loguru import logger


def test_configure_logging_routes_standard_logs():
    messages = []
    logger.remove()
    logger.add(lambda msg: messages.append(msg), format="{message}")

    configure_logging(extra_loggers=["test"])

    logging.getLogger("test").info("hello world")

    assert any("hello world" in message for message in messages)
    assert any(isinstance(handler, InterceptHandler) for handler in logging.getLogger("test").handlers)