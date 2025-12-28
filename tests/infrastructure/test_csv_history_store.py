from datetime import datetime, timedelta, timezone

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
from my_scalping_kabu_station_example.infrastructure.persistence.csv_history_store import (
    CsvHistoryStore,
)


def _make_snapshot(ts: datetime, bid_price: str, ask_price: str) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        ts=Timestamp(ts),
        symbol=Symbol("TEST"),
        bid_levels=[Level(price_key_from(bid_price), Quantity(1.0))],
        ask_levels=[Level(price_key_from(ask_price), Quantity(2.0))],
    )


def test_csv_history_store_persists_and_reads(tmp_path) -> None:
    path = tmp_path / "history.csv"
    store = CsvHistoryStore(path=path)
    ts0 = datetime(2024, 1, 1, 10, 59, 59, tzinfo=timezone.utc)
    ts1 = ts0 + timedelta(seconds=2)
    snap0 = _make_snapshot(ts0, bid_price="100.0", ask_price="100.5")
    snap1 = _make_snapshot(ts1, bid_price="100.1", ask_price="100.6")

    store.append(snap0)
    store.append(snap1)
    loaded = list(store.read_range(ts0, ts1))

    assert len(loaded) == 2
    assert loaded[0].best_bid_price == snap0.best_bid_price
    assert loaded[1].best_ask_price == snap1.best_ask_price


def test_csv_history_store_filters_by_time(tmp_path) -> None:
    path = tmp_path / "history.csv"
    store = CsvHistoryStore(path=path)
    ts0 = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
    ts1 = ts0 + timedelta(minutes=30)
    snap0 = _make_snapshot(ts0, bid_price="100.0", ask_price="100.5")
    snap1 = _make_snapshot(ts1, bid_price="100.1", ask_price="100.6")

    store.append(snap0)
    store.append(snap1)
    loaded = list(store.read_range(ts0, ts0))

    assert len(loaded) == 1
    assert loaded[0].best_bid_price == snap0.best_bid_price
