from my_scalping_kabu_station_example.application.usecase.on_market_data import (
    OnMarketDataUseCase,
)
from my_scalping_kabu_station_example.application.usecase.on_startup import (
    OnStartupUseCase,
)


class DummyInferencePipeline:
    def __init__(self) -> None:
        self.calls = 0

    def run_once(self, _state) -> None:
        self.calls += 1


class DummyInstrumentSync:
    def __init__(self) -> None:
        self.calls = 0

    def run(self) -> None:
        self.calls += 1


def test_on_market_data_usecase_delegates_to_pipeline() -> None:
    pipeline = DummyInferencePipeline()
    usecase = OnMarketDataUseCase(pipeline=pipeline)

    usecase.handle(state=None)

    assert pipeline.calls == 1


def test_on_startup_usecase_runs_sync() -> None:
    sync = DummyInstrumentSync()
    usecase = OnStartupUseCase(sync=sync)

    usecase.handle()

    assert sync.calls == 1
