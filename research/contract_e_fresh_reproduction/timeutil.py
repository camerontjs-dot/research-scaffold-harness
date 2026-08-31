"""Timestamp comparison helpers. Bound inclusivity is assumption T1."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def parse_time(value: Any) -> datetime | str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return _canon(value)
    if not isinstance(value, str):
        return str(value)
    text = value.replace("Z", "+00:00")
    try:
        return _canon(datetime.fromisoformat(text))
    except ValueError:
        return value


def _canon(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def time_leq(left: Any, right: Any) -> bool:
    pl, pr = parse_time(left), parse_time(right)
    if pl is None or pr is None:
        return False
    try:
        return pl <= pr  # type: ignore[operator]
    except TypeError:
        return str(left) <= str(right)


def in_interval(evaluated_at: Any, valid_from: Any, valid_until: Any) -> bool:
    """Inclusive interval membership (assumption T1)."""
    if evaluated_at is None or valid_from is None or valid_until is None:
        return False
    return time_leq(valid_from, evaluated_at) and time_leq(evaluated_at, valid_until)
