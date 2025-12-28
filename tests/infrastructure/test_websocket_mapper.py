from datetime import datetime, timezone

from my_scalping_kabu_station_example.domain.market.types import price_key_from
from my_scalping_kabu_station_example.infrastructure.websocket.dto import OrderBookDto
from my_scalping_kabu_station_example.infrastructure.websocket.mapper import to_domain


def test_to_domain_sorts_levels_and_builds_snapshot() -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    dto = OrderBookDto(
        ts=ts,
        symbol="TEST",
        bids=[("99.0", 1.0), ("100.0", 2.0)],
        asks=[("101.0", 1.0), ("100.5", 2.0)],
    )

    snapshot = to_domain(dto)

    assert snapshot.best_bid_price == price_key_from("100.0")
    assert snapshot.best_ask_price == price_key_from("100.5")
    assert snapshot.bid_levels[0].price == price_key_from("100.0")
    assert snapshot.ask_levels[0].price == price_key_from("100.5")
