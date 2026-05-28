from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from budget_app.errors import AppError

VALID_TYPES = {"income", "expense"}


def parse_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise AppError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).", "예: 2024-01-15") from exc
    return value


def parse_month(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise AppError("월 형식이 올바르지 않습니다 (YYYY-MM).", "예: 2024-01") from exc
    return value


def parse_amount(value: Union[str, int]) -> int:
    try:
        amount = int(value)
    except (TypeError, ValueError) as exc:
        raise AppError("금액은 양수 정수여야 합니다.", "예: 15000") from exc
    if amount <= 0:
        raise AppError("금액은 0보다 커야 합니다.", "예: 15000")
    return amount


def parse_type(value: str) -> str:
    if value not in VALID_TYPES:
        raise AppError("타입은 income 또는 expense만 가능합니다.", "예: expense")
    return value


def parse_tags(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [tag.strip() for tag in value.split(",") if tag.strip()]
