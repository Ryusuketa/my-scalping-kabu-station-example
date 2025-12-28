"""In-memory realtime order store."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from my_scalping_kabu_station_example.application.ports.broker import OrderStatePort
from my_scalping_kabu_station_example.domain.order.realtime_order import RealTimeOrder


@dataclass
class InMemoryOrderStore(OrderStatePort):
    orders: List[RealTimeOrder] = field(default_factory=list)

    def add(self, order: RealTimeOrder) -> None:
        self.orders.append(order)

    def list(self) -> List[RealTimeOrder]:
        return list(self.orders)
