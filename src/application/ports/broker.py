"""Broker and position ports."""

from __future__ import annotations

from typing import Iterable, Protocol

from domain.decision.signal import TradeIntent
from domain.instruments.instrument import Instrument
from domain.instruments.registry import InstrumentList
from domain.market.types import Symbol
from domain.order.realtime_order import RealTimeOrder


class OrderPort(Protocol):
    def place_order(self, intent: TradeIntent) -> str: ...


class PositionPort(Protocol):
    def current_position(self) -> float: ...


class OrderStatePort(Protocol):
    def add(self, order: RealTimeOrder) -> None: ...

    def list(self) -> Iterable[RealTimeOrder]: ...

    def mark_filled(self, order_id: str) -> bool: ...

    def remove(self, order_id: str) -> bool: ...


class InstrumentPort(Protocol):
    def list(self) -> InstrumentList: ...

    def get(self, symbol: Symbol) -> Instrument: ...
