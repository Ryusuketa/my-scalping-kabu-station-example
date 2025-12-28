"""Decision policy rules (domain)."""

from __future__ import annotations

from .risk import RiskParams
from .signal import DecisionContext, InferenceResult, TradeIntent


class DecisionPolicy:
    """Encapsulates decision making rules."""

    def decide(self, inference: InferenceResult, context: DecisionContext, risk: RiskParams) -> TradeIntent | None:
        raise NotImplementedError
