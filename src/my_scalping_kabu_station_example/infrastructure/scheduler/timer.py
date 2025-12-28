"""Timer utilities."""

from __future__ import annotations

import random
import time
from typing import Callable, Optional


def schedule(
    interval_seconds: float,
    fn: Callable[[], None],
    *,
    iterations: Optional[int] = None,
    jitter_seconds: float = 0.0,
    clock: Callable[[], float] = time.monotonic,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> None:
    """Run a function on a fixed interval with optional jitter.

    This is a synchronous loop; callers should run it in a worker thread/process.
    """

    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    if jitter_seconds < 0:
        raise ValueError("jitter_seconds must be non-negative")

    count = 0
    next_run = clock()
    while iterations is None or count < iterations:
        fn()
        count += 1
        next_run += interval_seconds
        sleep_for = max(0.0, next_run - clock())
        if jitter_seconds:
            sleep_for += random.uniform(0.0, jitter_seconds)
        if sleep_for:
            sleep_fn(sleep_for)
