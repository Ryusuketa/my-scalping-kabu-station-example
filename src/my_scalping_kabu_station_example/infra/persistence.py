"""Persistence and buffering infrastructure implementations."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict

from my_scalping_kabu_station_example.domain.order_book import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.ports import HistoryStore, SnapshotBuffer


class CsvHistoryStore(HistoryStore):
    """Persist order book snapshots into a fixed-column CSV file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.fieldnames = ["ts", "symbol"] + [f"bid_p{i}" for i in range(1, 11)] + [f"bid_q{i}" for i in range(1, 11)]
        self.fieldnames += [f"ask_p{i}" for i in range(1, 11)] + [f"ask_q{i}" for i in range(1, 11)]

    def append(self, snapshot: OrderBookSnapshot) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.path.exists()
        row = self._snapshot_to_row(snapshot)

        with self.path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def _snapshot_to_row(self, snapshot: OrderBookSnapshot) -> Dict[str, object]:
        row: Dict[str, object] = {"ts": snapshot.ts.isoformat(), "symbol": snapshot.symbol}
        for i in range(10):
            bid_level = snapshot.bid_levels[i] if i < len(snapshot.bid_levels) else None
            ask_level = snapshot.ask_levels[i] if i < len(snapshot.ask_levels) else None
            row[f"bid_p{i+1}"] = str(bid_level.price) if bid_level else None
            row[f"bid_q{i+1}"] = bid_level.quantity if bid_level else None
            row[f"ask_p{i+1}"] = str(ask_level.price) if ask_level else None
            row[f"ask_q{i+1}"] = ask_level.quantity if ask_level else None
        return row


class InMemorySnapshotBuffer(SnapshotBuffer):
    """Simple in-memory buffer storing the most recent snapshot."""

    def __init__(self) -> None:
        self._previous: OrderBookSnapshot | None = None

    def previous(self) -> OrderBookSnapshot | None:
        return self._previous

    def update(self, snapshot: OrderBookSnapshot) -> OrderBookSnapshot | None:
        prev = self._previous
        self._previous = snapshot
        return prev
