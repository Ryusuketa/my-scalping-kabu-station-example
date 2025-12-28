"""Streaming state combining previous snapshot and feature state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)
from application.service.state.feature_state import (
    FeatureState,
)


@dataclass
class StreamState:
    prev_snapshot: Optional[OrderBookSnapshot] = None
    feature_state: FeatureState = field(default_factory=FeatureState)
