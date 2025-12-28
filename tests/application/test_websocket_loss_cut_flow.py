import json
from datetime import datetime, timezone
from typing import List

from my_scalping_kabu_station_example.application.service.order_handler import OrderHandler
from my_scalping_kabu_station_example.application.service.pipelines.inference_pipeline import InferencePipeline
from my_scalping_kabu_station_example.application.service.state.feature_state import FeatureState
from my_scalping_kabu_station_example.application.service.state.stream_state import StreamState
from my_scalping_kabu_station_example.domain.decision.policy import DecisionPolicy
from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import InferenceResult
from my_scalping_kabu_station_example.domain.features.expr import Const
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.infrastructure.api.broker_client import KabuOrderPort
from my_scalping_kabu_station_example.infrastructure.memory.order_store import InMemoryOrderStore
from my_scalping_kabu_station_example.infrastructure.memory.ring_buffer import InMemoryMarketBuffer
from my_scalping_kabu_station_example.infrastructure.websocket.client import MockWebSocketClient
from my_scalping_kabu_station_example.infrastructure.websocket.dto import OrderBookDto
from my_scalping_kabu_station_example.infrastructure.websocket.mapper import to_domain


class MockWebSocketMarketData:
    def __init__(self, messages: List[str]) -> None:
        self.client = MockWebSocketClient(messages=messages)

    def subscribe(self) -> None:
        self.client.connect()

    def close(self) -> None:
        self.client.close()

    def receive(self):
        payload = self.client.receive()
        data = json.loads(payload)
        dto = OrderBookDto(ts=data["ts"], symbol=data["symbol"], bids=data["bids"], asks=data["asks"])
        return to_domain(dto)


class DummyHistoryStore:
    def __init__(self) -> None:
        self.appended = []

    def append(self, snapshot) -> None:
        self.appended.append(snapshot)

    def read_range(self, *_args, **_kwargs):  # pragma: no cover - unused
        return []


class DummyFeatureEngine:
    def compute_one(self, *_args, **_kwargs):
        return {"x": 0.0}, FeatureState()

    def compute_batch(self, *_args, **_kwargs):  # pragma: no cover - unused
        return []


class SequencedPredictor:
    def __init__(self, scores: List[float]) -> None:
        self.scores = scores

    def predict(self, features):
        score = self.scores.pop(0)
        return InferenceResult(features=features, score=score)


class DummyModelStore:
    def __init__(self, predictor) -> None:
        self.predictor = predictor

    def load_active(self):
        return self.predictor

    def save_candidate(self, *_args, **_kwargs):  # pragma: no cover - unused
        return None

    def swap_active(self, *_args, **_kwargs):  # pragma: no cover - unused
        return None


class DummyPositionPort:
    def current_position(self) -> float:
        return 0.0


class DummyBrokerClient:
    def __init__(self) -> None:
        self.order_id = "o1"
        self.filled = False

    def place_order(self, _data, api_key=None):
        _ = api_key
        return {"OrderId": self.order_id}

    def list_orders(self, _api_key, order_id):
        if self.filled and order_id == self.order_id:
            return [{"ID": order_id, "OrderQty": 100, "CumQty": 100}]
        return []


def _ws_message(ts: datetime, symbol: str, bid: float, ask: float) -> str:
    return json.dumps(
        {
            "ts": ts.isoformat(),
            "symbol": symbol,
            "bids": [[str(bid), 1.0]],
            "asks": [[str(ask), 1.0]],
        }
    )


def test_websocket_flow_places_loss_cut_after_fill() -> None:
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts1 = datetime(2024, 1, 1, 0, 0, 1, tzinfo=timezone.utc)
    messages = [
        _ws_message(ts0, "TEST", 100.0, 100.5),
        _ws_message(ts1, "TEST", 98.0, 98.5),
    ]
    market_data = MockWebSocketMarketData(messages)
    market_data.subscribe()

    order_store = InMemoryOrderStore()
    broker_client = DummyBrokerClient()
    order_port = KabuOrderPort(
        client=broker_client,
        api_key="token",
        base_payload={
            "Exchange": 9,
            "SecurityType": 1,
            "DelivType": 0,
            "AccountType": 2,
            "ExpireDay": 0,
            "FrontOrderType": 10,
        },
        order_store=order_store,
    )
    order_handler = OrderHandler(order_store=order_store, broker_client=broker_client, api_key="token")
    predictor = SequencedPredictor([1.0, 0.0])
    model_store = DummyModelStore(predictor)
    feature_spec = FeatureSpec(version="v1", eps=1e-9, params={}, features=[FeatureDef("x", Const(1.0))])
    policy = DecisionPolicy(score_threshold=0.5, lot_size=1.0)
    risk = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=0.0, loss_cut_pips=1.0)

    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=DummyHistoryStore(),
        buffer=InMemoryMarketBuffer(),
        feature_engine=DummyFeatureEngine(),
        model_store=model_store,
        order_port=order_port,
        position_port=DummyPositionPort(),
        order_state=order_store,
        feature_spec=feature_spec,
        decision_policy=policy,
        risk_params=risk,
    )
    state = StreamState()

    pipeline.run_once(state)
    broker_client.filled = True
    order_handler.refresh()

    pipeline.run_once(state)

    assert len(order_store.list()) >= 2
    loss_cut_order = order_store.list()[-1]
    assert loss_cut_order.cash_margin == 3
