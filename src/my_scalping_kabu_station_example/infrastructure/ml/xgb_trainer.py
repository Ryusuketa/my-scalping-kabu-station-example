"""XGBoost trainer placeholder."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np
import xgboost as xgb

from my_scalping_kabu_station_example.application.ports.feature_engine import FeatureVector
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.infrastructure.ml.schema import feature_ordering
from my_scalping_kabu_station_example.infrastructure.ml.xgb_predictor import XgbPredictor


@dataclass
class XgbTrainer:
    params: dict = field(default_factory=lambda: {"n_estimators": 50, "max_depth": 3, "learning_rate": 0.1})
    default_score: float = 0.0

    def train(self, spec: FeatureSpec, dataset: Iterable[FeatureVector]) -> XgbPredictor:
        feature_names = feature_ordering(spec)
        rows = list(dataset)
        if not rows:
            raise ValueError("Dataset is empty")

        labels = [row.get("label") for row in rows]
        has_labels = all(label is not None for label in labels)
        if not has_labels:
            return XgbPredictor(feature_order=feature_names, model=None, default_score=self.default_score)

        data = np.array([[row.get(name, 0.0) for name in feature_names] for row in rows], dtype=float)
        target = np.array([float(label) for label in labels], dtype=float)

        model = xgb.XGBRegressor(**self.params)
        model.fit(data, target)
        return XgbPredictor(feature_order=feature_names, model=model)
