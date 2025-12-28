from datetime import datetime, timezone

from my_scalping_kabu_station_example.application.usecase.on_market_data import OnMarketDataUseCase
from my_scalping_kabu_station_example.application.usecase.on_startup import OnStartupUseCase
from my_scalping_kabu_station_example.application.usecase.on_timer_training import OnTimerTrainingUseCase
from my_scalping_kabu_station_example.domain.features.expr import Const
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import Quantity, Symbol, price_key_from


class DummyInferencePipeline:
    def __init__(self) -> None:
        self.calls = 0

    def run_once(self, _state) -> None:
        self.calls += 1


class DummyTrainingPipeline:
    def __init__(self) -> None:
        self.calls: list[tuple[FeatureSpec, list[OrderBookSnapshot]]] = []

    def run(self, spec: FeatureSpec, snapshots: list[OrderBookSnapshot]) -> None:
        self.calls.append((spec, snapshots))


class DummyInstrumentSync:
    def __init__(self) -> None:
        self.calls = 0

    def run(self) -> None:
        self.calls += 1


def _snapshot(ts: datetime) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        ts=Timestamp(ts),
        symbol=Symbol("TEST"),
        bid_levels=[Level(price_key_from("100.0"), Quantity(1.0))],
        ask_levels=[Level(price_key_from("100.5"), Quantity(1.0))],
    )


def test_on_market_data_usecase_delegates_to_pipeline() -> None:
    pipeline = DummyInferencePipeline()
    usecase = OnMarketDataUseCase(pipeline=pipeline)

    usecase.handle(state=None)

    assert pipeline.calls == 1


def test_on_timer_training_usecase_passes_spec_and_snapshots() -> None:
    spec = FeatureSpec(version="v1", eps=1e-9, params={}, features=[FeatureDef("x", Const(1.0))])
    pipeline = DummyTrainingPipeline()
    usecase = OnTimerTrainingUseCase(pipeline=pipeline, spec=spec)
    snapshots = [_snapshot(datetime(2024, 1, 1, tzinfo=timezone.utc))]

    usecase.handle(snapshots)

    assert pipeline.calls == [(spec, snapshots)]


def test_on_startup_usecase_runs_sync() -> None:
    sync = DummyInstrumentSync()
    usecase = OnStartupUseCase(sync=sync)

    usecase.handle()

    assert sync.calls == 1
