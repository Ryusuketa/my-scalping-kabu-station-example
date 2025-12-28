"""Feature spec definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping

from .expr import (
    AddSum,
    BestAskPrice,
    BestAskQty,
    BestBidPrice,
    BestBidQty,
    DepletionSum,
    DepthQtySum,
    Diff,
    Imbalance,
    MicroPrice,
    Mid,
    TimeDecayEma,
)
from ..types import Side


@dataclass(frozen=True)
class FeatureDef:
    """Named feature definition."""

    name: str
    expr: object


@dataclass
class FeatureSpec:
    """Versioned feature specification."""

    version: str
    eps: float
    params: Mapping[str, object]
    features: List[FeatureDef] = field(default_factory=list)

    @classmethod
    def ob10_v1(
        cls, eps: float = 1e-9, n_list: Iterable[int] | None = None, tau: float = 1.0
    ) -> "FeatureSpec":
        """Build the default ob10_v1 spec. Implementation filled after tests."""
        depths = list(n_list) if n_list is not None else [5, 10]

        features: List[FeatureDef] = []

        for depth in depths:
            features.append(
                FeatureDef(
                    name=f"OBI_{depth}",
                    expr=Imbalance(
                        numerator=DepthQtySum(Side.BID, depth),
                        denominator=DepthQtySum(Side.ASK, depth),
                        eps=eps,
                        name=f"OBI_{depth}",
                    ),
                )
            )

        micro = FeatureDef(name="micro_price", expr=MicroPrice(eps=eps))
        features.append(micro)
        features.append(
            FeatureDef(
                name="micro_price_shift",
                expr=Diff(left=micro.expr, right=Mid()),
            )
        )

        depletion_bid = DepletionSum(Side.BID)
        depletion_ask = DepletionSum(Side.ASK)
        add_bid = AddSum(Side.BID)
        add_ask = AddSum(Side.ASK)

        di_expr = Imbalance(
            numerator=depletion_ask,
            denominator=depletion_bid,
            eps=eps,
            name="DI",
        )
        ai_expr = Imbalance(
            numerator=add_bid,
            denominator=add_ask,
            eps=eps,
            name="AI",
        )

        features.extend(
            [
                FeatureDef(name="depletion_bid", expr=depletion_bid),
                FeatureDef(name="depletion_ask", expr=depletion_ask),
                FeatureDef(name="add_bid", expr=add_bid),
                FeatureDef(name="add_ask", expr=add_ask),
                FeatureDef(name="depletion_imbalance", expr=di_expr),
                FeatureDef(name="add_imbalance", expr=ai_expr),
                FeatureDef(name="DI_ema", expr=TimeDecayEma(target=di_expr, tau_seconds=tau)),
                FeatureDef(name="AI_ema", expr=TimeDecayEma(target=ai_expr, tau_seconds=tau)),
            ]
        )

        # Only the primary depth gets an EMA by default.
        primary_depth = depths[0]
        features.append(
            FeatureDef(
                name=f"OBI_{primary_depth}_ema",
                expr=TimeDecayEma(
                    target=next(f.expr for f in features if f.name == f"OBI_{primary_depth}"),
                    tau_seconds=tau,
                    name=f"OBI_{primary_depth}",
                ),
            )
        )

        return cls(
            version="ob10_v1",
            eps=eps,
            params={"N_list": depths, "tau": tau},
            features=features,
        )
