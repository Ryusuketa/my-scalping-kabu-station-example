"""WebSocket market data source adapter."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from my_scalping_kabu_station_example.application.ports.market_data import (
    MarketDataSourcePort,
)
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)
from my_scalping_kabu_station_example.infrastructure.websocket.client import (
    WebSocketClient,
)
from my_scalping_kabu_station_example.infrastructure.websocket.dto import OrderBookDto
from my_scalping_kabu_station_example.infrastructure.websocket.mapper import to_domain


def _ensure_text(payload: Any) -> str:
    if isinstance(payload, bytes):
        return payload.decode("utf-8")
    return str(payload)


@dataclass
class WebSocketMarketDataSource(MarketDataSourcePort):
    client: WebSocketClient

    def subscribe(self) -> None:
        self.client.connect()

    def close(self) -> None:
        self.client.close()

    def receive(self) -> OrderBookSnapshot:
        payload = _ensure_text(self.client.receive())
        data = json.loads(payload)
        dto = OrderBookDto(
            ts=_parse_ts(data["ts"]),
            symbol=data["symbol"],
            bids=data["bids"],
            asks=data["asks"],
        )
        return to_domain(dto)


def _parse_ts(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError(f"Unsupported timestamp: {value!r}")
