"""Domain schema for persisted order book snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from domain.order_book import Level
from domain.types import PriceKey


@dataclass(frozen=True)
class OrderBookSnapshotSchema:
    """Fixed-column schema capturing top-10 levels per side."""

    ts: str
    symbol: str
    bid_prices: List[Optional[PriceKey]] = field(default_factory=list)
    bid_quantities: List[Optional[float]] = field(default_factory=list)
    ask_prices: List[Optional[PriceKey]] = field(default_factory=list)
    ask_quantities: List[Optional[float]] = field(default_factory=list)

    @classmethod
    def from_levels(
        cls,
        ts_iso: str,
        symbol: str,
        bid_levels: List[Level],
        ask_levels: List[Level],
        depth: int = 10,
    ) -> "OrderBookSnapshotSchema":
        """Construct schema enforcing fixed depth with padding."""
        padded_bids = bid_levels[:depth] + [None] * max(0, depth - len(bid_levels))
        padded_asks = ask_levels[:depth] + [None] * max(0, depth - len(ask_levels))

        def level_price(level: Level | None) -> Optional[PriceKey]:
            return level.price if level is not None else None

        def level_qty(level: Level | None) -> Optional[float]:
            return level.quantity if level is not None else None

        return cls(
            ts=ts_iso,
            symbol=symbol,
            bid_prices=[level_price(level) for level in padded_bids],
            bid_quantities=[level_qty(level) for level in padded_bids],
            ask_prices=[level_price(level) for level in padded_asks],
            ask_quantities=[level_qty(level) for level in padded_asks],
        )
