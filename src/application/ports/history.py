"""History persistence port."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Protocol

from domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)


class HistoryStorePort(Protocol):
    def append(self, snapshot: OrderBookSnapshot) -> None: ...

    def read_range(
        self, start: datetime, end: datetime
    ) -> Iterable[OrderBookSnapshot]: ...
