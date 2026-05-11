"""Utility package for shared cross-cutting helpers.

This package exposes reusable tools, including a shared structured logger
instance consumed across the application.
"""

from .logger import logger

__all__ = ["logger"]
