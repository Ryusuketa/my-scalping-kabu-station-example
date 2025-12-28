"""WebSocket client placeholder."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from websockets.sync.client import connect


@dataclass
class WebSocketClient:
    url: str
    api_key: Optional[str] = None
    _conn: Optional[Any] = None

    def connect(self) -> None:
        headers = {"X-API-KEY": self.api_key} if self.api_key else None
        self._conn = connect(self.url, additional_headers=headers)

    def receive(self) -> Any:
        if self._conn is None:
            raise RuntimeError("WebSocket connection is not established")
        return self._conn.recv()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


@dataclass
class MockWebSocketClient:
    messages: list[Any] = field(default_factory=list)
    connected: bool = False
    closed: bool = False

    def connect(self) -> None:
        self.connected = True

    def receive(self) -> Any:
        if not self.connected or self.closed:
            raise RuntimeError("MockWebSocketClient is not connected")
        if not self.messages:
            raise StopIteration("No more mock messages")
        return self.messages.pop(0)

    def close(self) -> None:
        self.closed = True
