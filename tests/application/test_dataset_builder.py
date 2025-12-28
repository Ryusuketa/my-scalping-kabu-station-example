from datetime import datetime, timezone

import pytest

from my_scalping_kabu_station_example.application.service.dataset import DatasetBuilder
from my_scalping_kabu_station_example.domain.features.expr import MicroPrice
from my_scalping_kabu_station_example.domain.features.spec import (
    FeatureDef,
    FeatureSpec,
)
from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import (
    Quantity,
    Symbol,
    price_key_from,
)
from my_scalping_kabu_station_example.infrastructure.compute.feature_engine_pandas import (
    PandasOrderBookFeatureEngine,
)
from my_scalping_kabu_station_example.infrastructure.persistence.csv_history_store import (
    CsvHistoryStore,
)


def _make_snapshot(ts: datetime, bid: str, ask: str) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        ts=Timestamp(ts),
        symbol=Symbol("TEST"),
        bid_levels=[Level(price_key_from(bid), Quantity(1.0))],
        ask_levels=[Level(price_key_from(ask), Quantity(2.0))],
    )


def test_dataset_builder_collects_features(tmp_path) -> None:
    spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef("microprice", MicroPrice(eps=1e-9))],
    )
    history_store = CsvHistoryStore(path=tmp_path / "history.csv")
    feature_engine = PandasOrderBookFeatureEngine()
    builder = DatasetBuilder(history_store=history_store, feature_engine=feature_engine)
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts1 = datetime(2024, 1, 1, 0, 0, 1, tzinfo=timezone.utc)
    snapshots = [
        _make_snapshot(ts0, "100.0", "100.5"),
        _make_snapshot(ts1, "100.1", "100.6"),
    ]

    features = builder.build(spec, snapshots)

    assert len(features) == 2
    expected = (100.5 * 1.0 + 100.0 * 2.0) / (1.0 + 2.0 + 1e-9)
    assert features[0]["microprice"] == pytest.approx(expected)
