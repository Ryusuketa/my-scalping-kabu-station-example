from dataclasses import dataclass

from my_scalping_kabu_station_example.infrastructure.persistence.model_store_fs import ModelStoreFs


@dataclass
class DummyPredictor:
    value: int


def test_model_store_fs_saves_and_loads(tmp_path) -> None:
    store = ModelStoreFs(base_dir=tmp_path)
    predictor = DummyPredictor(value=42)

    store.save_candidate(predictor)
    store.swap_active(predictor)

    loaded = store.load_active()

    assert loaded == predictor
