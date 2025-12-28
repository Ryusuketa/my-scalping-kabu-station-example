"""In-memory order port for local runs/tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from my_scalping_kabu_station_example.application.ports.broker import OrderPort, OrderStatePort
from my_scalping_kabu_station_example.domain.decision.signal import TradeIntent
from my_scalping_kabu_station_example.domain.order.realtime_order import RealTimeOrder


@dataclass
class InMemoryOrderPort(OrderPort):
    order_store: OrderStatePort | None = None
    intents: list[TradeIntent] = field(default_factory=list)
    lot_multiplier: int = 100

    def place_order(self, intent: TradeIntent) -> str:
        self.intents.append(intent)
        if self.order_store is not None:
            order = RealTimeOrder(
                symbol=intent.symbol,
                qty=int(intent.quantity * self.lot_multiplier),
                side=intent.side,
                cash_margin=int(intent.cash_margin),
                order_id=intent.intent_id,
                price=float(intent.price),
            )
            self.order_store.add(order)
        return intent.intent_id
