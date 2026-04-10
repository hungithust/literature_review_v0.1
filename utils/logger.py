"""
Structured logging setup for AI SOTA Radar.
"""

import logging
import sys

from config import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """Create a configured logger instance.

    Args:
        name: Logger name, typically the module name (e.g., __name__).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    return logger
