from datetime import datetime, timezone
from typing import Tuple

from my_scalping_kabu_station_example.application.ports.feature_engine import FeatureVector
from my_scalping_kabu_station_example.application.service.pipelines.inference_pipeline import InferencePipeline
from my_scalping_kabu_station_example.application.service.state.feature_state import FeatureState
from my_scalping_kabu_station_example.application.service.state.stream_state import StreamState
from my_scalping_kabu_station_example.domain.decision.policy import DecisionPolicy
from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import DecisionContext, InferenceResult, OrderSide, TradeIntent
from my_scalping_kabu_station_example.domain.features.expr import Const
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import Quantity, Symbol, price_key_from
from my_scalping_kabu_station_example.infrastructure.memory.ring_buffer import InMemoryMarketBuffer


def _make_snapshot(ts: datetime) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        ts=Timestamp(ts),
        symbol=Symbol("TEST"),
        bid_levels=[Level(price_key_from("100.0"), Quantity(1.0))],
        ask_levels=[Level(price_key_from("100.5"), Quantity(2.0))],
    )


class DummyMarketData:
    def __init__(self, snapshot: OrderBookSnapshot) -> None:
        self.snapshot = snapshot
        self.calls = 0

    def subscribe(self) -> None:  # pragma: no cover - not used in tests
        self.calls += 1

    def close(self) -> None:  # pragma: no cover - not used in tests
        self.calls += 1

    def receive(self) -> OrderBookSnapshot:
        self.calls += 1
        return self.snapshot


class DummyHistoryStore:
    def __init__(self) -> None:
        self.appended: list[OrderBookSnapshot] = []

    def append(self, snapshot: OrderBookSnapshot) -> None:
        self.appended.append(snapshot)

    def read_range(self, *_args, **_kwargs):  # pragma: no cover - not used
        return []


class DummyFeatureEngine:
    def __init__(self) -> None:
        self.calls: list[Tuple[OrderBookSnapshot | None, OrderBookSnapshot]] = []

    def compute_one(
        self,
        spec: FeatureSpec,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState | None,
    ) -> Tuple[FeatureVector, FeatureState]:
        self.calls.append((prev_snapshot, now_snapshot))
        return {"x": 42.0}, FeatureState(last_ts=now_snapshot.ts)

    def compute_batch(self, *_args, **_kwargs):  # pragma: no cover - not used
        return []


class DummyPredictor:
    def __init__(self) -> None:
        self.features: list[FeatureVector] = []

    def predict(self, features: FeatureVector) -> InferenceResult:
        self.features.append(features)
        return InferenceResult(features=features, score=1.0)


class DummyModelStore:
    def __init__(self, predictor: DummyPredictor) -> None:
        self.predictor = predictor
        self.loaded = 0

    def load_active(self) -> DummyPredictor:
        self.loaded += 1
        return self.predictor

    def save_candidate(self, *_args, **_kwargs):  # pragma: no cover - not used
        return None

    def swap_active(self, *_args, **_kwargs):  # pragma: no cover - not used
        return None


class MissingModelStore:
    def __init__(self) -> None:
        self.loaded = 0

    def load_active(self):
        self.loaded += 1
        raise FileNotFoundError

    def save_candidate(self, *_args, **_kwargs):  # pragma: no cover - not used
        return None

    def swap_active(self, *_args, **_kwargs):  # pragma: no cover - not used
        return None


class DummyOrderPort:
    def __init__(self) -> None:
        self.intents: list[TradeIntent] = []

    def place_order(self, intent: TradeIntent) -> str:
        self.intents.append(intent)
        return intent.intent_id


class DummyPositionPort:
    def __init__(self, position: float) -> None:
        self.position = position

    def current_position(self) -> float:
        return self.position


class DummyDecisionPolicy(DecisionPolicy):
    def __init__(self, intent: TradeIntent | None) -> None:
        self.intent = intent
        self.called_with: list[tuple[InferenceResult, DecisionContext, RiskParams]] = []

    def decide(self, inference: InferenceResult, context: DecisionContext, risk: RiskParams) -> TradeIntent | None:
        self.called_with.append((inference, context, risk))
        return self.intent


