"""Lock abstraction."""

from __future__ import annotations

from typing import Protocol


class LockPort(Protocol):
    def acquire(self) -> None: ...

    def release(self) -> None: ...
