"""Broker and position ports."""

from __future__ import annotations

from typing import Iterable, Protocol

from my_scalping_kabu_station_example.domain.decision.signal import OrderSide, TradeIntent
from my_scalping_kabu_station_example.domain.instruments.instrument import Instrument
from my_scalping_kabu_station_example.domain.instruments.registry import InstrumentList
from my_scalping_kabu_station_example.domain.market.types import Symbol
from my_scalping_kabu_station_example.domain.order.realtime_order import RealTimeOrder


class OrderPort(Protocol):
    def place_order(self, intent: TradeIntent) -> str:
        ...


class PositionPort(Protocol):
    def current_position(self) -> float:
        ...


class OrderStatePort(Protocol):
    def add(self, order: RealTimeOrder) -> None:
        ...

    def list(self) -> Iterable[RealTimeOrder]:
        ...


class InstrumentPort(Protocol):
    def list(self) -> InstrumentList:
        ...

    def get(self, symbol: Symbol) -> Instrument:
        ...
