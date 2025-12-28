"""REST client placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import requests


@dataclass
class BrokerClient:
    base_url: str
    timeout_seconds: float = 5.0

    def place_order(self, data: Mapping[str, Any]) -> Mapping[str, Any]:
        response = requests.post(f"{self.base_url}/orders", json=data, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()
