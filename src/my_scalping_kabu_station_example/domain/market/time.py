"""Time utilities and domain-specific wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import exp
from typing import NewType

Timestamp = NewType("Timestamp", datetime)
Duration = NewType("Duration", timedelta)


def utc_now() -> Timestamp:
    """Return a timezone-aware UTC timestamp."""

    return Timestamp(datetime.now(timezone.utc))


def to_duration(seconds: float) -> Duration:
    """Create a duration from seconds."""

    return Duration(timedelta(seconds=seconds))


def delta_seconds(later: Timestamp, earlier: Timestamp) -> float:
    """Compute fractional seconds between two timestamps."""

    return (later - earlier).total_seconds()


@dataclass(frozen=True)
class TimeDecay:
    """Continuous-time decay constant."""

    tau_seconds: float

    def __post_init__(self) -> None:
        if self.tau_seconds <= 0:
            raise ValueError("tau_seconds must be positive")

    def alpha(self, delta_t_seconds: float) -> float:
        """Compute alpha for EMA update based on time delta."""

        if delta_t_seconds < 0:
            raise ValueError("delta_t_seconds must be non-negative")
        return 1 - exp(-delta_t_seconds / self.tau_seconds)
