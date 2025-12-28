from my_scalping_kabu_station_example.infrastructure.scheduler.timer import schedule


def test_schedule_runs_for_requested_iterations() -> None:
    calls: list[float] = []

    class FakeClock:
        def __init__(self) -> None:
            self.now = 0.0

        def __call__(self) -> float:
            return self.now

        def sleep(self, seconds: float) -> None:
            self.now += seconds

    clock = FakeClock()

    def job() -> None:
        calls.append(clock())

    schedule(
        interval_seconds=1.0,
        fn=job,
        iterations=3,
        clock=clock,
        sleep_fn=clock.sleep,
    )

    assert calls == [0.0, 1.0, 2.0]