def test_inference_pipeline_runs_full_flow() -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    snapshot = _make_snapshot(ts)
    market_data = DummyMarketData(snapshot)
    history_store = DummyHistoryStore()
    buffer = InMemoryMarketBuffer()
    feature_engine = DummyFeatureEngine()
    predictor = DummyPredictor()
    model_store = DummyModelStore(predictor)
    order_port = DummyOrderPort()
    position_port = DummyPositionPort(position=0.5)
    intent = TradeIntent(intent_id="abc", side=OrderSide.BUY, quantity=1.0)
    decision_policy = DummyDecisionPolicy(intent=intent)
    feature_spec = FeatureSpec(version="v1", eps=1e-9, params={}, features=[FeatureDef(name="x", expr=Const(1.0))])
    risk_params = RiskParams(max_position=2.0, stop_loss=1.0, take_profit=1.0)
    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=history_store,
        buffer=buffer,
        feature_engine=feature_engine,
        model_store=model_store,
        order_port=order_port,
        position_port=position_port,
        feature_spec=feature_spec,
        decision_policy=decision_policy,
        risk_params=risk_params,
    )
    state = StreamState()

    pipeline.run_once(state)

    assert history_store.appended == [snapshot]
    assert buffer.get_prev() == snapshot
    assert feature_engine.calls[0] == (None, snapshot)
    assert predictor.features[0] == {"x": 42.0}
    assert decision_policy.called_with[0][1].position_size == 0.5
    assert order_port.intents == [intent]
    assert state.prev_snapshot == snapshot
    assert state.feature_state.last_ts == snapshot.ts


def test_inference_pipeline_skips_order_when_policy_returns_none() -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    snapshot = _make_snapshot(ts)
    market_data = DummyMarketData(snapshot)
    history_store = DummyHistoryStore()
    buffer = InMemoryMarketBuffer()
    feature_engine = DummyFeatureEngine()
    predictor = DummyPredictor()
    model_store = DummyModelStore(predictor)
    order_port = DummyOrderPort()
    position_port = DummyPositionPort(position=0.0)
    decision_policy = DummyDecisionPolicy(intent=None)
    feature_spec = FeatureSpec(version="v1", eps=1e-9, params={}, features=[FeatureDef(name="x", expr=Const(1.0))])
    risk_params = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=history_store,
        buffer=buffer,
        feature_engine=feature_engine,
        model_store=model_store,
        order_port=order_port,
        position_port=position_port,
        feature_spec=feature_spec,
        decision_policy=decision_policy,
        risk_params=risk_params,
    )
    state = StreamState()

    pipeline.run_once(state)

    assert order_port.intents == []


def test_inference_pipeline_skips_inference_when_model_missing() -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    snapshot = _make_snapshot(ts)
    market_data = DummyMarketData(snapshot)
    history_store = DummyHistoryStore()
    buffer = InMemoryMarketBuffer()
    feature_engine = DummyFeatureEngine()
    model_store = MissingModelStore()
    order_port = DummyOrderPort()
    position_port = DummyPositionPort(position=0.0)
    decision_policy = DummyDecisionPolicy(intent=None)
    feature_spec = FeatureSpec(version="v1", eps=1e-9, params={}, features=[FeatureDef(name="x", expr=Const(1.0))])
    risk_params = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=history_store,
        buffer=buffer,
        feature_engine=feature_engine,
        model_store=model_store,
        order_port=order_port,
        position_port=position_port,
        feature_spec=feature_spec,
        decision_policy=decision_policy,
        risk_params=risk_params,
    )
    state = StreamState()

    pipeline.run_once(state)

    assert history_store.appended == [snapshot]
    assert feature_engine.calls == []
    assert order_port.intents == []
    assert state.prev_snapshot == snapshot
