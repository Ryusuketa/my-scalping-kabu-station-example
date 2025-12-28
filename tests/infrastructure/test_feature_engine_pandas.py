from datetime import datetime, timedelta, timezone

import pytest

from my_scalping_kabu_station_example.application.service.state.feature_state import (
    FeatureState,
)
from my_scalping_kabu_station_example.domain.features import names
from my_scalping_kabu_station_example.domain.features.expr import (
    Add,
    AddSum,
    BestAskPrice,
    BestAskQty,
    BestBidPrice,
    BestBidQty,
    Const,
    DepletionSum,
    DepthQtySum,
    Div,
    MicroPrice,
    Mid,
    Sub,
    TimeDecayEma,
)
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
    Side,
    Symbol,
    price_key_from,
)
from my_scalping_kabu_station_example.infrastructure.compute.feature_engine_pandas import (
    PandasOrderBookFeatureEngine,
)


def _make_snapshot(ts: datetime, bids, asks) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        ts=Timestamp(ts),
        symbol=Symbol("TEST"),
        bid_levels=[Level(price_key_from(p), Quantity(q)) for p, q in bids],
        ask_levels=[Level(price_key_from(p), Quantity(q)) for p, q in asks],
    )


def _build_spec() -> FeatureSpec:
    eps = 1e-9
    def_b = DepthQtySum(Side.BID, depth=1)
    def_a = DepthQtySum(Side.ASK, depth=1)
    di_num = Sub(DepletionSum(Side.ASK), DepletionSum(Side.BID))
    di_den = Add(Add(DepletionSum(Side.ASK), DepletionSum(Side.BID)), Const(eps))
    ai_num = Sub(AddSum(Side.BID), AddSum(Side.ASK))
    ai_den = Add(Add(AddSum(Side.BID), AddSum(Side.ASK)), Const(eps))

    return FeatureSpec.from_features(
        version="ob10_v1",
        eps=eps,
        params={},
        features=[
            FeatureDef(
                names.OBI_5,
                expr=Div(Sub(def_b, def_a), Add(Add(def_b, def_a), Const(eps))),
            ),
            FeatureDef(names.MICROPRICE, expr=MicroPrice(eps=eps)),
            FeatureDef(names.DEPLETION_IMBALANCE, expr=Div(di_num, di_den)),
            FeatureDef(names.ADD_IMBALANCE, expr=Div(ai_num, ai_den)),
            FeatureDef(
                names.DEPLETION_IMBALANCE_EMA,
                expr=TimeDecayEma(source=Div(di_num, di_den), tau_seconds=1.0),
            ),
        ],
    )


def test_compute_one_calculates_depth_micro_and_imbalances() -> None:
    engine = PandasOrderBookFeatureEngine()
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts1 = ts0 + timedelta(seconds=1)
    prev = _make_snapshot(
        ts0,
        bids=[("100.0", 2.0), ("99.8", 1.0)],
        asks=[("100.5", 1.0)],
    )
    now = _make_snapshot(
        ts1,
        bids=[("100.0", 1.5), ("99.7", 2.0)],
        asks=[("100.4", 1.2), ("100.9", 0.5)],
    )

    features, state = engine.compute_one(_build_spec(), prev, now, FeatureState())

    assert pytest.approx(features[names.OBI_5], rel=1e-4) == (1.5 - 1.2) / (
        1.5 + 1.2 + 1e-9
    )
    assert pytest.approx(features[names.MICROPRICE], rel=1e-4) == 100.2222
    assert pytest.approx(features[names.DEPLETION_IMBALANCE], rel=1e-4) == (
        1.0 - 1.5
    ) / (1.0 + 1.5 + 1e-9)
    assert pytest.approx(features[names.ADD_IMBALANCE], rel=1e-4) == (2.0 - 1.7) / (
        2.0 + 1.7 + 1e-9
    )
    assert (
        pytest.approx(features[names.DEPLETION_IMBALANCE_EMA], rel=1e-4)
        == features[names.DEPLETION_IMBALANCE]
    )
    assert state.last_ts == now.ts
    assert names.DEPLETION_IMBALANCE_EMA in state.ema_values


def test_compute_batch_iterates_snapshots() -> None:
    engine = PandasOrderBookFeatureEngine()
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts1 = ts0 + timedelta(seconds=1)
    snapshots = [
        _make_snapshot(ts0, bids=[("100.0", 1.0)], asks=[("100.5", 1.0)]),
        _make_snapshot(ts1, bids=[("100.0", 1.5)], asks=[("100.4", 1.2)]),
    ]

    features = list(engine.compute_batch(_build_spec(), snapshots))

    assert len(features) == 2
    assert features[0][names.DEPLETION_IMBALANCE] == 0.0  # prev is None


def test_compute_one_exposes_best_levels_and_mid() -> None:
    engine = PandasOrderBookFeatureEngine()
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    snapshot = _make_snapshot(
        ts,
        bids=[("100.0", 2.0), ("99.8", 1.0)],
        asks=[("100.5", 1.0), ("101.0", 1.5)],
    )
    spec = FeatureSpec.from_features(
        version="ob10_v1",
        eps=1e-9,
        params={},
        features=[
            FeatureDef("best_bid_price", expr=BestBidPrice()),
            FeatureDef("best_ask_price", expr=BestAskPrice()),
            FeatureDef("best_bid_qty", expr=BestBidQty()),
            FeatureDef("best_ask_qty", expr=BestAskQty()),
            FeatureDef("mid_price", expr=Mid()),
            FeatureDef(names.MICROPRICE_SHIFT, expr=Sub(MicroPrice(eps=1e-9), Mid())),
        ],
    )

    features, state = engine.compute_one(spec, None, snapshot, FeatureState())

    assert features["best_bid_price"] == pytest.approx(100.0)
    assert features["best_ask_price"] == pytest.approx(100.5)
    assert features["best_bid_qty"] == pytest.approx(2.0)
    assert features["best_ask_qty"] == pytest.approx(1.0)
    assert features["mid_price"] == pytest.approx(100.25)
    expected_micro = (100.5 * 2.0 + 100.0 * 1.0) / (2.0 + 1.0 + 1e-9)
    assert features[names.MICROPRICE_SHIFT] == pytest.approx(expected_micro - 100.25)
    assert state.last_ts == snapshot.ts
