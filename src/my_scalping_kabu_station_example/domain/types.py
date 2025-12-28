"""Domain primitives and shared types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Iterable, Protocol


PriceKey = Decimal


class Side(str, Enum):
    """Order book side."""

    BID = "BID"
    ASK = "ASK"


def to_price_key(value: int | float | str | Decimal) -> PriceKey:
    """Convert numeric input into a PriceKey.

    This helper lives in the domain layer so that infra can share a single conversion rule.
    Implementation is provided later to satisfy tests.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, str)):
        return Decimal(str(value))
    if isinstance(value, float):
        # Convert through string to avoid binary floating artifacts.
        return Decimal(str(value))
    raise TypeError(f"Unsupported type for PriceKey: {type(value)}")


@dataclass(frozen=True)
class Timestamped:
    """Base mixin for timestamped domain entities."""

    ts: datetime


class PriceLevelIterable(Protocol):
    """Protocol for level iterables used across domain methods."""

    def __iter__(self) -> Iterable:
        ...


PriceQtyMap = Dict[PriceKey, float]
