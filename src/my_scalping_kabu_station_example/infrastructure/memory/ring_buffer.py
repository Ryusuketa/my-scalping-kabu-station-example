"""In-memory buffers for market snapshots."""

from __future__ import annotations

from collections import deque
from typing import Iterable, Optional

from ...application.ports.buffer import MarketBufferPort
from ...domain.market.orderbook_snapshot import OrderBookSnapshot


class RingBuffer:
    def __init__(self, size: int) -> None:
        self.size = size
        self.items: list = []

    def append(self, item) -> None:
        if len(self.items) >= self.size:
            self.items.pop(0)
        self.items.append(item)

    def get(self, n: int):
        return self.items[-n:]


class InMemoryMarketBuffer(MarketBufferPort):
    """Market buffer keeping track of the previous snapshot and recent window."""

    def __init__(self, window_size: int = 100) -> None:
        self._prev: Optional[OrderBookSnapshot] = None
        self._window: deque[OrderBookSnapshot] = deque(maxlen=window_size)

    def update(self, snapshot: OrderBookSnapshot) -> None:
        self._prev = snapshot
        self._window.append(snapshot)

    def get_prev(self) -> OrderBookSnapshot | None:
        return self._prev

    def get_window(self, size: int) -> Iterable[OrderBookSnapshot]:
        if size <= 0:
            return []
        return list(self._window)[-size:]
