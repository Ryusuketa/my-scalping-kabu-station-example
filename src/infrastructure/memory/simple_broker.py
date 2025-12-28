"""Simple broker/position adapters for demo usage."""

from __future__ import annotations

from application.ports.broker import (
    OrderPort,
    PositionPort,
)
from domain.decision.signal import TradeIntent


class LoggingOrderPort(OrderPort):
    def place_order(self, intent: TradeIntent) -> str:
        print(f"order: {intent.intent_id} {intent.side.value} qty={intent.quantity}")
        return intent.intent_id


class FixedPositionPort(PositionPort):
    def __init__(self, position: float = 0.0) -> None:
        self._position = position

    def current_position(self) -> float:
        return self._position
