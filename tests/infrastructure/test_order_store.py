from my_scalping_kabu_station_example.domain.decision.signal import OrderSide, TradeIntent
from my_scalping_kabu_station_example.domain.market.types import Symbol
from my_scalping_kabu_station_example.domain.order.realtime_order import RealTimeOrder
from my_scalping_kabu_station_example.infrastructure.memory.order_store import InMemoryOrderStore


def test_in_memory_order_store_records_orders() -> None:
    store = InMemoryOrderStore()
    order = RealTimeOrder(symbol=Symbol("TEST"), qty=100, side=OrderSide.BUY, cash_margin=2, order_id="o1", price=100.0)

    store.add(order)

    assert store.list() == [order]
