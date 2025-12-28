"""Order book level representation."""

from __future__ import annotations

from dataclasses import dataclass

from my_scalping_kabu_station_example.domain.market.types import PriceKey, Quantity


@dataclass(frozen=True)
class Level:
    """One price level of the order book."""

    price: PriceKey
    qty: Quantity

    def __post_init__(self) -> None:
        if self.qty < 0:
            raise ValueError("Quantity must be non-negative")
