"""CSV-based history store."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
from datetime import date

from my_scalping_kabu_station_example.application.ports.history import HistoryStorePort
from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import Quantity, Symbol, price_key_from


@dataclass
class CsvHistoryStore(HistoryStorePort):
    """Persist order book snapshots into fixed-column CSV rows."""

    path: Path

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        if self.path.suffix and self.path.suffix != ".csv":
            raise ValueError("CsvHistoryStore path must be a directory or .csv file path")
        self.fieldnames = ["ts", "symbol"]
        self.fieldnames += [f"bid_p{i}" for i in range(1, 11)] + [f"bid_q{i}" for i in range(1, 11)]
        self.fieldnames += [f"ask_p{i}" for i in range(1, 11)] + [f"ask_q{i}" for i in range(1, 11)]

    def append(self, snapshot: OrderBookSnapshot) -> None:
        """Append a snapshot to an hourly CSV, writing header on first write."""

        target_path = self._hourly_path(snapshot.ts)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not target_path.exists()
        row = self._snapshot_to_row(snapshot)

        with target_path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def read_range(self, start: datetime, end: datetime) -> Iterable[OrderBookSnapshot]:
        """Load snapshots whose timestamps fall within [start, end]."""

        files = self._files_for_range(start, end)
        if not files:
            return []

        snapshots: List[OrderBookSnapshot] = []
        for file_path in files:
            with file_path.open("r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ts = Timestamp(datetime.fromisoformat(row["ts"]))
                    if ts < start or ts > end:
                        continue
                    snapshots.append(self._row_to_snapshot(row))
        return snapshots

    def _hourly_path(self, ts: datetime) -> Path:
        ts_utc = ts.astimezone(timezone.utc) if ts.tzinfo else ts
        suffix = ts_utc.strftime("%Y%m%d_%H")
        if self.path.suffix == ".csv":
            return self.path.with_name(f"{self.path.stem}_{suffix}{self.path.suffix}")
        return self.path / f"history_{suffix}.csv"

    def _files_for_range(self, start: datetime, end: datetime) -> Sequence[Path]:
        if start > end:
            return []
        start_utc = start.astimezone(timezone.utc) if start.tzinfo else start
        end_utc = end.astimezone(timezone.utc) if end.tzinfo else end
        start_hour = start_utc.replace(minute=0, second=0, microsecond=0)
        end_hour = end_utc.replace(minute=0, second=0, microsecond=0)
        current = start_hour
        files: List[Path] = []
        while current <= end_hour:
            files.append(self._hourly_path(current))
            current += timedelta(hours=1)
        return [path for path in files if path.exists()]

    def available_dates(self) -> List[date]:
        """Return available dates based on hourly CSV filenames."""

        base_dir = self.path.parent if self.path.suffix == ".csv" else self.path
        if not base_dir.exists():
            return []

        if self.path.suffix == ".csv":
            stem = re.escape(self.path.stem)
            suffix = re.escape(self.path.suffix)
            pattern = re.compile(rf"^{stem}_(\d{{8}})_(\d{{2}}){suffix}$")
        else:
            pattern = re.compile(r"^history_(\d{8})_(\d{2})\.csv$")
        dates: set[date] = set()
        for entry in base_dir.iterdir():
            if not entry.is_file():
                continue
            match = pattern.match(entry.name)
            if not match:
                continue
            day_str = match.group(1)
            try:
                dates.add(datetime.strptime(day_str, "%Y%m%d").date())
            except ValueError:
                continue
        return sorted(dates)

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
