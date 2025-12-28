"""Feature expression AST definitions (domain-level)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from my_scalping_kabu_station_example.domain.market.types import Side


class Expr(Protocol):
    """Marker protocol for feature expressions."""

    def describe(self) -> str:
        """Human-readable description."""


@dataclass(frozen=True)
class Const(Expr):
    value: float

    def describe(self) -> str:
        return f"Const({self.value})"


@dataclass(frozen=True)
class Col(Expr):
    name: str

    def describe(self) -> str:
        return f"Col({self.name})"


@dataclass(frozen=True)
class BinaryExpr(Expr):
    left: Expr
    right: Expr
    op: str

    def describe(self) -> str:
        return f"({self.left.describe()} {self.op} {self.right.describe()})"


def Add(left: Expr, right: Expr) -> BinaryExpr:
    return BinaryExpr(left, right, "+")


def Sub(left: Expr, right: Expr) -> BinaryExpr:
    return BinaryExpr(left, right, "-")


def Mul(left: Expr, right: Expr) -> BinaryExpr:
    return BinaryExpr(left, right, "*")


def Div(left: Expr, right: Expr) -> BinaryExpr:
    return BinaryExpr(left, right, "/")


def Diff(left: Expr, right: Expr) -> BinaryExpr:
    return BinaryExpr(left, right, "diff")


@dataclass(frozen=True)
class DepthQtySum(Expr):
    side: Side
    depth: int

    def describe(self) -> str:
        return f"DepthQtySum({self.side.value}, depth={self.depth})"


@dataclass(frozen=True)
class MicroPrice(Expr):
    eps: float

    def describe(self) -> str:
        return f"MicroPrice(eps={self.eps})"


@dataclass(frozen=True)
class BestBidPrice(Expr):
    def describe(self) -> str:
        return "BestBidPrice()"


@dataclass(frozen=True)
class BestAskPrice(Expr):
    def describe(self) -> str:
        return "BestAskPrice()"


@dataclass(frozen=True)
class BestBidQty(Expr):
    def describe(self) -> str:
        return "BestBidQty()"


@dataclass(frozen=True)
class BestAskQty(Expr):
    def describe(self) -> str:
        return "BestAskQty()"


@dataclass(frozen=True)
class Mid(Expr):
    def describe(self) -> str:
        return "Mid()"


@dataclass(frozen=True)
class DepletionSum(Expr):
    side: Side

    def describe(self) -> str:
        return f"DepletionSum({self.side.value})"


@dataclass(frozen=True)
class AddSum(Expr):
    side: Side

    def describe(self) -> str:
        return f"AddSum({self.side.value})"


@dataclass(frozen=True)
class TimeDecayEma(Expr):
    source: Expr
    tau_seconds: float

    def describe(self) -> str:
        return f"TimeDecayEma(tau={self.tau_seconds}, source={self.source.describe()})"
