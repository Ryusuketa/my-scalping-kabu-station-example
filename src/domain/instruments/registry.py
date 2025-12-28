"""Instrument registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from domain.market.types import Symbol
from domain.instruments.instrument import Instrument


@dataclass
class InstrumentList:
    instruments: List[Instrument] = field(default_factory=list)

    def __post_init__(self) -> None:
        symbols = [inst.symbol for inst in self.instruments]
        if len(symbols) != len(set(symbols)):
            raise ValueError("Instrument symbols must be unique")

    def add(self, instrument: Instrument) -> None:
        if self.find(instrument.symbol):
            raise ValueError(f"Instrument {instrument.symbol} already registered")
        self.instruments.append(instrument)

    def find(self, symbol: Symbol) -> Optional[Instrument]:
        return next((inst for inst in self.instruments if inst.symbol == symbol), None)

    @classmethod
    def from_iterable(cls, instruments: Iterable[Instrument]) -> "InstrumentList":
        return cls(list(instruments))

    def as_dict(self) -> Dict[Symbol, Instrument]:
        return {inst.symbol: inst for inst in self.instruments}
