"""Feature state for streaming calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class FeatureState:
    """Holds previous timestamp and EMA values."""

    last_ts: Optional[datetime] = None
    ema_values: Dict[str, float] = field(default_factory=dict)

    def with_updated_ema(self, name: str, value: float) -> "FeatureState":
        """Return a new state with an updated EMA entry (implementation pending)."""
        new_values = dict(self.ema_values)
        new_values[name] = value
        return FeatureState(last_ts=self.last_ts, ema_values=new_values)
