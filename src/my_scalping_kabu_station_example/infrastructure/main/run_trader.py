"""Entrypoint for trader process."""

from __future__ import annotations

from my_scalping_kabu_station_example.infrastructure.main.di import build_container


def main() -> dict:
    return build_container()


if __name__ == "__main__":
    main()
