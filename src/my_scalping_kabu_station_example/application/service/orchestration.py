"""Orchestration helpers."""

from __future__ import annotations


def retryable(fn, retries: int = 3):
    """Placeholder retry decorator."""

    def wrapper(*args, **kwargs):
        last_exc = None
        for _ in range(retries):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
        raise last_exc

    return wrapper
