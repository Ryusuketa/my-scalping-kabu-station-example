"""Use case for market data arrival."""

from __future__ import annotations

from ..service.pipelines.inference_pipeline import InferencePipeline
from ..service.state.stream_state import StreamState


class OnMarketDataUseCase:
    def __init__(self, pipeline: InferencePipeline) -> None:
        self.pipeline = pipeline

    def handle(self, state: StreamState) -> None:
        self.pipeline.run_once(state)
