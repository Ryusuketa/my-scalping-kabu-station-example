"""Decision policy rules (domain)."""

from __future__ import annotations

from uuid import uuid4

from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import DecisionContext, InferenceResult, TradeIntent
from my_scalping_kabu_station_example.domain.decision.signal import OrderSide


class DecisionPolicy:
    """Encapsulates decision making rules."""

    def __init__(self, score_threshold: float = 0.0, lot_size: float = 1.0) -> None:
        self.score_threshold = score_threshold
        self.lot_size = lot_size

    def decide(self, inference: InferenceResult, context: DecisionContext, risk: RiskParams) -> TradeIntent | None:
        """Simple threshold-based decision rule with position caps.

        * score > threshold -> buy up to max_position
        * score < -threshold -> sell up to -max_position
        * otherwise: no trade
        """

        score = inference.score
        if score > self.score_threshold:
            qty = self._buy_quantity(context.position_size, risk.max_position)
            if qty <= 0:
                return None
            return TradeIntent(
                intent_id=self._intent_id(),
                side=OrderSide.BUY,
                quantity=qty,
                symbol=context.symbol,
                price=context.price,
            )

        if score < -self.score_threshold:
            qty = self._sell_quantity(context.position_size, risk.max_position)
            if qty <= 0:
                return None
            return TradeIntent(
                intent_id=self._intent_id(),
                side=OrderSide.SELL,
                quantity=qty,
                symbol=context.symbol,
                price=context.price,
            )

        return None

    def _buy_quantity(self, position_size: float, max_position: float) -> float:
        available = max_position - position_size
        if available <= 0:
            return 0.0
        return min(self.lot_size, available)

    def _sell_quantity(self, position_size: float, max_position: float) -> float:
        available = max_position + position_size
        if available <= 0:
            return 0.0
        return min(self.lot_size, available)

    @staticmethod
    def _intent_id() -> str:
        return str(uuid4())
