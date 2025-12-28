"""Training pipeline skeleton."""

from __future__ import annotations

from typing import Iterable

from ...ports.feature_engine import FeatureEnginePort
from ...ports.history import HistoryStorePort
from ...ports.model import ModelStorePort, ModelTrainerPort
from ....domain.features.spec import FeatureSpec
from ....domain.market.orderbook_snapshot import OrderBookSnapshot


class TrainingPipeline:
    def __init__(
        self,
        history_store: HistoryStorePort,
        feature_engine: FeatureEnginePort,
        trainer: ModelTrainerPort,
        model_store: ModelStorePort,
    ) -> None:
        self.history_store = history_store
        self.feature_engine = feature_engine
        self.trainer = trainer
        self.model_store = model_store

    def run(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]) -> None:
        raise NotImplementedError
