"""Configuration loading utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec


@dataclass(frozen=True)
class Settings:
    feature_spec: FeatureSpec
    risk_params: RiskParams
    history_path: Path


def load_settings(data: Mapping[str, Any] | None = None) -> Settings:
    """Load settings from a mapping (defaults to sensible values)."""

    config = data or {}
    feature_cfg = config.get("feature_spec")
    if isinstance(feature_cfg, FeatureSpec):
        feature_spec = feature_cfg
    else:
        feature_cfg = feature_cfg or {}
        feature_spec = FeatureSpec(
            version=str(feature_cfg.get("version", "ob10_v1")),
            eps=float(feature_cfg.get("eps", 1e-9)),
            params=dict(feature_cfg.get("params", {})),
            features=list(feature_cfg.get("features", [])),
        )

    risk_cfg = config.get("risk_params")
    if isinstance(risk_cfg, RiskParams):
        risk_params = risk_cfg
    else:
        risk_cfg = risk_cfg or {}
        risk_params = RiskParams(
            max_position=float(risk_cfg.get("max_position", 1.0)),
            stop_loss=float(risk_cfg.get("stop_loss", 1.0)),
            take_profit=float(risk_cfg.get("take_profit", 1.0)),
            cooldown_seconds=float(risk_cfg.get("cooldown_seconds", 0.0)),
        )

    history_path = Path(config.get("history_path", "data/history.csv"))
    return Settings(feature_spec=feature_spec, risk_params=risk_params, history_path=history_path)
