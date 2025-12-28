"""Model-related ports."""

from __future__ import annotations

from typing import Any, Iterable, Protocol

from ...domain.features.spec import FeatureSpec
from ...domain.market.orderbook_snapshot import OrderBookSnapshot
from ...domain.decision.signal import InferenceResult


class ModelPredictorPort(Protocol):
    def predict(self, features: dict[str, float]) -> InferenceResult:
        ...


class ModelTrainerPort(Protocol):
    def train(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]) -> Any:
        ...


class ModelStorePort(Protocol):
    def load_active(self) -> ModelPredictorPort:
        ...

    def save_candidate(self, predictor: ModelPredictorPort) -> None:
        ...

    def swap_active(self, predictor: ModelPredictorPort) -> None:
        ...
