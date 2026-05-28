from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

R = TypeVar("R")

logger = logging.getLogger("budget_app")


def log_timing(func: Callable[..., R]) -> Callable[..., R]:
    """Log command execution time without mixing timing code into CLI logic."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.info("%s completed in %.2fms", func.__name__, elapsed_ms)

    return wrapper
