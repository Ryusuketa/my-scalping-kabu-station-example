"""Filesystem-based model store."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

from my_scalping_kabu_station_example.application.ports.model import ModelPredictorPort, ModelStorePort
from my_scalping_kabu_station_example.domain.market.types import Symbol


@dataclass
class ModelStoreFs(ModelStorePort):
    base_dir: Path
    active_filename: str = "model_active.pkl"
    candidate_filename: str = "model_candidate.pkl"

    def _active_path(self) -> Path:
        return Path(self.base_dir) / self.active_filename

    def _candidate_path(self) -> Path:
        return Path(self.base_dir) / self.candidate_filename

    def load_active(self) -> ModelPredictorPort:
        path = self._active_path()
        if not path.exists():
            raise FileNotFoundError(f"Active model not found at {path}")
        with path.open("rb") as handle:
            return pickle.load(handle)

    def save_candidate(self, predictor: ModelPredictorPort) -> None:
        path = self._candidate_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            pickle.dump(predictor, handle)

    def swap_active(self, predictor: ModelPredictorPort) -> None:
        path = self._active_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".tmp")
        with tmp_path.open("wb") as handle:
            pickle.dump(predictor, handle)
        tmp_path.replace(path)


@dataclass
class SymbolModelStore:
    base_dir: Path

    def _store_for(self, symbol: Symbol) -> ModelStoreFs:
        return ModelStoreFs(base_dir=Path(self.base_dir) / str(symbol))

    def load_active_for(self, symbol: Symbol) -> ModelPredictorPort:
        return self._store_for(symbol).load_active()

    def save_candidate_for(self, symbol: Symbol, predictor: ModelPredictorPort) -> None:
        self._store_for(symbol).save_candidate(predictor)

    def swap_active_for(self, symbol: Symbol, predictor: ModelPredictorPort) -> None:
        self._store_for(symbol).swap_active(predictor)
