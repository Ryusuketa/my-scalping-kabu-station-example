"""Realtime order handler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from my_scalping_kabu_station_example.application.ports.broker import OrderStatePort
from my_scalping_kabu_station_example.infrastructure.api.broker_client import (
    BrokerClient,
)


@dataclass
class OrderHandler:
    order_store: OrderStatePort
    broker_client: BrokerClient
    api_key: str

    def refresh(self) -> None:
        """Poll order status and update in-memory state."""

        for order in list(self.order_store.list()):
            orders = self.broker_client.list_orders(self.api_key, order.order_id)
            if self._is_filled(orders, order.order_id):
                self.order_store.mark_filled(order.order_id)
                if order.cash_margin == 3:
                    self.order_store.remove(order.order_id)

    @staticmethod
    def _is_filled(orders: Iterable[Mapping[str, object]], order_id: str) -> bool:
        for entry in orders:
            if str(entry.get("ID")) != order_id:
                continue
            order_qty = entry.get("OrderQty")
            cum_qty = entry.get("CumQty")
            try:
                if order_qty is not None and cum_qty is not None:
                    return float(cum_qty) >= float(order_qty) and float(order_qty) > 0
            except (TypeError, ValueError):
                continue
        return False
