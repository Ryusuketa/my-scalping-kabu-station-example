"""In-memory market buffer port."""

from __future__ import annotations

from typing import Iterable, Protocol

from ...domain.market.orderbook_snapshot import OrderBookSnapshot


class MarketBufferPort(Protocol):
    def update(self, snapshot: OrderBookSnapshot) -> None:
        ...

    def get_prev(self) -> OrderBookSnapshot | None:
        ...

    def get_window(self, size: int) -> Iterable[OrderBookSnapshot]:
        ...
