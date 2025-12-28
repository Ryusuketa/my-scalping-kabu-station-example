from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Iterable, List

import requests

from my_scalping_kabu_station_example.application.ports.feature_engine import FeatureVector
from my_scalping_kabu_station_example.application.service.pipelines.inference_pipeline import InferencePipeline
from my_scalping_kabu_station_example.application.service.state.stream_state import StreamState
from my_scalping_kabu_station_example.domain.decision.policy import DecisionPolicy
from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import InferenceResult, OrderSide, TradeIntent
from my_scalping_kabu_station_example.domain.features import names
from my_scalping_kabu_station_example.domain.features.expr import (
    Add,
    AddSum,
    BestAskPrice,
    BestAskQty,
    BestBidPrice,
    BestBidQty,
    Const,
    DepletionSum,
    DepthQtySum,
    Div,
    MicroPrice,
    Mid,
    Sub,
    TimeDecayEma,
)
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import Quantity, Side, Symbol, price_key_from
from my_scalping_kabu_station_example.infrastructure.compute.feature_engine_pandas import PandasOrderBookFeatureEngine
from my_scalping_kabu_station_example.infrastructure.memory.ring_buffer import InMemoryMarketBuffer
from my_scalping_kabu_station_example.infrastructure.api.broker_client import BrokerClient, KabuOrderPort
from my_scalping_kabu_station_example.infrastructure.persistence.csv_history_store import CsvHistoryStore
from my_scalping_kabu_station_example.infrastructure.persistence.model_store_fs import ModelStoreFs
from my_scalping_kabu_station_example.infrastructure.websocket.client import WebSocketClient
from my_scalping_kabu_station_example.infrastructure.websocket.dto import OrderBookDto
from my_scalping_kabu_station_example.infrastructure.websocket.mapper import to_domain


class SimpleMarketDataSource:
    def __init__(self, snapshots: Iterable[OrderBookSnapshot]) -> None:
        self._snapshots = iter(snapshots)

    def subscribe(self) -> None:
        return None

    def close(self) -> None:
        return None

    def receive(self) -> OrderBookSnapshot:
        return next(self._snapshots)


class WebSocketMarketDataSource:
    def __init__(self, url: str) -> None:
        self.client = WebSocketClient(url=url)

    def subscribe(self) -> None:
        self.client.connect()

    def close(self) -> None:
        self.client.close()

    def receive(self) -> OrderBookSnapshot:
        payload = self.client.receive()
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        data = json.loads(payload)
        dto = OrderBookDto(
            ts=data["ts"],
            symbol=data["symbol"],
            bids=data.get("bids", []),
            asks=data.get("asks", []),
        )
        return to_domain(dto)


class InMemoryModelStore:
    def __init__(self) -> None:
        self._predictor = SimplePredictor()

    def load_active(self) -> "SimplePredictor":
        return self._predictor

    def save_candidate(self, _predictor: "SimplePredictor") -> None:
        return None

    def swap_active(self, predictor: "SimplePredictor") -> None:
        self._predictor = predictor


class SimplePredictor:
    def predict(self, features: FeatureVector) -> InferenceResult:
        return InferenceResult(features=features, score=0.0)


class LoggingOrderPort:
    def place_order(self, intent: TradeIntent) -> str:
        print(f"order: {intent.intent_id} {intent.side.value} qty={intent.quantity}")
        return intent.intent_id


class FixedPositionPort:
    def __init__(self, position: float = 0.0) -> None:
        self._position = position

    def current_position(self) -> float:
        return self._position


def _fetch_api_token(base_url: str, api_password: str) -> str:
    response = requests.post(
        f"{base_url}/token",
        json={"APIPassword": api_password},
        timeout=5.0,
    )
    response.raise_for_status()
    payload = response.json()
    result_code = payload.get("ResultCode")
    if result_code not in (None, 0):
        raise RuntimeError(f"Token request failed with code {result_code}")
    token = payload.get("Token")
    if not token:
        raise RuntimeError("Token not present in response")
    return str(token)


def _build_feature_spec() -> FeatureSpec:
    eps = 1e-9
    depth_bid = DepthQtySum(Side.BID, depth=5)
    depth_ask = DepthQtySum(Side.ASK, depth=5)
    obi = Div(Sub(depth_bid, depth_ask), Add(Add(depth_bid, depth_ask), Const(eps)))
    di_num = Sub(DepletionSum(Side.ASK), DepletionSum(Side.BID))
    di_den = Add(Add(DepletionSum(Side.ASK), DepletionSum(Side.BID)), Const(eps))
    ai_num = Sub(AddSum(Side.BID), AddSum(Side.ASK))
    ai_den = Add(Add(AddSum(Side.BID), AddSum(Side.ASK)), Const(eps))
    micro = MicroPrice(eps=eps)
    micro_shift = Sub(micro, Mid())
    return FeatureSpec.from_features(
        version="ob10_v1",
        eps=eps,
        params={"N_list": [5], "tau": 1.0},
        features=[
            FeatureDef(names.OBI_5, expr=obi),
            FeatureDef(names.MICROPRICE, expr=micro),
            FeatureDef(names.MICROPRICE_SHIFT, expr=micro_shift),
            FeatureDef(names.DEPLETION_IMBALANCE, expr=Div(di_num, di_den)),
            FeatureDef(names.ADD_IMBALANCE, expr=Div(ai_num, ai_den)),
            FeatureDef(names.DEPLETION_IMBALANCE_EMA, expr=TimeDecayEma(source=Div(di_num, di_den), tau_seconds=1.0)),
        ],
    )


