"""Mapping between DTOs and domain snapshots."""

from __future__ import annotations

from datetime import datetime

from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import (
    Quantity,
    Symbol,
    price_key_from,
)
from my_scalping_kabu_station_example.infrastructure.websocket.dto import OrderBookDto


def to_domain(dto: OrderBookDto) -> OrderBookSnapshot:
    """Normalize a WebSocket DTO into a domain snapshot."""

    ts = dto.ts
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)

    bids = sorted(dto.bids, key=lambda item: price_key_from(item[0]), reverse=True)[:10]
    asks = sorted(dto.asks, key=lambda item: price_key_from(item[0]))[:10]
    bid_levels = [Level(price_key_from(price), Quantity(qty)) for price, qty in bids]
    ask_levels = [Level(price_key_from(price), Quantity(qty)) for price, qty in asks]

    return OrderBookSnapshot(
        ts=Timestamp(ts),
        symbol=Symbol(dto.symbol),
        bid_levels=bid_levels,
        ask_levels=ask_levels,
    )
