"""Configuration loading utilities."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any, Mapping

from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec


@dataclass(frozen=True)
class Settings:
    feature_spec: FeatureSpec
    risk_params: RiskParams
    history_path: Path
    ws_url: str | None = None
    ws_api_key: str | None = None


def load_settings(data: Mapping[str, Any] | None = None) -> Settings:
    """Load settings from a mapping (defaults to sensible values)."""

    config = data or {}
    feature_cfg = config.get("feature_spec")
    if isinstance(feature_cfg, FeatureSpec):
        feature_spec = feature_cfg
    else:
        feature_cfg = feature_cfg or {}
        env_feature_spec = os.environ.get("FEATURE_SPEC_JSON")
        if env_feature_spec:
            try:
                feature_cfg = json.loads(env_feature_spec)
            except json.JSONDecodeError:
                feature_cfg = {}
        env_params = os.environ.get("FEATURE_SPEC_PARAMS_JSON")
        if env_params:
            try:
                env_params_obj = json.loads(env_params)
            except json.JSONDecodeError:
                env_params_obj = {}
        else:
            env_params_obj = {}
        feature_spec = FeatureSpec(
            version=str(
                feature_cfg.get("version") or os.environ.get("FEATURE_SPEC_VERSION", "ob10_v1")
            ),
            eps=float(
                feature_cfg.get("eps") if feature_cfg.get("eps") is not None else os.environ.get("FEATURE_SPEC_EPS", 1e-9)
            ),
            params=dict(feature_cfg.get("params") or env_params_obj),
            features=list(feature_cfg.get("features", [])),
        )

    risk_cfg = config.get("risk_params")
    if isinstance(risk_cfg, RiskParams):
        risk_params = risk_cfg
    else:
        risk_cfg = risk_cfg or {}
        risk_params = RiskParams(
            max_position=float(
                risk_cfg.get("max_position") if risk_cfg.get("max_position") is not None else os.environ.get("RISK_MAX_POSITION", 1.0)
            ),
            stop_loss=float(
                risk_cfg.get("stop_loss") if risk_cfg.get("stop_loss") is not None else os.environ.get("RISK_STOP_LOSS", 1.0)
            ),
            take_profit=float(
                risk_cfg.get("take_profit") if risk_cfg.get("take_profit") is not None else os.environ.get("RISK_TAKE_PROFIT", 1.0)
            ),
            cooldown_seconds=float(
                risk_cfg.get("cooldown_seconds") if risk_cfg.get("cooldown_seconds") is not None else os.environ.get("RISK_COOLDOWN_SECONDS", 0.0)
            ),
            loss_cut_pips=float(
                risk_cfg.get("loss_cut_pips") if risk_cfg.get("loss_cut_pips") is not None else os.environ.get("RISK_LOSS_CUT_PIPS", 0.0)
            ),
        )

    history_path_value = config.get("history_path") or os.environ.get("HISTORY_PATH") or "data/history"
    history_path = Path(history_path_value)
    ws_url = config.get("ws_url") or os.environ.get("WS_URL") or "ws://localhost:18081"
    ws_api_key = config.get("ws_api_key") or os.environ.get("WS_API_KEY")
    return Settings(
        feature_spec=feature_spec,
        risk_params=risk_params,
        history_path=history_path,
        ws_url=ws_url,
        ws_api_key=ws_api_key,
    )
