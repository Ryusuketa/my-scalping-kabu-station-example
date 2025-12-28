from typing import Iterable, List

from my_scalping_kabu_station_example.application.service.dataset import DatasetBuilder
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
    def __init__(self) -> None:
        self.batch_calls: list[tuple[FeatureSpec, Iterable[OrderBookSnapshot]]] = []
        self.return_value = [{"x": 1.0}, {"x": 2.0}]

    def compute_batch(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]):
        self.batch_calls.append((spec, snapshots))
        yield from self.return_value


def test_dataset_builder_collects_features() -> None:
    spec = FeatureSpec(version="v1", eps=1e-9, params={}, features=[FeatureDef("x", Const(1.0))])
    history_store = DummyHistoryStore()
    feature_engine = DummyFeatureEngine()
    builder = DatasetBuilder(history_store=history_store, feature_engine=feature_engine)
    snapshots: list[OrderBookSnapshot] = []

    features = builder.build(spec, snapshots)

    assert features == feature_engine.return_value
    assert feature_engine.batch_calls[0][0] == spec
    assert feature_engine.batch_calls[0][1] is snapshots
