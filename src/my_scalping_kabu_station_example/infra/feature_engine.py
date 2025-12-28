"""Infrastructure implementation skeleton for the order book feature engine."""

from __future__ import annotations

import pandas as pd

from ..domain.features.spec import FeatureSpec
from ..domain.features.state import FeatureState
from ..domain.order_book import OrderBookSnapshot
from ..domain.ports import FeatureEnginePort


class PandasOrderBookFeatureEngine(FeatureEnginePort):
    """Placeholder implementation using pandas."""

    def compute_one(
        self,
        spec: FeatureSpec,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState,
    ) -> tuple[dict[str, float], FeatureState]:
        raise NotImplementedError

    def compute_batch(self, spec: FeatureSpec, snapshots_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

