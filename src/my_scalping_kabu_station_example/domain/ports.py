"""Ports (interfaces) used by application/service layers."""

from __future__ import annotations

from typing import Protocol, Tuple

import pandas as pd

from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.features.state import FeatureState
from my_scalping_kabu_station_example.domain.order_book import OrderBookSnapshot


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


class HistoryStore(Protocol):
    """Persists normalized snapshots for backtesting or training."""

    def append(self, snapshot: OrderBookSnapshot) -> None:
        """Append a single snapshot to the underlying store."""
        ...


class SnapshotBuffer(Protocol):
    """In-memory buffer used to retrieve the previous snapshot."""

    def previous(self) -> OrderBookSnapshot | None:
        """Return the most recent snapshot stored in the buffer."""
        ...

    def update(self, snapshot: OrderBookSnapshot) -> OrderBookSnapshot | None:
        """Store the snapshot and return the previously stored one (if any)."""
        ...
