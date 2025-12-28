"""Instrument sync workflow skeleton."""

from __future__ import annotations

from ...ports.broker import InstrumentPort
from ....domain.instruments.registry import InstrumentList


class InstrumentSync:
    def __init__(self, instrument_port: InstrumentPort) -> None:
        self.instrument_port = instrument_port

    def run(self) -> InstrumentList:
        raise NotImplementedError
