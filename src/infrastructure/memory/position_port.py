"""In-memory position port for local runs/tests."""

from __future__ import annotations

from dataclasses import dataclass

from application.ports.broker import PositionPort


@dataclass
class InMemoryPositionPort(PositionPort):
    position: float = 0.0

    def current_position(self) -> float:
        return self.position
