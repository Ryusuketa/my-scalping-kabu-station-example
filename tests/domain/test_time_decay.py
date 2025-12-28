import pytest

from my_scalping_kabu_station_example.domain.market.time import TimeDecay


def test_time_decay_alpha_increases_with_dt() -> None:
    decay = TimeDecay(tau_seconds=2.0)
    small = decay.alpha(0.1)
    larger = decay.alpha(1.0)

    assert 0 <= small < larger < 1


def test_time_decay_rejects_negative_dt() -> None:
    decay = TimeDecay(tau_seconds=1.0)
    with pytest.raises(ValueError):
        decay.alpha(-0.5)
