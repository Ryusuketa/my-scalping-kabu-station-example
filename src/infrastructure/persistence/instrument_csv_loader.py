"""Instrument loader from CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict

from domain.instruments.instrument import Instrument
from domain.instruments.registry import InstrumentList
from domain.market.types import Symbol


def load_instruments(path: str) -> InstrumentList:
    """Load instruments from a CSV file (expects a 'symbol' column)."""

    csv_path = Path(path)
    instruments: list[Instrument] = []

    with csv_path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            symbol = row.get("symbol")
            if not symbol:
                continue
            metadata: Dict[str, str] = {
                key: value
                for key, value in row.items()
                if key != "symbol" and value not in (None, "")
            }
            instruments.append(
                Instrument(symbol=Symbol(symbol), metadata=metadata or None)
            )

    return InstrumentList(instruments=instruments)
