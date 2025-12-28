"""Instrument definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from domain.market.types import Symbol


@dataclass(frozen=True)
class Instrument:
    symbol: Symbol
    metadata: Optional[Dict[str, Any]] = None
