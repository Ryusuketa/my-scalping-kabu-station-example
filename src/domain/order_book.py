"""Order book domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Tuple

from domain.types import (
    PriceKey,
    PriceQtyMap,
    to_price_key,
)


@dataclass(frozen=True)
class Level:
    """Price level representation."""

    price: PriceKey
    quantity: float


@dataclass
class OrderBookSnapshot:
    """Fixed-depth order book snapshot for the top 10 levels on each side."""

    ts: datetime
    symbol: str
    bid_levels: List[Level]
    ask_levels: List[Level]
    best_bid_price: Optional[PriceKey] = None
    best_bid_qty: Optional[float] = None
    best_ask_price: Optional[PriceKey] = None
    best_ask_qty: Optional[float] = None
    mid: Optional[PriceKey] = None
    bid_map: PriceQtyMap = field(default_factory=dict)
    ask_map: PriceQtyMap = field(default_factory=dict)

    @classmethod
    def from_levels(
        cls,
        ts: datetime,
        symbol: str,
        bid_levels: Iterable[Level],
        ask_levels: Iterable[Level],
    ) -> "OrderBookSnapshot":
        """Build a snapshot from unordered raw levels.

        Sorting, trimming, and best/mid calculations are completed in a dedicated method
        that will be implemented after tests are written.
        """
        bid_sorted = sorted(bid_levels, key=lambda level: level.price, reverse=True)[:10]
        ask_sorted = sorted(ask_levels, key=lambda level: level.price)[:10]

        best_bid = bid_sorted[0] if bid_sorted else None
        best_ask = ask_sorted[0] if ask_sorted else None

        mid_price = None
        if best_bid and best_ask:
            mid_price = (best_bid.price + best_ask.price) / 2

        return cls(
            ts=ts,
            symbol=symbol,
            bid_levels=bid_sorted,
            ask_levels=ask_sorted,
            best_bid_price=best_bid.price if best_bid else None,
            best_bid_qty=best_bid.quantity if best_bid else None,
            best_ask_price=best_ask.price if best_ask else None,
            best_ask_qty=best_ask.quantity if best_ask else None,
            mid=mid_price,
            bid_map={level.price: level.quantity for level in bid_sorted},
            ask_map={level.price: level.quantity for level in ask_sorted},
        )


@dataclass(frozen=True)
class OrderBookUpdate:
    """Raw order book update DTO prior to normalization."""

    ts: datetime
    symbol: str
    bids: Sequence[Tuple[PriceKey | float | int | str, float]]
    asks: Sequence[Tuple[PriceKey | float | int | str, float]]

    def to_snapshot(self) -> OrderBookSnapshot:
        """Normalize the raw update into an OrderBookSnapshot."""
        bid_levels = [
            Level(price=to_price_key(price), quantity=qty) for price, qty in self.bids
        ]
        ask_levels = [
            Level(price=to_price_key(price), quantity=qty) for price, qty in self.asks
        ]
        return OrderBookSnapshot.from_levels(
            ts=self.ts,
            symbol=self.symbol,
            bid_levels=bid_levels,
            ask_levels=ask_levels,
        )
