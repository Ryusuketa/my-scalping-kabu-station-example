import math

from my_scalping_kabu_station_example.domain.features.expr import Const
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.infrastructure.ml.xgb_trainer import XgbTrainer


def test_xgb_trainer_trains_model_when_labels_present() -> None:
    spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef("a", Const(1.0)), FeatureDef("b", Const(2.0))],
    )
    dataset = [
        {"a": 0.1, "b": 0.2, "label": 0},
        {"a": 0.2, "b": 0.4, "label": 1},
        {"a": 0.3, "b": 0.1, "label": 1},
    ]

    predictor = XgbTrainer(params={"n_estimators": 5, "max_depth": 2}).train(spec, dataset)

    assert predictor.model is not None
    result = predictor.predict({"a": 0.15, "b": 0.25})
    assert isinstance(result.score, float)
    assert math.isfinite(result.score)
    assert 0.0 <= result.score <= 1.0


def test_xgb_trainer_returns_default_predictor_without_labels() -> None:
    spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef("a", Const(1.0))],
    )
    dataset = [
        {"a": 0.1},
        {"a": 0.2},
    ]

    predictor = XgbTrainer(default_score=0.25).train(spec, dataset)

    assert predictor.model is None
    result = predictor.predict({"a": 0.3})
    assert result.score == 0.25
