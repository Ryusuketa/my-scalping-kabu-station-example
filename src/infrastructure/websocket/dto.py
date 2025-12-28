"""WebSocket DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence, Tuple


@dataclass(frozen=True)
class OrderBookDto:
    ts: datetime
    symbol: str
    bids: Sequence[Tuple[str | float, float]]
    asks: Sequence[Tuple[str | float, float]]
