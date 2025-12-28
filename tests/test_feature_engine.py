import math
import unittest
from datetime import datetime, timedelta

import pandas as pd

from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.features.state import FeatureState
from my_scalping_kabu_station_example.domain.order_book import Level, OrderBookSnapshot
from my_scalping_kabu_station_example.domain.types import to_price_key
from my_scalping_kabu_station_example.infra.feature_engine import PandasOrderBookFeatureEngine


def _levels(prices: list[float], quantities: list[float]) -> list[Level]:
    return [Level(to_price_key(p), qty) for p, qty in zip(prices, quantities)]


class PandasOrderBookFeatureEngineTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = FeatureSpec.ob10_v1(eps=1e-6, tau=1.0)
        self.engine = PandasOrderBookFeatureEngine()

        base_ts = datetime(2024, 1, 1, 0, 0, 0)
        self.prev_snapshot = OrderBookSnapshot.from_levels(
            ts=base_ts,
            symbol="TEST",
            bid_levels=_levels(
                [100.0, 99.9, 99.8, 99.7, 99.6],
                [5.0, 4.0, 1.0, 1.0, 1.0],
            ),
            ask_levels=_levels(
                [100.1, 100.2, 100.3, 100.4, 100.5],
                [3.0, 2.0, 2.0, 1.0, 1.0],
            ),
        )
        self.now_snapshot = OrderBookSnapshot.from_levels(
            ts=base_ts + timedelta(seconds=1),
            symbol="TEST",
            bid_levels=_levels(
                [100.0, 99.9, 99.8, 99.7, 99.6],
                [4.0, 3.0, 2.0, 1.0, 1.5],
            ),
            ask_levels=_levels(
                [100.1, 100.2, 100.3, 100.4, 100.5],
                [5.0, 1.0, 2.0, 1.0, 1.0],
            ),
        )

    def test_compute_one_streaming_features_and_ema(self) -> None:
        state = FeatureState(
            last_ts=self.prev_snapshot.ts,
            ema_values={"DI_ema": -0.5, "AI_ema": 0.25, "OBI_5_ema": 0.1},
        )

        features, new_state = self.engine.compute_one(
            spec=self.spec,
            prev_snapshot=self.prev_snapshot,
            now_snapshot=self.now_snapshot,
            state=state,
        )

        self.assertAlmostEqual((11.5 - 10.0) / (21.5 + 1e-6), features["OBI_5"], places=6)
        self.assertAlmostEqual(features["OBI_10"], features["OBI_5"], places=6)

        expected_depletion_bid = 2.0
        expected_depletion_ask = 1.0
        expected_add_bid = 1.5
        expected_add_ask = 2.0
        self.assertAlmostEqual(expected_depletion_bid, features["depletion_bid"])
        self.assertAlmostEqual(expected_depletion_ask, features["depletion_ask"])
        self.assertAlmostEqual(expected_add_bid, features["add_bid"])
        self.assertAlmostEqual(expected_add_ask, features["add_ask"])

        di = (expected_depletion_ask - expected_depletion_bid) / (
            expected_depletion_ask + expected_depletion_bid + 1e-6
        )
        ai = (expected_add_bid - expected_add_ask) / (expected_add_bid + expected_add_ask + 1e-6)
        self.assertAlmostEqual(di, features["depletion_imbalance"], places=6)
        self.assertAlmostEqual(ai, features["add_imbalance"], places=6)

        micro_price = (
            float(self.now_snapshot.best_ask_price) * self.now_snapshot.best_bid_qty
            + float(self.now_snapshot.best_bid_price) * self.now_snapshot.best_ask_qty
        ) / (self.now_snapshot.best_bid_qty + self.now_snapshot.best_ask_qty + 1e-6)
        self.assertAlmostEqual(micro_price, features["micro_price"], places=6)
        mid = float(self.now_snapshot.mid)
        self.assertAlmostEqual(micro_price - mid, features["micro_price_shift"], places=6)

        # EMA update with dt=1s and tau=1s -> alpha = 1-exp(-1)
        alpha = 1 - math.exp(-1)
        expected_di_ema = state.ema_values["DI_ema"] + alpha * (di - state.ema_values["DI_ema"])
        expected_ai_ema = state.ema_values["AI_ema"] + alpha * (ai - state.ema_values["AI_ema"])
        expected_obi_ema = state.ema_values["OBI_5_ema"] + alpha * (
            features["OBI_5"] - state.ema_values["OBI_5_ema"]
        )
        self.assertAlmostEqual(expected_di_ema, features["DI_ema"], places=6)
        self.assertAlmostEqual(expected_ai_ema, features["AI_ema"], places=6)
        self.assertAlmostEqual(expected_obi_ema, features["OBI_5_ema"], places=6)

        self.assertEqual(self.now_snapshot.ts, new_state.last_ts)
        self.assertAlmostEqual(expected_di_ema, new_state.ema_values["DI_ema"], places=6)
        self.assertAlmostEqual(expected_ai_ema, new_state.ema_values["AI_ema"], places=6)
        self.assertAlmostEqual(expected_obi_ema, new_state.ema_values["OBI_5_ema"], places=6)

    def test_compute_batch_matches_streaming(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "ts": self.prev_snapshot.ts,
                    "symbol": self.prev_snapshot.symbol,
                    **{
                        f"bid_p{i}": float(self.prev_snapshot.bid_levels[i - 1].price)
                        if i <= len(self.prev_snapshot.bid_levels)
                        else None
                        for i in range(1, 11)
                    },
                    **{
                        f"bid_q{i}": self.prev_snapshot.bid_levels[i - 1].quantity
                        if i <= len(self.prev_snapshot.bid_levels)
                        else None
                        for i in range(1, 11)
                    },
                    **{
                        f"ask_p{i}": float(self.prev_snapshot.ask_levels[i - 1].price)
                        if i <= len(self.prev_snapshot.ask_levels)
                        else None
                        for i in range(1, 11)
                    },
                    **{
                        f"ask_q{i}": self.prev_snapshot.ask_levels[i - 1].quantity
                        if i <= len(self.prev_snapshot.ask_levels)
                        else None
                        for i in range(1, 11)
                    },
                },
                {
                    "ts": self.now_snapshot.ts,
                    "symbol": self.now_snapshot.symbol,
                    **{
                        f"bid_p{i}": float(self.now_snapshot.bid_levels[i - 1].price)
                        if i <= len(self.now_snapshot.bid_levels)
                        else None
                        for i in range(1, 11)
                    },
                    **{
                        f"bid_q{i}": self.now_snapshot.bid_levels[i - 1].quantity
                        if i <= len(self.now_snapshot.bid_levels)
                        else None
                        for i in range(1, 11)
                    },
                    **{
                        f"ask_p{i}": float(self.now_snapshot.ask_levels[i - 1].price)
                        if i <= len(self.now_snapshot.ask_levels)
                        else None
                        for i in range(1, 11)
                    },
                    **{
                        f"ask_q{i}": self.now_snapshot.ask_levels[i - 1].quantity
                        if i <= len(self.now_snapshot.ask_levels)
                        else None
                        for i in range(1, 11)
                    },
                },
            ]
        )

        batch_features = self.engine.compute_batch(spec=self.spec, snapshots_df=df)

        # Streaming reference
        state = FeatureState()
        prev: OrderBookSnapshot | None = None
        streaming_rows = []
        for snapshot in [self.prev_snapshot, self.now_snapshot]:
            features, state = self.engine.compute_one(
                spec=self.spec,
                prev_snapshot=prev,
                now_snapshot=snapshot,
                state=state,
            )
            streaming_rows.append(features)
            prev = snapshot

        streaming_df = pd.DataFrame(streaming_rows)
        pd.testing.assert_frame_equal(
            batch_features.reset_index(drop=True),
            streaming_df,
            rtol=1e-6,
            atol=1e-6,
        )


if __name__ == "__main__":
    unittest.main()
