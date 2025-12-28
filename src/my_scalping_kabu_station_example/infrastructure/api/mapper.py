"""API mappers."""

from __future__ import annotations

from my_scalping_kabu_station_example.domain.decision.signal import TradeIntent
from my_scalping_kabu_station_example.domain.market.types import Symbol
from my_scalping_kabu_station_example.infrastructure.api.dto import OrderRequestDto


def to_api(intent: TradeIntent) -> OrderRequestDto:
    """Convert a TradeIntent into an API order request DTO."""

    symbol_value = None
    if intent.metadata and "symbol" in intent.metadata:
        symbol_value = Symbol(str(intent.metadata["symbol"]))
    return OrderRequestDto(
        intent_id=intent.intent_id,
        side=intent.side,
        quantity=intent.quantity,
        symbol=symbol_value,
    )
