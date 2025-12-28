"""Startup use case."""

from __future__ import annotations

from ..service.pipelines.instrument_sync import InstrumentSync


class OnStartupUseCase:
    def __init__(self, sync: InstrumentSync) -> None:
        self.sync = sync

    def handle(self) -> None:
        self.sync.run()
