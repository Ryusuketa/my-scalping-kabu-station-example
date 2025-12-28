"""XGBoost predictor placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np

from my_scalping_kabu_station_example.domain.decision.signal import InferenceResult


@dataclass
class XgbPredictor:
    feature_order: Iterable[str]
    model: Optional[object] = None
    default_score: float = 0.0

    def predict(self, features: dict[str, float]) -> InferenceResult:
        if self.model is None:
            return InferenceResult(features=features, score=self.default_score)

        order = list(self.feature_order)
        data = np.array([[features.get(name, 0.0) for name in order]], dtype=float)
        score = float(self.model.predict(data)[0])
        return InferenceResult(features=features, score=score)
