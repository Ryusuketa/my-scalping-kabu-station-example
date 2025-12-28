import json
from datetime import datetime, timezone

from my_scalping_kabu_station_example.application.service.pipelines.inference_pipeline import (
    InferencePipeline,
)
from my_scalping_kabu_station_example.application.service.state.stream_state import (
    StreamState,
)
from my_scalping_kabu_station_example.domain.decision.policy import DecisionPolicy
from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.features.expr import MicroPrice
from my_scalping_kabu_station_example.domain.features.spec import (
    FeatureDef,
    FeatureSpec,
)
from my_scalping_kabu_station_example.infrastructure.compute.feature_engine_pandas import (
    PandasOrderBookFeatureEngine,
)
from my_scalping_kabu_station_example.infrastructure.memory.order_port import (
    InMemoryOrderPort,
)
from my_scalping_kabu_station_example.infrastructure.memory.order_store import (
    InMemoryOrderStore,
)
from my_scalping_kabu_station_example.infrastructure.memory.position_port import (
    InMemoryPositionPort,
)
from my_scalping_kabu_station_example.infrastructure.memory.ring_buffer import (
    InMemoryMarketBuffer,
)
from my_scalping_kabu_station_example.infrastructure.ml.xgb_predictor import (
    XgbPredictor,
)
from my_scalping_kabu_station_example.infrastructure.persistence.csv_history_store import (
    CsvHistoryStore,
)
from my_scalping_kabu_station_example.infrastructure.persistence.model_store_fs import (
    ModelStoreFs,
    SymbolModelStore,
)
from tests.helpers.mock_ws_client import MockWebSocketClient
from my_scalping_kabu_station_example.infrastructure.websocket.market_data import (
    WebSocketMarketDataSource,
)


def _ws_message(ts: datetime, symbol: str, bid: float, ask: float) -> str:
    return json.dumps(
        {
            "ts": ts.isoformat(),
            "symbol": symbol,
            "bids": [[str(bid), 1.0]],
            "asks": [[str(ask), 2.0]],
        }
    )


def test_inference_pipeline_runs_full_flow(tmp_path) -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    messages = [_ws_message(ts, "TEST", 100.0, 100.5)]
    market_data = WebSocketMarketDataSource(
        client=MockWebSocketClient(messages=messages)
    )
    market_data.subscribe()
    history_store = CsvHistoryStore(path=tmp_path / "history.csv")
    buffer = InMemoryMarketBuffer()
    feature_engine = PandasOrderBookFeatureEngine()
    predictor = XgbPredictor(
        feature_order=["microprice"], model=None, default_score=1.0
    )
    model_store = ModelStoreFs(base_dir=tmp_path / "models")
    model_store.save_candidate(predictor)
    model_store.swap_active(predictor)
    order_store = InMemoryOrderStore()
    order_port = InMemoryOrderPort(order_store=order_store)
    position_port = InMemoryPositionPort(position=0.5)
    decision_policy = DecisionPolicy(score_threshold=0.5, lot_size=1.0)
    feature_spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef(name="microprice", expr=MicroPrice(eps=1e-9))],
    )
    risk_params = RiskParams(max_position=2.0, stop_loss=1.0, take_profit=1.0)
    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=history_store,
        buffer=buffer,
        feature_engine=feature_engine,
        model_store=model_store,
        order_port=order_port,
        position_port=position_port,
        order_state=order_store,
        feature_spec=feature_spec,
        decision_policy=decision_policy,
        risk_params=risk_params,
    )
    state = StreamState()

    pipeline.run_once(state)

    assert len(order_port.intents) == 1
    assert order_port.intents[0].symbol == "TEST"
    assert state.prev_snapshot is not None
    assert state.feature_state.last_ts == state.prev_snapshot.ts


