"""Order book invariant helpers."""

from __future__ import annotations

from typing import Iterable

from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.types import Side


def is_sorted_bids(levels: Iterable[Level]) -> bool:
    """Check bids are sorted descending by price."""

    prices = [level.price for level in levels]
    return all(prices[i] >= prices[i + 1] for i in range(len(prices) - 1))


def is_sorted_asks(levels: Iterable[Level]) -> bool:
    """Check asks are sorted ascending by price."""

    prices = [level.price for level in levels]
    return all(prices[i] <= prices[i + 1] for i in range(len(prices) - 1))


def validate_side_order(levels: Iterable[Level], side: Side) -> None:
    """Raise if levels are not ordered correctly for the given side."""

    if side is Side.BID and not is_sorted_bids(levels):
        raise ValueError("Bid levels must be sorted descending by price")
    if side is Side.ASK and not is_sorted_asks(levels):
        raise ValueError("Ask levels must be sorted ascending by price")


def spread_is_valid(best_bid: float, best_ask: float) -> bool:
    """Validate spread (bid < ask)."""

    return best_bid < best_ask
