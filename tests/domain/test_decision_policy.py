from my_scalping_kabu_station_example.domain.decision.policy import DecisionPolicy
from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import (
    DecisionContext,
    InferenceResult,
    OrderSide,
)
from my_scalping_kabu_station_example.domain.market.types import Symbol


def test_decision_policy_triggers_buy_within_limits() -> None:
    policy = DecisionPolicy(score_threshold=0.1, lot_size=1.0)
    risk = RiskParams(max_position=2.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(
        position_size=0.5,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=0.0,
        pip_size=1.0,
    )
    inference = InferenceResult(features={}, score=0.5)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.side is OrderSide.BUY
    assert intent.quantity == 1.0
    assert intent.cash_margin == 2


def test_decision_policy_respects_position_cap() -> None:
    policy = DecisionPolicy(score_threshold=0.1, lot_size=1.0)
    risk = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(
        position_size=1.0,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=0.0,
        pip_size=1.0,
    )
    inference = InferenceResult(features={}, score=0.9)

    intent = policy.decide(inference, context, risk)

    assert intent is None


def test_decision_policy_handles_sell_and_fractional_quantity() -> None:
    policy = DecisionPolicy(score_threshold=0.1, lot_size=1.0)
    risk = RiskParams(max_position=2.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(
        position_size=-1.5,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=0.0,
        pip_size=1.0,
    )
    inference = InferenceResult(features={}, score=-0.6)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.side is OrderSide.SELL
    assert intent.quantity == 0.5
    assert intent.cash_margin == 2


def test_decision_policy_ignores_small_scores() -> None:
    policy = DecisionPolicy(score_threshold=0.2, lot_size=1.0)
    risk = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(
        position_size=0.0,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=0.0,
        pip_size=1.0,
    )
    inference = InferenceResult(features={}, score=0.1)

    intent = policy.decide(inference, context, risk)

    assert intent is None


def test_decision_policy_triggers_loss_cut_for_buy() -> None:
    policy = DecisionPolicy(score_threshold=0.9, lot_size=1.0)
    risk = RiskParams(
        max_position=1.0, stop_loss=1.0, take_profit=1.0, loss_cut_pips=1.0
    )
    context = DecisionContext(
        position_size=0.0,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=99.0,
        pip_size=1.0,
        has_open_order=True,
        open_order_side=OrderSide.BUY,
        open_order_price=100.5,
        open_order_qty=200,
    )
    inference = InferenceResult(features={}, score=0.0)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.cash_margin == 3
    assert intent.side is OrderSide.SELL
    assert intent.quantity == 2.0
    assert intent.price == 0.0


def test_decision_policy_triggers_take_profit_for_buy() -> None:
    policy = DecisionPolicy(score_threshold=0.9, lot_size=1.0)
    risk = RiskParams(
        max_position=1.0, stop_loss=1.0, take_profit=2.0, loss_cut_pips=5.0
    )
    context = DecisionContext(
        position_size=0.0,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=105.0,
        pip_size=1.0,
        has_open_order=True,
        open_order_side=OrderSide.BUY,
        open_order_price=100.0,
        open_order_qty=100,
    )
    inference = InferenceResult(features={}, score=0.0)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.cash_margin == 3
    assert intent.side is OrderSide.SELL
    assert intent.quantity == 1.0
    assert intent.price == 0.0


def test_decision_policy_triggers_loss_cut_for_sell() -> None:
    policy = DecisionPolicy(score_threshold=0.9, lot_size=1.0)
    risk = RiskParams(
        max_position=1.0, stop_loss=1.0, take_profit=2.0, loss_cut_pips=1.0
    )
    context = DecisionContext(
        position_size=0.0,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=102.0,
        pip_size=1.0,
        has_open_order=True,
        open_order_side=OrderSide.SELL,
        open_order_price=100.0,
        open_order_qty=100,
    )
    inference = InferenceResult(features={}, score=0.0)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.cash_margin == 3
    assert intent.side is OrderSide.BUY
    assert intent.quantity == 1.0
    assert intent.price == 0.0


def test_decision_policy_triggers_take_profit_for_sell() -> None:
    policy = DecisionPolicy(score_threshold=0.9, lot_size=1.0)
    risk = RiskParams(
        max_position=1.0, stop_loss=1.0, take_profit=1.0, loss_cut_pips=5.0
    )
    context = DecisionContext(
        position_size=0.0,
        risk_budget=risk.max_position,
        symbol=Symbol("TEST"),
        price=95.0,
        pip_size=1.0,
        has_open_order=True,
        open_order_side=OrderSide.SELL,
        open_order_price=100.0,
        open_order_qty=200,
    )
    inference = InferenceResult(features={}, score=0.0)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.cash_margin == 3
    assert intent.side is OrderSide.BUY
    assert intent.quantity == 2.0
    assert intent.price == 0.0
