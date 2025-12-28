"""Dependency wiring placeholder."""

from __future__ import annotations

from pathlib import Path

from infrastructure.compute.feature_engine_pandas import (
    PandasOrderBookFeatureEngine,
)
from infrastructure.config.settings import (
    load_settings,
)
from infrastructure.persistence.csv_history_store import (
    CsvHistoryStore,
)
from infrastructure.persistence.model_store_fs import (
    ModelStoreFs,
)
from infrastructure.websocket.client import (
    WebSocketClient,
)
from infrastructure.websocket.market_data import (
    WebSocketMarketDataSource,
)


def build_container() -> dict:
    settings = load_settings()
    history_store = CsvHistoryStore(path=settings.history_path)
    feature_engine = PandasOrderBookFeatureEngine()
    model_store = ModelStoreFs(base_dir=Path("models"))
    market_data = None
    if settings.ws_url:
        ws_client = WebSocketClient(url=settings.ws_url, api_key=settings.api_key)
        market_data = WebSocketMarketDataSource(client=ws_client)
    return {
        "settings": settings,
        "history_store": history_store,
        "feature_engine": feature_engine,
        "model_store": model_store,
        "market_data": market_data,
    }
