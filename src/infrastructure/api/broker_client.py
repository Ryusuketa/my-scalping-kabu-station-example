"""REST client placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from application.ports.broker import OrderStatePort
    from domain.decision.signal import OrderSide


@dataclass
class BrokerClient:
    base_url: str
    timeout_seconds: float = 5.0

    def place_order(
        self, data: Mapping[str, Any], api_key: str | None = None
    ) -> Mapping[str, Any]:
        headers = {"X-API-KEY": api_key} if api_key else None
        response = requests.post(
            f"{self.base_url}/sendorder",
            json=data,
            headers=headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def list_orders(self, api_key: str, order_id: str) -> list[Mapping[str, Any]]:
        params = {"id": order_id}
        headers = {"X-API-KEY": api_key}
        response = requests.get(
            f"{self.base_url}/orders",
            params=params,
            headers=headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return list(response.json())


@dataclass
class KabuOrderPort:
    client: BrokerClient
    api_key: str
    base_payload: Mapping[str, Any]
    side_override: "OrderSide | None" = None
    order_store: "OrderStatePort | None" = None

    def place_order(self, intent) -> str:
        from infrastructure.api.mapper import (
            build_order_payload,
        )

        payload = build_order_payload(
            intent, base_payload=self.base_payload, side_override=self.side_override
        )
        response = self.client.place_order(payload, api_key=self.api_key)
        order_id = str(response.get("OrderId") or intent.intent_id)
        if self.order_store is not None:
            from domain.order.realtime_order import (
                RealTimeOrder,
            )

            cash_margin = int(payload["CashMargin"])
            qty = int(payload["Qty"])
            price = float(payload["Price"])
            order = RealTimeOrder(
                symbol=intent.symbol,
                qty=qty,
                side=self.side_override or intent.side,
                cash_margin=cash_margin,
                order_id=order_id,
                price=price,
            )
            self.order_store.add(order)
        return order_id