def _mock_snapshots(count: int) -> List[OrderBookSnapshot]:
    now = datetime.now(timezone.utc)
    snapshots: List[OrderBookSnapshot] = []
    for i in range(count):
        ts = now + timedelta(milliseconds=200 * i)
        bid_price = price_key_from(100.0 + 0.1 * i)
        ask_price = price_key_from(100.5 + 0.1 * i)
        snapshots.append(
            OrderBookSnapshot(
                ts=Timestamp(ts),
                symbol=Symbol("TEST"),
                bid_levels=[Level(bid_price, Quantity(1.0 + 0.1 * i))],
                ask_levels=[Level(ask_price, Quantity(1.2 + 0.05 * i))],
            )
        )
    return snapshots


def main() -> None:
    api_base_url = os.getenv("KABU_API_BASE_URL", "http://localhost:18080/kabusapi")
    skip_auth = os.getenv("SKIP_KABU_AUTH", "").lower() in {"1", "true", "yes"}
    if not skip_auth:
        api_password = os.getenv("KABU_API_PASSWORD")
        if not api_password:
            raise RuntimeError("KABU_API_PASSWORD is required to fetch API token")
        token = _fetch_api_token(api_base_url, api_password)
        os.environ["KABU_API_TOKEN"] = token

    ws_url = os.getenv("WEBSOCKET_URL")
    max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))

    if ws_url:
        market_data = WebSocketMarketDataSource(ws_url)
        market_data.subscribe()
    else:
        market_data = SimpleMarketDataSource(_mock_snapshots(max_iterations))

    history_store = CsvHistoryStore(path=os.getenv("HISTORY_PATH", "data/history.csv"))
    buffer = InMemoryMarketBuffer()
    feature_engine = PandasOrderBookFeatureEngine()
    use_inmemory = os.getenv("USE_INMEMORY_MODEL", "").lower() in {"1", "true", "yes"}
    if use_inmemory:
        model_store = InMemoryModelStore()
    else:
        model_store = ModelStoreFs(base_dir=os.getenv("MODEL_DIR", "models"))
    use_api_order = os.getenv("USE_API_ORDER", "").lower() in {"1", "true", "yes"}
    if use_api_order:
        api_token = os.getenv("KABU_API_TOKEN")
        if not api_token:
            raise RuntimeError("KABU_API_TOKEN is required when USE_API_ORDER is enabled")
        side_override_value = os.getenv("ORDER_SIDE_OVERRIDE", "").upper()
        side_override = None
        if side_override_value in {"BUY", "SELL"}:
            side_override = OrderSide[side_override_value]

        order_payload = {
            "Exchange": int(os.getenv("ORDER_EXCHANGE", "9")),
            "SecurityType": int(os.getenv("ORDER_SECURITY_TYPE", "1")),
            "CashMargin": int(os.getenv("ORDER_CASH_MARGIN", "2")),
            "MarginTradeType": int(os.getenv("ORDER_MARGIN_TRADE_TYPE", "3")),
            "DelivType": int(os.getenv("ORDER_DELIV_TYPE", "0")),
            "AccountType": int(os.getenv("ORDER_ACCOUNT_TYPE", "2")),
            "Price": int(os.getenv("ORDER_PRICE", "0")),
            "ExpireDay": int(os.getenv("ORDER_EXPIRE_DAY", "0")),
            "FrontOrderType": int(os.getenv("ORDER_FRONT_ORDER_TYPE", "10")),
        }
        broker_client = BrokerClient(base_url=api_base_url)
        order_port = KabuOrderPort(
            client=broker_client,
            api_key=api_token,
            base_payload=order_payload,
            side_override=side_override,
        )
    else:
        order_port = LoggingOrderPort()
    position_port = FixedPositionPort()
    feature_spec = _build_feature_spec()
    decision_policy = DecisionPolicy(score_threshold=0.0, lot_size=1.0)
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
    for _ in range(max_iterations):
        pipeline.run_once(state)
    if ws_url:
        market_data.close()


if __name__ == "__main__":
    main()
