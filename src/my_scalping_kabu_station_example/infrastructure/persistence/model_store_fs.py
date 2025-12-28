"""Filesystem-based model store."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

from my_scalping_kabu_station_example.application.ports.model import ModelPredictorPort, ModelStorePort


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
