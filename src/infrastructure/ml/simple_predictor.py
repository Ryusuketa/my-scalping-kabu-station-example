"""Minimal predictor for demo usage."""

from __future__ import annotations

from application.ports.feature_engine import (
    FeatureVector,
)
from domain.decision.signal import InferenceResult


class SimplePredictor:
    def predict(self, features: FeatureVector) -> InferenceResult:
        return InferenceResult(features=features, score=0.0)
