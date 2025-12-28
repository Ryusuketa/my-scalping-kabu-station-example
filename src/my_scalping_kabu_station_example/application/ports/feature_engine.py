"""Feature computation port."""

from __future__ import annotations

from typing import Dict, Iterable, Protocol, Tuple

from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.application.service.state.feature_state import FeatureState

FeatureVector = Dict[str, float]
FeatureTable = Iterable[FeatureVector]


class FeatureEnginePort(Protocol):
    def compute_one(
        self,
        spec: FeatureSpec,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState | None,
    ) -> Tuple[FeatureVector, FeatureState]:
        ...

    def compute_batch(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]) -> FeatureTable:
        ...
