"""Dataset builder utilities."""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable, List

from application.ports.feature_engine import (
    FeatureEnginePort,
)
from application.ports.history import HistoryStorePort
from domain.features.spec import FeatureSpec
from domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)


class DatasetBuilder:
    def __init__(
        self, history_store: HistoryStorePort, feature_engine: FeatureEnginePort
    ) -> None:
        self.history_store = history_store
        self.feature_engine = feature_engine

    def build(self, spec: FeatureSpec, snapshots: Iterable[OrderBookSnapshot]):
        """Compute feature vectors for the provided snapshots."""

        return list(self.feature_engine.compute_batch(spec, snapshots))

    def build_with_labels(
        self,
        spec: FeatureSpec,
        snapshots: Iterable[OrderBookSnapshot],
        horizon_seconds: float = 10.0,
    ) -> List[dict[str, float]]:
        """Compute feature vectors with binary labels based on future mid moves."""

        snapshot_list = sorted(list(snapshots), key=lambda snap: snap.ts)
        features = list(self.feature_engine.compute_batch(spec, snapshot_list))
        labels = _labels_from_future(snapshot_list, horizon_seconds)
        labeled_rows: List[dict[str, float]] = []
        for row, label in zip(features, labels):
            if label is None:
                continue
            enriched = dict(row)
            enriched["label"] = float(label)
            labeled_rows.append(enriched)
        return labeled_rows


def _labels_from_future(
    snapshots: List[OrderBookSnapshot],
    horizon_seconds: float,
) -> List[int | None]:
    if horizon_seconds <= 0:
        raise ValueError("horizon_seconds must be positive")

    labels: List[int | None] = [None] * len(snapshots)
    j = 0
    for i, snap in enumerate(snapshots):
        target_time = snap.ts + timedelta(seconds=horizon_seconds)
        if j < i + 1:
            j = i + 1
        while j < len(snapshots) and snapshots[j].ts < target_time:
            j += 1
        if j >= len(snapshots):
            labels[i] = None
            continue
        now_mid = snap.mid
        future_mid = snapshots[j].mid
        if now_mid is None or future_mid is None:
            labels[i] = None
            continue
        labels[i] = 1 if float(future_mid) > float(now_mid) else 0
    return labels
