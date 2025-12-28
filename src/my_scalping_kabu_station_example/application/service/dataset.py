"""Dataset builder utilities."""

from __future__ import annotations

from typing import Iterable

from my_scalping_kabu_station_example.application.ports.feature_engine import FeatureEnginePort
from my_scalping_kabu_station_example.application.ports.history import HistoryStorePort
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot


class DatasetBuilder:
    def __init__(self, history_store: HistoryStorePort, feature_engine: FeatureEnginePort) -> None:
        self.history_store = history_store
        self.feature_engine = feature_engine

    def build(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]):
        """Compute feature vectors for the provided snapshots."""

        return list(self.feature_engine.compute_batch(spec, snapshots))
