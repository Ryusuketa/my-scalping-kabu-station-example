"""Primitive market types."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from enum import Enum
from typing import Dict, NewType

# Set a sane precision for price calculations. Adjust as needed by upstream config.
getcontext().prec = 16

PriceKey = NewType("PriceKey", Decimal)
Quantity = NewType("Quantity", float)
Symbol = NewType("Symbol", str)
PriceQtyMap = Dict[PriceKey, Quantity]


class Side(str, Enum):
    """Order book side."""

    BID = "BID"
    ASK = "ASK"

    def opposite(self) -> "Side":
        return Side.ASK if self is Side.BID else Side.BID


@dataclass(frozen=True)
class Epsilon:
    """Small constant to prevent division by zero."""

    value: float = 1e-9


def price_key_from(value: float | int | str | Decimal) -> PriceKey:
    """Create a normalized price key.

    Domain mandates avoiding floating point drift by storing prices as Decimal.
    """

    if isinstance(value, Decimal):
        return PriceKey(value)
    if isinstance(value, (int, str)):
        return PriceKey(Decimal(str(value)))
    if isinstance(value, float):
        # Convert via string to avoid binary floating point artifacts.
        return PriceKey(Decimal(str(value)))
    raise TypeError(f"Unsupported type for PriceKey: {type(value)}")
