from datetime import datetime, timezone
from decimal import Decimal

import pytest

from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import (
    PriceKey,
    Quantity,
    Side,
    Symbol,
    price_key_from,
)


def test_orderbook_snapshot_computes_mid_and_maps() -> None:
    ts = Timestamp(datetime(2024, 1, 1, tzinfo=timezone.utc))
    bids = [
        Level(price_key_from("100.0"), Quantity(1.0)),
        Level(price_key_from("99.8"), Quantity(2.0)),
    ]
    asks = [
        Level(price_key_from("100.5"), Quantity(1.5)),
        Level(price_key_from("101.0"), Quantity(2.5)),
    ]

    snapshot = OrderBookSnapshot(ts=ts, symbol=Symbol("TEST"), bid_levels=bids, ask_levels=asks)

    assert snapshot.best_bid_price == price_key_from("100.0")
    assert snapshot.best_ask_price == price_key_from("100.5")
    assert snapshot.mid == PriceKey(Decimal("100.25"))
    assert snapshot.bid_map[price_key_from("100.0")] == Quantity(1.0)
    assert snapshot.ask_map[price_key_from("101.0")] == Quantity(2.5)
    assert snapshot.depth_levels(Side.BID)[0].price == price_key_from("100.0")
    assert snapshot.depth_levels(Side.ASK)[0].price == price_key_from("100.5")


def test_invalid_sorting_raises() -> None:
    ts = Timestamp(datetime(2024, 1, 1, tzinfo=timezone.utc))
    bids = [
        Level(price_key_from("99.8"), Quantity(1.0)),
        Level(price_key_from("100.0"), Quantity(1.0)),
    ]

    with pytest.raises(ValueError):
        OrderBookSnapshot(ts=ts, symbol=Symbol("TEST"), bid_levels=bids, ask_levels=[])


def test_crossed_book_sets_mid_none() -> None:
    ts = Timestamp(datetime(2024, 1, 1, tzinfo=timezone.utc))
    bids = [Level(price_key_from("100.5"), Quantity(1.0))]
    asks = [Level(price_key_from("100.0"), Quantity(1.0))]

    snapshot = OrderBookSnapshot(ts=ts, symbol=Symbol("TEST"), bid_levels=bids, ask_levels=asks)

    assert snapshot.mid is None
