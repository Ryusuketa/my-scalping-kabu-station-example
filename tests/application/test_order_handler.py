from my_scalping_kabu_station_example.application.service.order_handler import OrderHandler
from my_scalping_kabu_station_example.domain.decision.signal import OrderSide
from my_scalping_kabu_station_example.domain.market.types import Symbol
from my_scalping_kabu_station_example.domain.order.realtime_order import RealTimeOrder
from my_scalping_kabu_station_example.infrastructure.memory.order_store import InMemoryOrderStore


class DummyBrokerClient:
    def __init__(self, responses) -> None:
        self.responses = responses
        self.calls = []

    def list_orders(self, _api_key: str, order_id: str):
        self.calls.append(order_id)
        return self.responses.get(order_id, [])


def test_order_handler_marks_filled() -> None:
    store = InMemoryOrderStore()
    order = RealTimeOrder(
        symbol=Symbol("TEST"),
        qty=100,
        side=OrderSide.BUY,
        cash_margin=2,
        order_id="o1",
        price=100.0,
    )
    store.add(order)
    broker = DummyBrokerClient(
        {
            "o1": [{"ID": "o1", "OrderQty": 100, "CumQty": 100}],
        }
    )
    handler = OrderHandler(order_store=store, broker_client=broker, api_key="k")

    handler.refresh()

    assert store.list()[0].is_filled is True


def test_order_handler_removes_repayment_orders() -> None:
    store = InMemoryOrderStore()
    order = RealTimeOrder(
        symbol=Symbol("TEST"),
        qty=100,
        side=OrderSide.SELL,
        cash_margin=3,
        order_id="o2",
        price=100.0,
    )
    store.add(order)
    broker = DummyBrokerClient(
        {
            "o2": [{"ID": "o2", "OrderQty": 100, "CumQty": 100}],
        }
    )
    handler = OrderHandler(order_store=store, broker_client=broker, api_key="k")

    handler.refresh()

    assert store.list() == []
