"""Infrastructure implementation skeleton for the order book feature engine."""

from __future__ import annotations

import pandas as pd
from math import exp
from typing import Dict, Iterable

from my_scalping_kabu_station_example.domain.features.expr import (
    AddSum,
    BestAskPrice,
    BestAskQty,
    BestBidPrice,
    BestBidQty,
    DepletionSum,
    DepthQtySum,
    Diff,
    FeatureExpr,
    Imbalance,
    MicroPrice,
    Mid,
    TimeDecayEma,
)
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.features.state import FeatureState
from my_scalping_kabu_station_example.domain.order_book import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.ports import FeatureEnginePort
from my_scalping_kabu_station_example.domain.types import (
    PriceQtyMap,
    Side,
    to_price_key,
)
from my_scalping_kabu_station_example.domain.order_book import Level


class PandasOrderBookFeatureEngine(FeatureEnginePort):
    """Placeholder implementation using pandas."""

    def compute_one(
        self,
        spec: FeatureSpec,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState,
    ) -> tuple[dict[str, float], FeatureState]:
        ema_store: Dict[str, float] = dict(state.ema_values)
        results: Dict[str, float] = {}
        memo: Dict[FeatureExpr, float] = {}
        prev_ts = state.last_ts

        def eval_expr(expr: FeatureExpr, feature_name: str | None = None) -> float:
            if expr in memo:
                return memo[expr]

            value: float
            if isinstance(expr, BestBidPrice):
                value = (
                    float(now_snapshot.best_bid_price)
                    if now_snapshot.best_bid_price is not None
                    else float("nan")
                )
            elif isinstance(expr, BestAskPrice):
                value = (
                    float(now_snapshot.best_ask_price)
                    if now_snapshot.best_ask_price is not None
                    else float("nan")
                )
            elif isinstance(expr, BestBidQty):
                value = (
                    now_snapshot.best_bid_qty
                    if now_snapshot.best_bid_qty is not None
                    else float("nan")
                )
            elif isinstance(expr, BestAskQty):
                value = (
                    now_snapshot.best_ask_qty
                    if now_snapshot.best_ask_qty is not None
                    else float("nan")
                )
            elif isinstance(expr, Mid):
                value = (
                    float(now_snapshot.mid)
                    if now_snapshot.mid is not None
                    else float("nan")
                )
            elif isinstance(expr, DepthQtySum):
                levels = (
                    now_snapshot.bid_levels
                    if expr.side == Side.BID
                    else now_snapshot.ask_levels
                )
                value = float(sum(level.quantity for level in levels[: expr.depth]))
            elif isinstance(expr, DepletionSum):
                value = self._quantity_diff_sum(
                    prev_snapshot, now_snapshot, expr.side, mode="depletion"
                )
            elif isinstance(expr, AddSum):
                value = self._quantity_diff_sum(
                    prev_snapshot, now_snapshot, expr.side, mode="add"
                )
            elif isinstance(expr, Imbalance):
                numerator = eval_expr(expr.numerator)
                denominator = eval_expr(expr.denominator)
                value = (numerator - denominator) / (numerator + denominator + expr.eps)
            elif isinstance(expr, MicroPrice):
                best_ask_price = (
                    float(now_snapshot.best_ask_price)
                    if now_snapshot.best_ask_price is not None
                    else float("nan")
                )
                best_bid_price = (
                    float(now_snapshot.best_bid_price)
                    if now_snapshot.best_bid_price is not None
                    else float("nan")
                )
                best_bid_qty = (
                    now_snapshot.best_bid_qty
                    if now_snapshot.best_bid_qty is not None
                    else float("nan")
                )
                best_ask_qty = (
                    now_snapshot.best_ask_qty
                    if now_snapshot.best_ask_qty is not None
                    else float("nan")
                )
                value = (
                    best_ask_price * best_bid_qty + best_bid_price * best_ask_qty
                ) / (best_bid_qty + best_ask_qty + expr.eps)
            elif isinstance(expr, Diff):
                value = eval_expr(expr.left) - eval_expr(expr.right)
            elif isinstance(expr, TimeDecayEma):
                target_value = eval_expr(expr.target)
                key = (
                    feature_name
                    or expr.name
                    or getattr(expr.target, "name", None)
                    or "ema"
                )
                prev_ema = ema_store.get(key, target_value)
                if prev_ts is None:
                    ema_value = target_value
                else:
                    delta = (now_snapshot.ts - prev_ts).total_seconds()
                    alpha = (
                        1 - exp(-delta / expr.tau_seconds)
                        if expr.tau_seconds > 0
                        else 1.0
                    )
                    ema_value = prev_ema + alpha * (target_value - prev_ema)
                ema_store[key] = ema_value
                value = ema_value
            else:
                raise TypeError(f"Unsupported feature expression: {expr}")

            memo[expr] = value
            return value

        for feature in spec.features:
            results[feature.name] = eval_expr(feature.expr, feature_name=feature.name)

        new_state = FeatureState(last_ts=now_snapshot.ts, ema_values=ema_store)
        return results, new_state

    def compute_batch(
        self, spec: FeatureSpec, snapshots_df: pd.DataFrame
    ) -> pd.DataFrame:
        features: list[Dict[str, float]] = []
        state = FeatureState()
        prev_snapshot: OrderBookSnapshot | None = None

        for _, row in snapshots_df.iterrows():
            snapshot = self._snapshot_from_row(row)
            feature_row, state = self.compute_one(spec, prev_snapshot, snapshot, state)
            features.append(feature_row)
            prev_snapshot = snapshot

        return pd.DataFrame(features)

    @staticmethod
    def _quantity_diff_sum(
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        side: Side,
        mode: str,
    ) -> float:
        prev_map: PriceQtyMap = (
            (prev_snapshot.bid_map if side == Side.BID else prev_snapshot.ask_map)
            if prev_snapshot is not None
            else {}
        )
        now_map: PriceQtyMap = (
            now_snapshot.bid_map if side == Side.BID else now_snapshot.ask_map
        )
        keys = set(prev_map.keys()) | set(now_map.keys())

        total = 0.0
        for price in keys:
            prev_qty = prev_map.get(price, 0.0)
            now_qty = now_map.get(price, 0.0)
            if mode == "depletion":
                diff = prev_qty - now_qty
            elif mode == "add":
                diff = now_qty - prev_qty
            else:
                raise ValueError(f"Unsupported mode: {mode}")
            if diff > 0:
                total += diff
        return float(total)

    @staticmethod
    def _snapshot_from_row(row: pd.Series) -> OrderBookSnapshot:
        bid_levels = PandasOrderBookFeatureEngine._levels_from_row(row, prefix="bid")
        ask_levels = PandasOrderBookFeatureEngine._levels_from_row(row, prefix="ask")
        ts = pd.to_datetime(row["ts"]).to_pydatetime()
        symbol = row["symbol"]
        return OrderBookSnapshot.from_levels(
            ts=ts, symbol=symbol, bid_levels=bid_levels, ask_levels=ask_levels
        )

    @staticmethod
    def _levels_from_row(row: pd.Series, prefix: str) -> Iterable[Level]:
        levels = []
        for i in range(1, 11):
            price = row.get(f"{prefix}_p{i}")
            qty = row.get(f"{prefix}_q{i}")
            if price is None or pd.isna(price) or qty is None or pd.isna(qty):
                continue
            levels.append(Level(price=to_price_key(price), quantity=float(qty)))
        return levels
