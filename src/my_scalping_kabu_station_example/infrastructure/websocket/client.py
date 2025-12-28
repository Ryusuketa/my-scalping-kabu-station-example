"""WebSocket client placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from websockets.sync.client import connect


@dataclass
class WebSocketClient:
    url: str
    _conn: Optional[Any] = None

    def connect(self) -> None:
        self._conn = connect(self.url)

    def receive(self) -> Any:
        if self._conn is None:
            raise RuntimeError("WebSocket connection is not established")
        return self._conn.recv()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
