"""In-memory ring buffer for market snapshots."""

from __future__ import annotations


class RingBuffer:
    def __init__(self, size: int) -> None:
        self.size = size
        self.items: list = []

    def append(self, item) -> None:
        if len(self.items) >= self.size:
            self.items.pop(0)
        self.items.append(item)

    def get(self, n: int):
        return self.items[-n:]
