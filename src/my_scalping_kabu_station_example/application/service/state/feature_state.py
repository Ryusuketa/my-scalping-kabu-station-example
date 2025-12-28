"""State for feature computation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from my_scalping_kabu_station_example.domain.market.time import Timestamp


@dataclass
class FeatureState:
    last_ts: Optional[Timestamp] = None
    ema_values: Dict[str, float] = field(default_factory=dict)
