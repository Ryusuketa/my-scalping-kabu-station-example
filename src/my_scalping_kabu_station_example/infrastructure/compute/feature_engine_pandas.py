"""Pandas-based feature engine implementation."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import Dict, Iterable, List, Tuple

from ...application.ports.feature_engine import FeatureEnginePort, FeatureTable, FeatureVector
from ...application.service.state.feature_state import FeatureState
from ...domain.features.expr import (
    Add,
    BestAskPrice,
    BestAskQty,
    BestBidPrice,
    BestBidQty,
    AddSum,
    BinaryExpr,
    Const,
    DepletionSum,
    DepthQtySum,
    Diff,
    Div,
    Expr,
    Mid,
    MicroPrice,
    Mul,
    Sub,
    TimeDecayEma,
)
from ...domain.features.spec import FeatureDef, FeatureSpec
from ...domain.market.orderbook_snapshot import OrderBookSnapshot
from ...domain.market.time import TimeDecay
from ...domain.market.types import PriceKey, Quantity, Side


def _qty_to_float(qty: Quantity | None) -> float:
    return float(qty) if qty is not None else 0.0


def _price_to_float(price: PriceKey | None) -> float:
    return float(price) if price is not None else 0.0


class PandasOrderBookFeatureEngine(FeatureEnginePort):
    def compute_one(
        self,
        spec: FeatureSpec,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState | None,
    ) -> Tuple[FeatureVector, FeatureState]:
        current_state = state or FeatureState()
        features: FeatureVector = {}

        for feature_def in spec.features:
            value, current_state = self._eval_expr(
                feature_def.name,
                feature_def.expr,
                prev_snapshot,
                now_snapshot,
                current_state,
                eps=spec.eps,
            )
            features[feature_def.name] = value

        current_state.last_ts = now_snapshot.ts
        return features, current_state

    def compute_batch(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]) -> FeatureTable:
        state = FeatureState()
        for prev, now in self._pairwise_snapshots(snapshots):
            features, state = self.compute_one(spec, prev, now, state)
            yield features

    def _pairwise_snapshots(
        self, snapshots: Iterable[OrderBookSnapshot]
    ) -> Iterable[Tuple[OrderBookSnapshot | None, OrderBookSnapshot]]:
        prev: OrderBookSnapshot | None = None
        for snap in snapshots:
            yield prev, snap
            prev = snap

    def _eval_expr(
        self,
        feature_name: str,
        expr: Expr,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState,
        eps: float,
    ) -> Tuple[float, FeatureState]:
        if isinstance(expr, Const):
            return float(expr.value), state
        if isinstance(expr, BestBidPrice):
            return _price_to_float(now_snapshot.best_bid_price), state
        if isinstance(expr, BestAskPrice):
            return _price_to_float(now_snapshot.best_ask_price), state
        if isinstance(expr, BestBidQty):
            return _qty_to_float(now_snapshot.best_bid_qty), state
        if isinstance(expr, BestAskQty):
            return _qty_to_float(now_snapshot.best_ask_qty), state
        if isinstance(expr, Mid):
            return _price_to_float(now_snapshot.mid), state
        if isinstance(expr, BinaryExpr):
            left, state = self._eval_expr(feature_name, expr.left, prev_snapshot, now_snapshot, state, eps)
            right, state = self._eval_expr(feature_name, expr.right, prev_snapshot, now_snapshot, state, eps)
            if expr.op in {"+", "add"}:
                return left + right, state
            if expr.op in {"-", "sub", "diff"}:
                return left - right, state
            if expr.op in {"*", "mul"}:
                return left * right, state
            if expr.op in {"/", "div"}:
                denominator = right if right != 0 else eps
                return left / denominator, state
            raise ValueError(f"Unsupported binary op: {expr.op}")
        if isinstance(expr, DepthQtySum):
            levels = now_snapshot.depth_levels(expr.side)[: expr.depth]
            total_qty = sum(_qty_to_float(level.qty) for level in levels)
            return total_qty, state
        if isinstance(expr, MicroPrice):
            bid_p = _price_to_float(now_snapshot.best_bid_price)
            ask_p = _price_to_float(now_snapshot.best_ask_price)
            bid_q = _qty_to_float(now_snapshot.best_bid_qty)
            ask_q = _qty_to_float(now_snapshot.best_ask_qty)
            denom = bid_q + ask_q + expr.eps
            micro = (ask_p * bid_q + bid_p * ask_q) / denom
            return micro, state
        if isinstance(expr, DepletionSum):
            return self._calc_delta_sum(prev_snapshot, now_snapshot, expr.side, mode="depletion"), state
        if isinstance(expr, AddSum):
            return self._calc_delta_sum(prev_snapshot, now_snapshot, expr.side, mode="add"), state
        if isinstance(expr, TimeDecayEma):
            source_value, state = self._eval_expr(feature_name, expr.source, prev_snapshot, now_snapshot, state, eps)
            last_ts = state.last_ts or now_snapshot.ts
            decay = TimeDecay(expr.tau_seconds)
            delta_t = (now_snapshot.ts - last_ts).total_seconds()
            alpha = decay.alpha(delta_t)
            prev_ema = state.ema_values.get(feature_name, source_value)
            ema = prev_ema + alpha * (source_value - prev_ema)
            new_state = replace(state, ema_values={**state.ema_values, feature_name: ema})
            return ema, new_state
        raise ValueError(f"Unsupported expression type: {expr}")

    def _calc_delta_sum(
        self,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        side: Side,
        mode: str,
    ) -> float:
        if prev_snapshot is None:
            return 0.0

        prev_map = prev_snapshot.bid_map if side is Side.BID else prev_snapshot.ask_map
        now_map = now_snapshot.bid_map if side is Side.BID else now_snapshot.ask_map

        keys = set(prev_map.keys()) | set(now_map.keys())
        total = 0.0

        for key in keys:
            prev_qty = _qty_to_float(prev_map.get(key))
            now_qty = _qty_to_float(now_map.get(key))
            diff = prev_qty - now_qty if mode == "depletion" else now_qty - prev_qty
            total += max(0.0, diff)
        return total
