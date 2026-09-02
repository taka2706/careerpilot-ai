"""Simple, process-wide logging configuration."""

import logging
from logging.config import dictConfig


def configure_logging(log_level: str) -> None:
    """Configure consistent console logs without recording sensitive request data."""

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": log_level,
                }
            },
            "root": {"handlers": ["console"], "level": log_level},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger after application configuration."""

    return logging.getLogger(name)
