"""In-memory model store for demo usage."""

from __future__ import annotations

from application.ports.model import ModelStorePort
from infrastructure.ml.simple_predictor import (
    SimplePredictor,
)


class InMemoryModelStore(ModelStorePort):
    def __init__(self) -> None:
        self._predictor = SimplePredictor()

    def load_active(self) -> SimplePredictor:
        return self._predictor

    def save_candidate(self, _predictor: SimplePredictor) -> None:
        return None

    def swap_active(self, predictor: SimplePredictor) -> None:
        self._predictor = predictor
