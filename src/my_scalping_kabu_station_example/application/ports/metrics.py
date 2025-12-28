"""Metrics abstraction."""

from __future__ import annotations

from typing import Protocol


class MetricsPort(Protocol):
    def incr(self, name: str, value: int = 1) -> None:
        ...

    def timing(self, name: str, value_ms: float) -> None:
        ...
