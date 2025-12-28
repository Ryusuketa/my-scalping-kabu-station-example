from my_scalping_kabu_station_example.domain.decision.risk import RiskParams
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.infrastructure.config.settings import Settings, load_settings


def test_load_settings_uses_defaults() -> None:
    settings = load_settings()

    assert isinstance(settings, Settings)
    assert settings.feature_spec.version == "ob10_v1"
    assert settings.feature_spec.eps == 1e-9
    assert settings.risk_params.max_position == 1.0
    assert settings.history_path.as_posix().endswith("data/history.csv")


def test_load_settings_accepts_overrides() -> None:
    spec = FeatureSpec(version="v2", eps=1e-6, params={"tau": 0.5}, features=[])
    risk = RiskParams(max_position=2.0, stop_loss=0.3, take_profit=0.6, cooldown_seconds=5.0)

    settings = load_settings(
        {"feature_spec": spec, "risk_params": risk, "history_path": "tmp/history.csv"}
    )

    assert settings.feature_spec is spec
    assert settings.risk_params is risk
    assert settings.history_path.as_posix().endswith("tmp/history.csv")
