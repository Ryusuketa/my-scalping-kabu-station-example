"""Ports (interfaces) used by application/service layers."""

from __future__ import annotations

from typing import Protocol, Tuple

import pandas as pd

from .features.spec import FeatureSpec
from .features.state import FeatureState
from .order_book import OrderBookSnapshot


class FeatureEnginePort(Protocol):
    """Feature engine capable of streaming and batch calculations."""

    def compute_one(
        self,
        spec: FeatureSpec,
        prev_snapshot: OrderBookSnapshot | None,
        now_snapshot: OrderBookSnapshot,
        state: FeatureState,
    ) -> tuple[dict[str, float], FeatureState]:
        """Compute feature vector for a single event."""
        ...

    def compute_batch(self, spec: FeatureSpec, snapshots_df: pd.DataFrame) -> pd.DataFrame:
        """Compute features for an entire dataframe of snapshots."""
        ...

