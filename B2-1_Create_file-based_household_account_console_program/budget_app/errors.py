from __future__ import annotations

from typing import Optional


class AppError(Exception):
    """User-facing application error with an optional hint."""

    def __init__(self, message: str, hint: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
