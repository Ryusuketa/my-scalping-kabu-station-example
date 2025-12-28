"""Inference pipeline skeleton."""

from __future__ import annotations

from ...ports.buffer import MarketBufferPort
from ...ports.feature_engine import FeatureEnginePort
from ...ports.history import HistoryStorePort
from ...ports.model import ModelStorePort
from ...ports.broker import OrderPort, PositionPort
from ...ports.market_data import MarketDataSourcePort
from ....domain.decision.policy import DecisionPolicy
from ....domain.decision.risk import RiskParams
from ....domain.decision.signal import DecisionContext
from ....domain.features.spec import FeatureSpec
from ..state.stream_state import StreamState


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
    ) -> None:
        self.market_data = market_data
        self.history_store = history_store
        self.buffer = buffer
        self.feature_engine = feature_engine
        self.model_store = model_store
        self.order_port = order_port
        self.position_port = position_port
        self.feature_spec = feature_spec
        self.decision_policy = decision_policy
        self.risk_params = risk_params

    def run_once(self, state: StreamState) -> None:
        """One inference iteration following normalize -> persist -> features -> predict -> decide -> order."""

        snapshot = self.market_data.receive()
        prev_snapshot = self.buffer.get_prev()
        self.history_store.append(snapshot)
        self.buffer.update(snapshot)

        features, feature_state = self.feature_engine.compute_one(
            spec=self.feature_spec,
            prev_snapshot=prev_snapshot,
            now_snapshot=snapshot,
            state=state.feature_state,
        )

        predictor = self.model_store.load_active()
        inference = predictor.predict(features)

        context = DecisionContext(
            position_size=self.position_port.current_position(),
            risk_budget=self.risk_params.max_position,
        )
        intent = self.decision_policy.decide(inference=inference, context=context, risk=self.risk_params)
        if intent is not None:
            self.order_port.place_order(intent)

        state.prev_snapshot = snapshot
        state.feature_state = feature_state
