import logging
import sys

from api.core.config import settings


def setup_logging() -> None:
    """
    Configure global logging for the application.
    Sets log level based on DEBUG setting and formats log output for readability.
    """
    format_string = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format=format_string,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger instance for the given module or component name.
    Use this to log messages with context of the caller.
    """
    return logging.getLogger(name)
