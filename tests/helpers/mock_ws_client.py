from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
