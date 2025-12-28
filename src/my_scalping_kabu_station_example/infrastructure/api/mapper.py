"""API mappers."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from my_scalping_kabu_station_example.domain.decision.signal import (
    OrderSide,
    TradeIntent,
)
from my_scalping_kabu_station_example.infrastructure.api.dto import OrderRequestDto


def to_api(intent: TradeIntent) -> OrderRequestDto:
    """Convert a TradeIntent into an API order request DTO."""

    symbol_value = intent.symbol
    return OrderRequestDto(
        intent_id=intent.intent_id,
        side=intent.side,
        quantity=intent.quantity,
        symbol=symbol_value,
    )


def build_order_payload(
    intent: TradeIntent,
    base_payload: Mapping[str, Any] | None = None,
    side_override: OrderSide | None = None,
) -> Dict[str, Any]:
    """Build a request payload for /sendorder from a trade intent."""

    payload: Dict[str, Any] = dict(base_payload or {})
    payload.update(intent.metadata or {})
    if "symbol" in payload and "Symbol" not in payload:
        payload["Symbol"] = payload["symbol"]
    payload["Symbol"] = intent.symbol
    payload["Price"] = intent.price
    side_value = side_override or intent.side
    payload["Side"] = "2" if side_value is OrderSide.BUY else "1"
    payload["Qty"] = int(intent.quantity * 100)
    payload["CashMargin"] = int(intent.cash_margin)

    required = {
        "Symbol",
        "Exchange",
        "SecurityType",
        "Side",
        "CashMargin",
        "DelivType",
        "AccountType",
        "Qty",
        "Price",
        "ExpireDay",
        "FrontOrderType",
    }
    missing = sorted(key for key in required if key not in payload)
    if missing:
        raise ValueError(f"Order payload missing required fields: {', '.join(missing)}")
    return payload


def to_order_payload(intent: TradeIntent) -> Dict[str, Any]:
    return build_order_payload(intent)
