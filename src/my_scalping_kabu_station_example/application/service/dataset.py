"""Dataset builder utilities."""

from __future__ import annotations

from typing import Iterable

from ..ports.feature_engine import FeatureEnginePort
from ..ports.history import HistoryStorePort
from ...domain.features.spec import FeatureSpec
from ...domain.market.orderbook_snapshot import OrderBookSnapshot


class DatasetBuilder:
    def __init__(self, history_store: HistoryStorePort, feature_engine: FeatureEnginePort) -> None:
        self.history_store = history_store
        self.feature_engine = feature_engine

    def build(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]):
        raise NotImplementedError
