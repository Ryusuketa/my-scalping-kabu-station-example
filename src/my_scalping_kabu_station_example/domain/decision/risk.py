"""Risk parameter definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskParams:
    max_position: float
    stop_loss: float
    take_profit: float
    cooldown_seconds: float = 0.0
