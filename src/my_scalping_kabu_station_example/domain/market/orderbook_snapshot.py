"""Snapshot representation for a 10-level order book."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from my_scalping_kabu_station_example.domain.market.invariants import (
    is_sorted_asks,
    is_sorted_bids,
)
from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import (
    PriceKey,
    PriceQtyMap,
    Quantity,
    Side,
    Symbol,
)


@dataclass(slots=True)
class OrderBookSnapshot:
    """Immutable snapshot of the visible order book."""

    ts: Timestamp
    symbol: Symbol
    bid_levels: List[Level]
    ask_levels: List[Level]
    best_bid_price: Optional[PriceKey] = None
    best_bid_qty: Optional[Quantity] = None
    best_ask_price: Optional[PriceKey] = None
    best_ask_qty: Optional[Quantity] = None
    mid: Optional[PriceKey] = None
    bid_map: PriceQtyMap = field(init=False)
    ask_map: PriceQtyMap = field(init=False)

    def __post_init__(self) -> None:
        self._validate_levels()
        self.bid_map = {level.price: level.qty for level in self.bid_levels}
        self.ask_map = {level.price: level.qty for level in self.ask_levels}
        self._populate_best_levels()
        self._populate_mid()

    def _validate_levels(self) -> None:
        if len(self.bid_levels) > 10 or len(self.ask_levels) > 10:
            raise ValueError("Order book snapshot supports up to 10 levels per side")
        if not is_sorted_bids(self.bid_levels):
            raise ValueError("Bid levels must be sorted descending by price")
        if not is_sorted_asks(self.ask_levels):
            raise ValueError("Ask levels must be sorted ascending by price")

    def _populate_best_levels(self) -> None:
        if self.bid_levels:
            best_bid = self.bid_levels[0]
            self.best_bid_price = self.best_bid_price or best_bid.price
            self.best_bid_qty = self.best_bid_qty or best_bid.qty
        if self.ask_levels:
            best_ask = self.ask_levels[0]
            self.best_ask_price = self.best_ask_price or best_ask.price
            self.best_ask_qty = self.best_ask_qty or best_ask.qty

    def _populate_mid(self) -> None:
        if self.best_bid_price is None or self.best_ask_price is None:
            self.mid = None
            return
        if self.best_bid_price >= self.best_ask_price:
            # Crossed book: leave mid undefined to signal invalid snapshot.
            self.mid = None
            return
        mid_value = (
            Decimal(self.best_bid_price) + Decimal(self.best_ask_price)
        ) / Decimal(2)
        self.mid = PriceKey(mid_value)

    def depth_levels(self, side: Side) -> List[Level]:
        return self.bid_levels if side is Side.BID else self.ask_levels
