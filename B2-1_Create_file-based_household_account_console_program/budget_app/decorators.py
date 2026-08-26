from __future__ import annotations

import functools
import logging
import time

logger = logging.getLogger("budget_app")


def log_timing(func):
    """명령 실행 시간을 로그에 기록한다."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.info("%s completed in %.2fms", func.__name__, elapsed_ms)

    return wrapper
