"""Simple in-memory market data source for demos/tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

from application.ports.market_data import (
    MarketDataSourcePort,
)
from domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)


@dataclass
class SimpleMarketDataSource(MarketDataSourcePort):
    snapshots: Iterable[OrderBookSnapshot]

    def __post_init__(self) -> None:
        self._iterator: Iterator[OrderBookSnapshot] = iter(self.snapshots)

    def subscribe(self) -> None:
        return None

    def close(self) -> None:
        return None

    def receive(self) -> OrderBookSnapshot:
        return next(self._iterator)
