"""Dependency wiring placeholder."""

from __future__ import annotations

from pathlib import Path

from my_scalping_kabu_station_example.infrastructure.compute.feature_engine_pandas import PandasOrderBookFeatureEngine
from my_scalping_kabu_station_example.infrastructure.config.settings import load_settings
from my_scalping_kabu_station_example.infrastructure.persistence.csv_history_store import CsvHistoryStore
from my_scalping_kabu_station_example.infrastructure.persistence.model_store_fs import ModelStoreFs


def build_container() -> dict:
    settings = load_settings()
    history_store = CsvHistoryStore(path=settings.history_path)
    feature_engine = PandasOrderBookFeatureEngine()
    model_store = ModelStoreFs(base_dir=Path("models"))
    return {
        "settings": settings,
        "history_store": history_store,
        "feature_engine": feature_engine,
        "model_store": model_store,
    }
