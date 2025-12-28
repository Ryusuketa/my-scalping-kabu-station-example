"""Inference pipeline skeleton."""

from __future__ import annotations

from my_scalping_kabu_station_example.application.ports.buffer import MarketBufferPort
from my_scalping_kabu_station_example.application.ports.feature_engine import (
    FeatureEnginePort,
)
from my_scalping_kabu_station_example.application.ports.history import HistoryStorePort
from my_scalping_kabu_station_example.application.ports.model import ModelStorePort
from my_scalping_kabu_station_example.application.ports.broker import (
    OrderPort,
    OrderStatePort,
    PositionPort,
)
from my_scalping_kabu_station_example.application.ports.market_data import (
    MarketDataSourcePort,
)
from my_scalping_kabu_station_example.domain.decision.policy import DecisionPolicy
from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import DecisionContext
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.application.service.state.stream_state import (
    StreamState,
)
from my_scalping_kabu_station_example.application.service.order_handler import (
    OrderHandler,
)


class InferencePipeline:
    def __init__(
        self,
        market_data: MarketDataSourcePort,
        history_store: HistoryStorePort,
        buffer: MarketBufferPort,
        feature_engine: FeatureEnginePort,
        model_store: ModelStorePort,
        order_port: OrderPort,
        position_port: PositionPort,
        feature_spec: FeatureSpec,
        decision_policy: DecisionPolicy,
        risk_params: RiskParams,
        order_state: OrderStatePort | None = None,
        order_handler: OrderHandler | None = None,
    ) -> None:
        self.market_data = market_data
        self.history_store = history_store
        self.buffer = buffer
        self.feature_engine = feature_engine
        self.model_store = model_store
        self.order_port = order_port
        self.position_port = position_port
        self.order_state = order_state
        self.feature_spec = feature_spec
        self.decision_policy = decision_policy
        self.risk_params = risk_params
        self.order_handler = order_handler

    def run_once(self, state: StreamState) -> None:
        """One inference iteration following normalize -> persist -> features -> predict -> decide -> order."""

        snapshot = self.market_data.receive()
        prev_snapshot = self.buffer.get_prev()
        self.history_store.append(snapshot)
        self.buffer.update(snapshot)
        if self.order_handler is not None:
            self.order_handler.refresh()

        try:
            load_active_for = getattr(self.model_store, "load_active_for", None)
            if load_active_for is not None:
                predictor = load_active_for(snapshot.symbol)
            else:
                predictor = self.model_store.load_active()
        except FileNotFoundError:
            state.prev_snapshot = snapshot
            return
        if predictor is None:
            state.prev_snapshot = snapshot
            return

        features, feature_state = self.feature_engine.compute_one(
            spec=self.feature_spec,
            prev_snapshot=prev_snapshot,
            now_snapshot=snapshot,
            state=state.feature_state,
        )

        inference = predictor.predict(features)

        open_order = None
        if self.order_state is not None:
            orders = [
                order
                for order in self.order_state.list()
                if order.symbol == snapshot.symbol
            ]
            open_order = orders[0] if orders else None

        best_bid = snapshot.best_bid_price
        best_ask = snapshot.best_ask_price
        pip_size = 1.0
        if best_bid is not None and best_ask is not None:
            spread = float(best_ask) - float(best_bid)
            if spread > 0:
                pip_size = spread

        context = DecisionContext(
            position_size=self.position_port.current_position(),
            risk_budget=self.risk_params.max_position,
            symbol=snapshot.symbol,
            price=float(snapshot.mid or 0.0),
            pip_size=pip_size,
            has_open_order=open_order is not None,
            open_order_side=open_order.side if open_order else None,
            open_order_price=open_order.price if open_order else None,
            open_order_qty=open_order.qty if open_order else None,
        )
        intent = self.decision_policy.decide(
            inference=inference, context=context, risk=self.risk_params
        )
        if intent is not None:
            self.order_port.place_order(intent)

        state.prev_snapshot = snapshot
        state.feature_state = feature_state
