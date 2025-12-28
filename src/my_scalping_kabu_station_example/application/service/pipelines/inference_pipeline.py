"""Inference pipeline skeleton."""

from __future__ import annotations

from ...ports.buffer import MarketBufferPort
from ...ports.feature_engine import FeatureEnginePort
from ...ports.history import HistoryStorePort
from ...ports.model import ModelStorePort
from ...ports.broker import OrderPort, PositionPort
from ...ports.market_data import MarketDataSourcePort
from ..state.stream_state import StreamState


class InferencePipeline:
    def __init__(
        self,
        market_data: MarketDataSourcePort,
        history_store: HistoryStorePort,
        buffer: MarketBufferPort,
        feature_engine: FeatureEnginePort,
        model_store: ModelStorePort,
        order_port: OrderPort,
        position_port: PositionPort,
    ) -> None:
        self.market_data = market_data
        self.history_store = history_store
        self.buffer = buffer
        self.feature_engine = feature_engine
        self.model_store = model_store
        self.order_port = order_port
        self.position_port = position_port

    def run_once(self, state: StreamState) -> None:
        """One inference iteration (not implemented)."""

        raise NotImplementedError
