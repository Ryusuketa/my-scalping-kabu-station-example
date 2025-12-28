"""Feature expression nodes (declarative AST)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..types import Side


class FeatureExpr:
    """Base class for feature expressions."""

    def describe(self) -> str:
        """Human-readable description."""
        return repr(self)


@dataclass(frozen=True)
class BestBidPrice(FeatureExpr):
    pass


@dataclass(frozen=True)
class BestAskPrice(FeatureExpr):
    pass


@dataclass(frozen=True)
class BestBidQty(FeatureExpr):
    pass


@dataclass(frozen=True)
class BestAskQty(FeatureExpr):
    pass


@dataclass(frozen=True)
class Mid(FeatureExpr):
    pass


@dataclass(frozen=True)
class DepthQtySum(FeatureExpr):
    side: Side
    depth: int


@dataclass(frozen=True)
class DepletionSum(FeatureExpr):
    side: Side


@dataclass(frozen=True)
class AddSum(FeatureExpr):
    side: Side


@dataclass(frozen=True)
class Imbalance(FeatureExpr):
    numerator: FeatureExpr
    denominator: FeatureExpr
    eps: float
    name: Optional[str] = None


@dataclass(frozen=True)
class MicroPrice(FeatureExpr):
    eps: float


@dataclass(frozen=True)
class Diff(FeatureExpr):
    left: FeatureExpr
    right: FeatureExpr


@dataclass(frozen=True)
class TimeDecayEma(FeatureExpr):
    target: FeatureExpr
    tau_seconds: float
    name: Optional[str] = None
