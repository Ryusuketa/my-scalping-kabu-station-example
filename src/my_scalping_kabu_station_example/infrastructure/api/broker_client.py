"""REST client placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import requests


@dataclass
class BrokerClient:
    base_url: str
    timeout_seconds: float = 5.0

    def place_order(self, data: Mapping[str, Any], api_key: str | None = None) -> Mapping[str, Any]:
        headers = {"X-API-KEY": api_key} if api_key else None
        response = requests.post(
            f"{self.base_url}/sendorder",
            json=data,
            headers=headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


@dataclass
class KabuOrderPort:
    client: BrokerClient
    api_key: str
    base_payload: Mapping[str, Any]
    side_override: "OrderSide | None" = None

    def place_order(self, intent) -> str:
        from my_scalping_kabu_station_example.domain.decision.signal import OrderSide
        from my_scalping_kabu_station_example.infrastructure.api.mapper import build_order_payload

        payload = build_order_payload(intent, base_payload=self.base_payload, side_override=self.side_override)
        response = self.client.place_order(payload, api_key=self.api_key)
        return str(response.get("OrderId") or intent.intent_id)
