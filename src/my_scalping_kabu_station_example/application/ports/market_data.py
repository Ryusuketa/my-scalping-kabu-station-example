"""Port for subscribing to market data."""

from __future__ import annotations

from typing import Protocol

from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot


class MarketDataSourcePort(Protocol):
    def subscribe(self) -> None:
        ...

    def close(self) -> None:
        ...

    def receive(self) -> OrderBookSnapshot:
        ...
