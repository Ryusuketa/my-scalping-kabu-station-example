"""WebSocket client placeholder."""

from __future__ import annotations


class WebSocketClient:
    def connect(self) -> None:
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError
