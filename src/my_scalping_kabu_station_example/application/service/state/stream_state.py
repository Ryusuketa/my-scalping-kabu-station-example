"""Streaming state combining previous snapshot and feature state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.application.service.state.feature_state import FeatureState


@dataclass
class StreamState:
    prev_snapshot: Optional[OrderBookSnapshot] = None
    feature_state: FeatureState = field(default_factory=FeatureState)
