from datetime import datetime, timezone

from my_scalping_kabu_station_example.domain.features.expr import MicroPrice
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.domain.market.level import Level
from my_scalping_kabu_station_example.domain.market.orderbook_snapshot import OrderBookSnapshot
from my_scalping_kabu_station_example.domain.market.time import Timestamp
from my_scalping_kabu_station_example.domain.market.types import Quantity, Symbol, price_key_from
from my_scalping_kabu_station_example.application.service.dataset import DatasetBuilder
from my_scalping_kabu_station_example.infrastructure.compute.feature_engine_pandas import PandasOrderBookFeatureEngine
from my_scalping_kabu_station_example.infrastructure.ml.xgb_trainer import XgbTrainer
from my_scalping_kabu_station_example.infrastructure.persistence.csv_history_store import CsvHistoryStore
from my_scalping_kabu_station_example.infrastructure.persistence.model_store_fs import ModelStoreFs


def _make_snapshot(ts: datetime, bid: str, ask: str) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        ts=Timestamp(ts),
        symbol=Symbol("TEST"),
        bid_levels=[Level(price_key_from(bid), Quantity(1.0))],
        ask_levels=[Level(price_key_from(ask), Quantity(2.0))],
    )


def test_csv_to_feature_training_flow(tmp_path) -> None:
    spec = FeatureSpec.from_features(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef("microprice", MicroPrice(eps=1e-9))],
    )
    history_store = CsvHistoryStore(path=tmp_path / "history.csv")
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts1 = datetime(2024, 1, 1, 0, 0, 11, tzinfo=timezone.utc)
    ts2 = datetime(2024, 1, 1, 0, 0, 22, tzinfo=timezone.utc)
    history_store.append(_make_snapshot(ts0, "100.0", "100.5"))
    history_store.append(_make_snapshot(ts1, "100.2", "100.7"))
    history_store.append(_make_snapshot(ts2, "99.8", "100.3"))

    snapshots = list(history_store.read_range(ts0, ts2))
    feature_engine = PandasOrderBookFeatureEngine()
    builder = DatasetBuilder(history_store=history_store, feature_engine=feature_engine)
    features = builder.build_with_labels(spec, snapshots, horizon_seconds=10.0)

    trainer = XgbTrainer(params={"n_estimators": 5, "max_depth": 2})
    predictor = trainer.train(spec, features)
    model_store = ModelStoreFs(base_dir=tmp_path / "models")
    model_store.save_candidate(predictor)
    model_store.swap_active(predictor)

    loaded = model_store.load_active()
    assert loaded.model is not None
