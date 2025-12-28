import pytest

from my_scalping_kabu_station_example.domain.decision.signal import OrderSide, TradeIntent
from my_scalping_kabu_station_example.domain.market.types import Symbol
from my_scalping_kabu_station_example.infrastructure.api.mapper import build_order_payload, to_order_payload


def test_to_order_payload_includes_intent_fields() -> None:
    intent = TradeIntent(
        intent_id="abc",
        side=OrderSide.BUY,
        quantity=5.0,
        symbol=Symbol("1234"),
        price=0,
        metadata={
            "Exchange": 1,
            "SecurityType": 1,
            "CashMargin": 1,
            "DelivType": 0,
            "AccountType": 2,
            "ExpireDay": 0,
            "FrontOrderType": 10,
        },
    )

    payload = to_order_payload(intent)

    assert payload["Symbol"] == Symbol("1234")
    assert payload["Price"] == 0
    assert payload["Side"] == "2"
    assert payload["Qty"] == 500


def test_build_order_payload_applies_side_override() -> None:
    intent = TradeIntent(
        intent_id="abc",
        side=OrderSide.SELL,
        quantity=1.0,
        symbol=Symbol("1234"),
        price=0,
        metadata={
            "Exchange": 1,
            "SecurityType": 1,
            "CashMargin": 1,
            "DelivType": 0,
            "AccountType": 2,
            "ExpireDay": 0,
            "FrontOrderType": 10,
        },
    )

    payload = build_order_payload(intent, side_override=OrderSide.BUY)

    assert payload["Symbol"] == Symbol("1234")
    assert payload["Price"] == 0
    assert payload["Side"] == "2"


def test_to_order_payload_requires_fields() -> None:
    intent = TradeIntent(intent_id="abc", side=OrderSide.SELL, quantity=1.0, symbol=Symbol("1234"), price=0.0)

    with pytest.raises(ValueError):
        to_order_payload(intent)