def test_inference_pipeline_skips_order_when_score_below_threshold(tmp_path) -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    messages = [_ws_message(ts, "TEST", 100.0, 100.5)]
    market_data = WebSocketMarketDataSource(
        client=MockWebSocketClient(messages=messages)
    )
    market_data.subscribe()
    history_store = CsvHistoryStore(path=tmp_path / "history.csv")
    buffer = InMemoryMarketBuffer()
    feature_engine = PandasOrderBookFeatureEngine()
    predictor = XgbPredictor(
        feature_order=["microprice"], model=None, default_score=0.1
    )
    model_store = ModelStoreFs(base_dir=tmp_path / "models")
    model_store.save_candidate(predictor)
    model_store.swap_active(predictor)
    order_store = InMemoryOrderStore()
    order_port = InMemoryOrderPort(order_store=order_store)
    position_port = InMemoryPositionPort(position=0.0)
    decision_policy = DecisionPolicy(score_threshold=0.5, lot_size=1.0)
    feature_spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef(name="microprice", expr=MicroPrice(eps=1e-9))],
    )
    risk_params = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=history_store,
        buffer=buffer,
        feature_engine=feature_engine,
        model_store=model_store,
        order_port=order_port,
        position_port=position_port,
        order_state=order_store,
        feature_spec=feature_spec,
        decision_policy=decision_policy,
        risk_params=risk_params,
    )
    state = StreamState()

    pipeline.run_once(state)

    assert order_port.intents == []


def test_inference_pipeline_skips_inference_when_model_missing(tmp_path) -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    messages = [_ws_message(ts, "TEST", 100.0, 100.5)]
    market_data = WebSocketMarketDataSource(
        client=MockWebSocketClient(messages=messages)
    )
    market_data.subscribe()
    history_store = CsvHistoryStore(path=tmp_path / "history.csv")
    buffer = InMemoryMarketBuffer()
    feature_engine = PandasOrderBookFeatureEngine()
    model_store = ModelStoreFs(base_dir=tmp_path / "models")
    order_store = InMemoryOrderStore()
    order_port = InMemoryOrderPort(order_store=order_store)
    position_port = InMemoryPositionPort(position=0.0)
    decision_policy = DecisionPolicy(score_threshold=0.5, lot_size=1.0)
    feature_spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef(name="microprice", expr=MicroPrice(eps=1e-9))],
    )
    risk_params = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=history_store,
        buffer=buffer,
        feature_engine=feature_engine,
        model_store=model_store,
        order_port=order_port,
        position_port=position_port,
        order_state=order_store,
        feature_spec=feature_spec,
        decision_policy=decision_policy,
        risk_params=risk_params,
    )
    state = StreamState()

    pipeline.run_once(state)

    assert order_port.intents == []
    assert state.prev_snapshot is not None


def test_inference_pipeline_uses_symbol_specific_model(tmp_path) -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    messages = [
        _ws_message(ts, "AAA", 100.0, 100.5),
        _ws_message(ts, "BBB", 100.0, 100.5),
    ]
    market_data = WebSocketMarketDataSource(
        client=MockWebSocketClient(messages=messages)
    )
    market_data.subscribe()
    history_store = CsvHistoryStore(path=tmp_path / "history.csv")
    buffer = InMemoryMarketBuffer()
    feature_engine = PandasOrderBookFeatureEngine()
    models_root = tmp_path / "models"
    ModelStoreFs(base_dir=models_root / "AAA").swap_active(
        XgbPredictor(feature_order=["microprice"], model=None, default_score=1.0)
    )
    ModelStoreFs(base_dir=models_root / "BBB").swap_active(
        XgbPredictor(feature_order=["microprice"], model=None, default_score=0.0)
    )
    model_store = SymbolModelStore(base_dir=models_root)
    order_store = InMemoryOrderStore()
    order_port = InMemoryOrderPort(order_store=order_store)
    position_port = InMemoryPositionPort(position=0.0)
    decision_policy = DecisionPolicy(score_threshold=0.5, lot_size=1.0)
    feature_spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef(name="microprice", expr=MicroPrice(eps=1e-9))],
    )
    risk_params = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    pipeline = InferencePipeline(
        market_data=market_data,
        history_store=history_store,
        buffer=buffer,
        feature_engine=feature_engine,
        model_store=model_store,
        order_port=order_port,
        position_port=position_port,
        order_state=order_store,
        feature_spec=feature_spec,
        decision_policy=decision_policy,
        risk_params=risk_params,
    )
    state = StreamState()

    pipeline.run_once(state)
    pipeline.run_once(state)

    assert len(order_port.intents) == 1
    assert order_port.intents[0].symbol == "AAA"
