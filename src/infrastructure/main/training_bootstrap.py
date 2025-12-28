"""Training bootstrap from CSV history."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Iterable

from application.service.pipelines.training_pipeline import (
    TrainingPipeline,
)
from domain.market.orderbook_snapshot import (
    OrderBookSnapshot,
)
from infrastructure.compute.feature_engine_pandas import (
    PandasOrderBookFeatureEngine,
)
from infrastructure.config.settings import (
    load_settings,
)
from infrastructure.ml.xgb_trainer import XgbTrainer
from infrastructure.persistence.csv_history_store import (
    CsvHistoryStore,
)
from infrastructure.persistence.model_store_fs import (
    ModelStoreFs,
)


def train_models_from_history(asof: datetime | None = None) -> None:
    settings = load_settings()
    history_store = CsvHistoryStore(path=settings.history_path)
    training_day = _select_training_day(
        history_store, asof or datetime.now(timezone.utc)
    )
    if training_day is None:
        return

    snapshots = list(_read_day(history_store, training_day))
    if not snapshots:
        return

    feature_engine = PandasOrderBookFeatureEngine()
    trainer = XgbTrainer()

    snapshots_by_symbol: dict[str, list[OrderBookSnapshot]] = {}
    for snap in snapshots:
        symbol = str(snap.symbol)
        snapshots_by_symbol.setdefault(symbol, []).append(snap)

    for symbol, symbol_snaps in snapshots_by_symbol.items():
        model_store = ModelStoreFs(base_dir=Path("models") / symbol)
        pipeline = TrainingPipeline(
            history_store=history_store,
            feature_engine=feature_engine,
            trainer=trainer,
            model_store=model_store,
        )
        pipeline.run(settings.feature_spec, symbol_snaps)


def _select_training_day(history_store: CsvHistoryStore, asof: datetime) -> date | None:
    available = history_store.available_dates()
    if not available:
        return None

    asof_utc = (
        asof.astimezone(timezone.utc)
        if asof.tzinfo
        else asof.replace(tzinfo=timezone.utc)
    )
    prev_day = asof_utc.date() - timedelta(days=1)
    if prev_day in available:
        return prev_day
    return max(available)


def _read_day(history_store: CsvHistoryStore, day: date) -> Iterable[OrderBookSnapshot]:
    start = datetime.combine(day, time(0, 0, 0), tzinfo=timezone.utc)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    return history_store.read_range(start, end)
