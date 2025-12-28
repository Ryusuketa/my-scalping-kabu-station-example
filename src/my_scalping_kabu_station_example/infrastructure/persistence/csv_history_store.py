"""CSV-based history store."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from ...application.ports.history import HistoryStorePort
from ...domain.market.level import Level
from ...domain.market.orderbook_snapshot import OrderBookSnapshot
from ...domain.market.time import Timestamp
from ...domain.market.types import Quantity, Symbol, price_key_from


@dataclass
class CsvHistoryStore(HistoryStorePort):
    """Persist order book snapshots into fixed-column CSV rows."""

    path: Path

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        self.fieldnames = ["ts", "symbol"]
        self.fieldnames += [f"bid_p{i}" for i in range(1, 11)] + [f"bid_q{i}" for i in range(1, 11)]
        self.fieldnames += [f"ask_p{i}" for i in range(1, 11)] + [f"ask_q{i}" for i in range(1, 11)]

    def append(self, snapshot: OrderBookSnapshot) -> None:
        """Append a snapshot to CSV, writing header on first write."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.path.exists()
        row = self._snapshot_to_row(snapshot)

        with self.path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def read_range(self, start: datetime, end: datetime) -> Iterable[OrderBookSnapshot]:
        """Load snapshots whose timestamps fall within [start, end]."""

        if not self.path.exists():
            return []

        snapshots: List[OrderBookSnapshot] = []
        with self.path.open("r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = Timestamp(datetime.fromisoformat(row["ts"]))
                if ts < start or ts > end:
                    continue
                snapshots.append(self._row_to_snapshot(row))
        return snapshots

    def _snapshot_to_row(self, snapshot: OrderBookSnapshot) -> Dict[str, object]:
        row: Dict[str, object] = {"ts": snapshot.ts.isoformat(), "symbol": snapshot.symbol}
        for i in range(10):
            bid_level = snapshot.bid_levels[i] if i < len(snapshot.bid_levels) else None
            ask_level = snapshot.ask_levels[i] if i < len(snapshot.ask_levels) else None
            row[f"bid_p{i+1}"] = str(bid_level.price) if bid_level else None
            row[f"bid_q{i+1}"] = float(bid_level.qty) if bid_level else None
            row[f"ask_p{i+1}"] = str(ask_level.price) if ask_level else None
            row[f"ask_q{i+1}"] = float(ask_level.qty) if ask_level else None
        return row

    def _row_to_snapshot(self, row: Dict[str, str]) -> OrderBookSnapshot:
        bids: List[Level] = []
        asks: List[Level] = []
        symbol = Symbol(row["symbol"])
        ts = Timestamp(datetime.fromisoformat(row["ts"]))

        for i in range(1, 11):
            bid_price = row.get(f"bid_p{i}")
            bid_qty = row.get(f"bid_q{i}")
            if bid_price and bid_qty not in (None, ""):
                bids.append(Level(price=price_key_from(bid_price), qty=Quantity(float(bid_qty))))

            ask_price = row.get(f"ask_p{i}")
            ask_qty = row.get(f"ask_q{i}")
            if ask_price and ask_qty not in (None, ""):
                asks.append(Level(price=price_key_from(ask_price), qty=Quantity(float(ask_qty))))

        return OrderBookSnapshot(ts=ts, symbol=symbol, bid_levels=bids, ask_levels=asks)
