import pytest

from my_scalping_kabu_station_example.domain.instruments.instrument import Instrument
from my_scalping_kabu_station_example.domain.instruments.registry import InstrumentList
from my_scalping_kabu_station_example.domain.market.types import Symbol


def test_instrument_list_prevents_duplicates() -> None:
    instruments = [Instrument(symbol=Symbol("A")), Instrument(symbol=Symbol("B"))]
    registry = InstrumentList(instruments=instruments)

    registry.add(Instrument(symbol=Symbol("C")))
    assert registry.find(Symbol("C"))

    with pytest.raises(ValueError):
        registry.add(Instrument(symbol=Symbol("A")))
