"""Startup use case."""

from __future__ import annotations

from my_scalping_kabu_station_example.application.service.pipelines.instrument_sync import InstrumentSync


class OnStartupUseCase:
    def __init__(self, sync: InstrumentSync) -> None:
        self.sync = sync

    def handle(self) -> None:
        self.sync.run()
