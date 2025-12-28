from typing import Iterable, List

from my_scalping_kabu_station_example.application.service.pipelines.training_pipeline import TrainingPipeline
from my_scalping_kabu_station_example.domain.features.expr import Const
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot


class DummyHistoryStore:
    def __init__(self) -> None:
        self.appended: List[OrderBookSnapshot] = []

    def append(self, snapshot: OrderBookSnapshot) -> None:  # pragma: no cover - unused
        self.appended.append(snapshot)

    def read_range(self, *_args, **_kwargs) -> Iterable[OrderBookSnapshot]:  # pragma: no cover - unused
        return []


class DummyFeatureEngine:
    def compute_batch(self, *_args, **_kwargs):  # pragma: no cover - unused
        return []


class DummyPredictor:
    def __init__(self) -> None:
        self.trained_on: list[OrderBookSnapshot] = []

    def predict(self, *_args, **_kwargs):  # pragma: no cover - unused
        return {}


class DummyTrainer:
    def __init__(self) -> None:
        self.calls: list[tuple[FeatureSpec, Iterable[OrderBookSnapshot]]] = []
        self.predictor = DummyPredictor()

    def train(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]):
        self.calls.append((spec, snapshots))
        return self.predictor


class DummyModelStore:
    def __init__(self) -> None:
        self.saved: list[DummyPredictor] = []
        self.swapped: list[DummyPredictor] = []

    def load_active(self):  # pragma: no cover - unused
        raise NotImplementedError

    def save_candidate(self, predictor: DummyPredictor) -> None:
        self.saved.append(predictor)

    def swap_active(self, predictor: DummyPredictor) -> None:
        self.swapped.append(predictor)


def test_training_pipeline_trains_and_activates_model() -> None:
    spec = FeatureSpec(version="v1", eps=1e-9, params={}, features=[FeatureDef("x", Const(1.0))])
    history_store = DummyHistoryStore()
    feature_engine = DummyFeatureEngine()
    trainer = DummyTrainer()
    model_store = DummyModelStore()
    pipeline = TrainingPipeline(
        history_store=history_store,
        feature_engine=feature_engine,
        trainer=trainer,
        model_store=model_store,
    )
    snapshots: list[OrderBookSnapshot] = []

    pipeline.run(spec, snapshots)

    assert trainer.calls[0] == (spec, snapshots)
    assert model_store.saved == [trainer.predictor]
    assert model_store.swapped == [trainer.predictor]
