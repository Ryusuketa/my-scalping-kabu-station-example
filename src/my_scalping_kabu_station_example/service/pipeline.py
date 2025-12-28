"""Pipeline orchestration for streaming inference."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from ..domain.features.spec import FeatureSpec
from ..domain.features.state import FeatureState
from ..domain.order_book import OrderBookSnapshot
from ..domain.ports import FeatureEnginePort


class ModelPredictor(Protocol):
    """Prediction interface for trained models."""

    def predict(self, features: Dict[str, float]) -> Any:
        ...


class DecisionPolicy(Protocol):
    """Decision policy producing trade intents."""

    def decide(self, inference_result: Any, position_state: Any, risk_params: Any) -> Any:
        ...


class OrderPort(Protocol):
    """Order submission interface."""

    def place_order(self, trade_intent: Any) -> Any:
        ...


@dataclass
class FeatureNode:
    """Computes feature vectors using the configured feature engine."""

    feature_engine: FeatureEnginePort
    feature_spec: FeatureSpec

    def compute(
        self,
        prev_snapshot: Optional[OrderBookSnapshot],
        now_snapshot: OrderBookSnapshot,
        state: FeatureState,
    ) -> tuple[Dict[str, float], FeatureState]:
        return self.feature_engine.compute_one(
            spec=self.feature_spec,
            prev_snapshot=prev_snapshot,
            now_snapshot=now_snapshot,
            state=state,
        )


@dataclass
class InferNode:
    """Runs model prediction from feature vectors."""

    model_predictor: ModelPredictor

    def predict(self, features: Dict[str, float]) -> Any:
        return self.model_predictor.predict(features)


@dataclass
class DecideNode:
    """Applies risk policy to inference output."""

    decision_policy: DecisionPolicy
    position_state: Any
    risk_params: Any

    def decide(self, inference_result: Any) -> Any:
        return self.decision_policy.decide(
            inference_result=inference_result,
            position_state=self.position_state,
            risk_params=self.risk_params,
        )


@dataclass
class OrderNode:
    """Submits orders via the order port."""

    order_port: OrderPort

    def place(self, trade_intent: Any) -> Any:
        return self.order_port.place_order(trade_intent)
