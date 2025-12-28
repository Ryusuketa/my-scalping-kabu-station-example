"""Training pipeline skeleton."""

from __future__ import annotations

from typing import Iterable

from my_scalping_kabu_station_example.application.ports.feature_engine import FeatureEnginePort
from my_scalping_kabu_station_example.application.ports.history import HistoryStorePort
from my_scalping_kabu_station_example.application.ports.model import ModelStorePort, ModelTrainerPort
from my_scalping_kabu_station_example.application.service.dataset import DatasetBuilder
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot


class TrainingPipeline:
    def __init__(
        self,
        history_store: HistoryStorePort,
        feature_engine: FeatureEnginePort,
        trainer: ModelTrainerPort,
        model_store: ModelStorePort,
        label_horizon_seconds: float = 10.0,
    ) -> None:
        self.history_store = history_store
        self.feature_engine = feature_engine
        self.trainer = trainer
        self.model_store = model_store
        self.label_horizon_seconds = label_horizon_seconds

    def run(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]) -> None:
        """Train a model from snapshots and activate the resulting predictor."""

        builder = DatasetBuilder(history_store=self.history_store, feature_engine=self.feature_engine)
        dataset = builder.build_with_labels(
            spec=spec,
            snapshots=snapshots,
            horizon_seconds=self.label_horizon_seconds,
        )
        predictor = self.trainer.train(spec, dataset)
        self.model_store.save_candidate(predictor)
        self.model_store.swap_active(predictor)
