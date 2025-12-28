"""Polars-based feature engine implementation placeholder."""

from __future__ import annotations

from typing import Iterable, Tuple

from application.ports.feature_engine import (
    FeatureEnginePort,
    FeatureTable,
    FeatureVector,
)
from application.service.state.feature_state import (
    FeatureState,
)
from domain.features.spec import FeatureSpec
from domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)
from infrastructure.compute.feature_engine_pandas import (
    PandasOrderBookFeatureEngine,
)


class PolarsOrderBookFeatureEngine(FeatureEnginePort):
    """Thin wrapper that reuses the pandas implementation for now."""

    def __init__(self) -> None:
        self._fallback = PandasOrderBookFeatureEngine()

    def compute_one(
        self,
        spec: FeatureSpec,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState | None,
    ) -> Tuple[FeatureVector, FeatureState]:
        return self._fallback.compute_one(spec, prev_snapshot, now_snapshot, state)

    def compute_batch(
        self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]
    ) -> FeatureTable:
        return self._fallback.compute_batch(spec, snapshots)
