"""Entrypoint for trainer process."""

from __future__ import annotations

from my_scalping_kabu_station_example.infrastructure.main.training_bootstrap import (
    train_models_from_history,
)


def main() -> None:
    train_models_from_history()


if __name__ == "__main__":
    main()
