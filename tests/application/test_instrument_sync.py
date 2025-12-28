import pytest

from my_scalping_kabu_station_example.application.service.pipelines.instrument_sync import (
    InstrumentSync,
)
from my_scalping_kabu_station_example.domain.instruments.instrument import Instrument
from my_scalping_kabu_station_example.domain.instruments.registry import InstrumentList
from my_scalping_kabu_station_example.domain.market.types import Symbol


class DummyInstrumentPort:
    def __init__(self, instruments: InstrumentList) -> None:
        self.instruments = instruments
        self.calls = 0

    def list(self) -> InstrumentList:
        self.calls += 1
        return self.instruments

    def get(self, symbol: Symbol):  # pragma: no cover - unused
        return self.instruments.find(symbol)


def test_instrument_sync_returns_registry() -> None:
    registry = InstrumentList(instruments=[Instrument(symbol=Symbol("TEST"))])
    port = DummyInstrumentPort(registry)
    sync = InstrumentSync(instrument_port=port)

    result = sync.run()

    assert result is registry
    assert port.calls == 1


def test_instrument_sync_requires_instruments() -> None:
    empty_registry = InstrumentList(instruments=[])
    port = DummyInstrumentPort(empty_registry)
    sync = InstrumentSync(instrument_port=port)

    with pytest.raises(ValueError):
        sync.run()
