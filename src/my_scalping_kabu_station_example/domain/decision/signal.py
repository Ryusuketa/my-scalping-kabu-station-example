"""Trading signal and intent definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from my_scalping_kabu_station_example.domain.market.types import Symbol

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class InferenceResult:
    """Output of model inference."""

    features: Dict[str, float]
    score: float
    raw: Optional[Any] = None


@dataclass(frozen=True)
class TradeIntent:
    """Domain representation of a trading intent."""

    intent_id: str
    side: OrderSide
    quantity: float
    symbol: Symbol
    price: float
    cash_margin: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class DecisionContext:
    """Context for decision making."""

    position_size: float
    risk_budget: float
    symbol: Symbol
    price: float
    pip_size: float
    has_open_order: bool = False
    open_order_side: OrderSide | None = None
    open_order_price: float | None = None
    open_order_qty: int | None = None
