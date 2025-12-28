"""Mapping between DTOs and domain snapshots."""

from __future__ import annotations

from datetime import datetime

from domain.market.level import Level
from domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)
from domain.market.time import Timestamp
from domain.market.types import (
    Quantity,
    Symbol,
    price_key_from,
)
from infrastructure.websocket.dto import OrderBookDto


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
