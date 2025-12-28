"""Realtime order record."""

from __future__ import annotations

from dataclasses import dataclass

from domain.decision.signal import OrderSide
from domain.market.types import Symbol


@dataclass
class RealTimeOrder:
    symbol: Symbol
    qty: int
    side: OrderSide
    cash_margin: int
    order_id: str
    price: float
    is_filled: bool = False
