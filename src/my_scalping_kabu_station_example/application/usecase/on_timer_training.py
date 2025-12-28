"""Use case for scheduled training."""

from __future__ import annotations

from datetime import datetime

from ..service.pipelines.training_pipeline import TrainingPipeline
from ...domain.features.spec import FeatureSpec
from ...domain.market.orderbook_snapshot import OrderBookSnapshot


class OnTimerTrainingUseCase:
    def __init__(self, pipeline: TrainingPipeline, spec: FeatureSpec) -> None:
        self.pipeline = pipeline
        self.spec = spec

    def handle(self, snapshots: list[OrderBookSnapshot], asof: datetime | None = None) -> None:
        _ = asof  # placeholder for scheduling logic
        self.pipeline.run(self.spec, snapshots)
