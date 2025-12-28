from my_scalping_kabu_station_example.domain.decision.policy import DecisionPolicy
from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.decision.signal import DecisionContext, InferenceResult, OrderSide


def test_decision_policy_triggers_buy_within_limits() -> None:
    policy = DecisionPolicy(score_threshold=0.1, lot_size=1.0)
    risk = RiskParams(max_position=2.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(position_size=0.5, risk_budget=risk.max_position)
    inference = InferenceResult(features={}, score=0.5)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.side is OrderSide.BUY
    assert intent.quantity == 1.0


def test_decision_policy_respects_position_cap() -> None:
    policy = DecisionPolicy(score_threshold=0.1, lot_size=1.0)
    risk = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(position_size=1.0, risk_budget=risk.max_position)
    inference = InferenceResult(features={}, score=0.9)

    intent = policy.decide(inference, context, risk)

    assert intent is None


def test_decision_policy_handles_sell_and_fractional_quantity() -> None:
    policy = DecisionPolicy(score_threshold=0.1, lot_size=1.0)
    risk = RiskParams(max_position=2.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(position_size=-1.5, risk_budget=risk.max_position)
    inference = InferenceResult(features={}, score=-0.6)

    intent = policy.decide(inference, context, risk)

    assert intent is not None
    assert intent.side is OrderSide.SELL
    assert intent.quantity == 0.5


def test_decision_policy_ignores_small_scores() -> None:
    policy = DecisionPolicy(score_threshold=0.2, lot_size=1.0)
    risk = RiskParams(max_position=1.0, stop_loss=1.0, take_profit=1.0)
    context = DecisionContext(position_size=0.0, risk_budget=risk.max_position)
    inference = InferenceResult(features={}, score=0.1)

    intent = policy.decide(inference, context, risk)

    assert intent is None
