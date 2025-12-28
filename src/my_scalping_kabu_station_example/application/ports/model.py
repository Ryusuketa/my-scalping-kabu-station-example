"""Model-related ports."""

from __future__ import annotations

from typing import Any, Iterable, Protocol

from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.decision.signal import InferenceResult
from my_scalping_kabu_station_example.application.ports.feature_engine import FeatureVector


class ModelPredictorPort(Protocol):
    def predict(self, features: dict[str, float]) -> InferenceResult:
        ...


class ModelTrainerPort(Protocol):
    def train(self, spec: FeatureSpec, dataset: Iterable[FeatureVector]) -> Any:
        ...


class ModelStorePort(Protocol):
    def load_active(self) -> ModelPredictorPort:
        ...

    def save_candidate(self, predictor: ModelPredictorPort) -> None:
        ...

    def swap_active(self, predictor: ModelPredictorPort) -> None:
        ...
