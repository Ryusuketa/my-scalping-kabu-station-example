"""Decision policy rules (domain)."""

from __future__ import annotations

from uuid import uuid4

from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import (
    DecisionContext,
    InferenceResult,
    TradeIntent,
)
from my_scalping_kabu_station_example.domain.decision.signal import OrderSide


class DecisionPolicy:
    """Encapsulates decision making rules."""

    def __init__(self, score_threshold: float = 0.0, lot_size: float = 1.0) -> None:
        self.score_threshold = score_threshold
        self.lot_size = lot_size

    def decide(
        self, inference: InferenceResult, context: DecisionContext, risk: RiskParams
    ) -> TradeIntent | None:
        """Simple threshold-based decision rule with position caps.

        * score > threshold -> buy up to max_position
        * score < -threshold -> sell up to -max_position
        * otherwise: no trade
        """

        exit_intent = self._exit_intent(context, risk)
        if exit_intent is not None:
            return exit_intent

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
                cash_margin=2,
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
                cash_margin=2,
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

    def _exit_intent(
        self, context: DecisionContext, risk: RiskParams
    ) -> TradeIntent | None:
        if not context.has_open_order:
            return None
        if (
            context.open_order_price is None
            or context.open_order_side is None
            or context.open_order_qty is None
        ):
            return None

        pip_size = context.pip_size if context.pip_size > 0 else 1.0
        if context.open_order_side is OrderSide.BUY:
            loss_pips = (context.open_order_price - context.price) / pip_size
            gain_pips = (context.price - context.open_order_price) / pip_size
            repay_side = OrderSide.SELL
        else:
            loss_pips = (context.price - context.open_order_price) / pip_size
            gain_pips = (context.open_order_price - context.price) / pip_size
            repay_side = OrderSide.BUY

        loss_triggered = risk.loss_cut_pips > 0 and loss_pips >= risk.loss_cut_pips
        gain_triggered = risk.take_profit > 0 and gain_pips >= risk.take_profit
        if not (loss_triggered or gain_triggered):
            return None

        quantity_units = context.open_order_qty / 100.0
        metadata = (
            {"FrontOrderType": 10} if (loss_triggered or gain_triggered) else None
        )
        price = 0.0 if (loss_triggered or gain_triggered) else context.price
        return TradeIntent(
            intent_id=self._intent_id(),
            side=repay_side,
            quantity=quantity_units,
            symbol=context.symbol,
            price=price,
            cash_margin=3,
            metadata=metadata,
        )

    @staticmethod
    def _intent_id() -> str:
        return str(uuid4())
