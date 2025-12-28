"""API DTO definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from domain.decision.signal import OrderSide
from domain.market.types import Symbol


@dataclass(frozen=True)
class OrderRequestDto:
    intent_id: str
    side: OrderSide
    quantity: float
    symbol: Optional[Symbol] = None
