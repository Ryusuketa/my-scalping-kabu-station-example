"""Model-related ports."""

from __future__ import annotations

from typing import Any, Iterable, Protocol

from domain.features.spec import FeatureSpec
from domain.decision.signal import InferenceResult
from application.ports.feature_engine import (
    FeatureVector,
)


class ModelPredictorPort(Protocol):
    def predict(self, features: dict[str, float]) -> InferenceResult: ...


class ModelTrainerPort(Protocol):
    def train(self, spec: FeatureSpec, dataset: Iterable[FeatureVector]) -> Any: ...


class ModelStorePort(Protocol):
    def load_active(self) -> ModelPredictorPort: ...

    def save_candidate(self, predictor: ModelPredictorPort) -> None: ...

    def swap_active(self, predictor: ModelPredictorPort) -> None: ...
