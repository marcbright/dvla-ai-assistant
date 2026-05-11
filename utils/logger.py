"""Centralized Loguru configuration for the DVLA AI Assistant.

This module configures a single logger instance with rotating file output
and a consistent format suitable for tracing requests and responses.
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger as _loguru_logger

from config.settings import settings

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

_log_level = settings.LOG_LEVEL

_loguru_logger.remove()
_loguru_logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {message}",
    level=_log_level,
)
_loguru_logger.add(
    LOGS_DIR / "dvla-assistant.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {message}",
    level=_log_level,
)
_loguru_logger.add(
    LOGS_DIR / "audit.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | AUDIT | {module} | {message}",
    level="INFO",
    filter=lambda record: record["extra"].get("audit_event") is True,
)


def log_audit(message: str) -> None:
    """Write a safety or compliance event to the audit log file."""
    _loguru_logger.bind(audit_event=True).info(message)


# Shared logger imported throughout the application.
logger = _loguru_logger
