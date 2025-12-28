from my_scalping_kabu_station_example.domain.decision.signal import OrderSide, TradeIntent
from my_scalping_kabu_station_example.domain.market.types import Symbol
from my_scalping_kabu_station_example.infrastructure.api.mapper import to_api


def test_to_api_maps_trade_intent() -> None:
    intent = TradeIntent(intent_id="abc", side=OrderSide.BUY, quantity=1.5, metadata={"symbol": "TEST"})

    dto = to_api(intent)

    assert dto.intent_id == "abc"
    assert dto.side == OrderSide.BUY
    assert dto.quantity == 1.5
    assert dto.symbol == Symbol("TEST")
