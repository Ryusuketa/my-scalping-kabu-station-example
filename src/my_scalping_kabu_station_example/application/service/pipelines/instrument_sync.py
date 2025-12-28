"""Instrument sync workflow skeleton."""

from __future__ import annotations

from my_scalping_kabu_station_example.application.ports.broker import InstrumentPort
from my_scalping_kabu_station_example.domain.instruments.registry import InstrumentList


class InstrumentSync:
    def __init__(self, instrument_port: InstrumentPort) -> None:
        self.instrument_port = instrument_port

    def run(self) -> InstrumentList:
        """Fetch instruments from broker and return a validated registry."""

        instruments = self.instrument_port.list()
        if not instruments.instruments:
            raise ValueError("No instruments available from broker")
        return instruments
