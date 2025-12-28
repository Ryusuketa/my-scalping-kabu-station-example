"""Training pipeline skeleton."""

from __future__ import annotations

from typing import Iterable

from my_scalping_kabu_station_example.application.ports.feature_engine import FeatureEnginePort
from my_scalping_kabu_station_example.application.ports.history import HistoryStorePort
from my_scalping_kabu_station_example.application.ports.model import ModelStorePort, ModelTrainerPort
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot


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
        """Train a model from snapshots and activate the resulting predictor."""

        predictor = self.trainer.train(spec, snapshots)
        self.model_store.save_candidate(predictor)
        self.model_store.swap_active(predictor)
