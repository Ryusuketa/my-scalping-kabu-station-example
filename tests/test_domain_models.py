import unittest
from datetime import datetime
from decimal import Decimal

from my_scalping_kabu_station_example.domain.features.expr import (
    AddSum,
    DepletionSum,
    DepthQtySum,
    Diff,
    Imbalance,
    MicroPrice,
    Mid,
    TimeDecayEma,
)
from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec
from my_scalping_kabu_station_example.domain.features.state import FeatureState
from my_scalping_kabu_station_example.domain.order_book import Level, OrderBookSnapshot
from my_scalping_kabu_station_example.domain.types import Side, to_price_key


class PriceKeyTestCase(unittest.TestCase):
    def test_to_price_key_uses_decimal(self) -> None:
        price_float = 101.23
        key = to_price_key(price_float)
        self.assertIsInstance(key, Decimal)
        self.assertEqual(Decimal("101.23"), key)


class OrderBookSnapshotTestCase(unittest.TestCase):
    def test_snapshot_sorts_trims_and_computes_fields(self) -> None:
        ts = datetime(2024, 1, 1, 12, 0, 0)
        bid_levels = [
            Level(to_price_key(100 + i * 0.1), i + 1) for i in range(12)
        ]  # increasing price
        ask_levels = [
            Level(to_price_key(100.5 + i * 0.1), i + 2) for i in range(12)
        ]  # increasing price

        snapshot = OrderBookSnapshot.from_levels(ts, "TEST", bid_levels, ask_levels)

        self.assertEqual(10, len(snapshot.bid_levels))
        self.assertEqual(10, len(snapshot.ask_levels))
        # Bids sorted descending
        self.assertGreater(snapshot.bid_levels[0].price, snapshot.bid_levels[-1].price)
        # Asks sorted ascending
        self.assertLess(snapshot.ask_levels[0].price, snapshot.ask_levels[-1].price)

        self.assertEqual(snapshot.best_bid_price, snapshot.bid_levels[0].price)
        self.assertEqual(snapshot.best_ask_price, snapshot.ask_levels[0].price)
        self.assertEqual(
            (snapshot.best_bid_price + snapshot.best_ask_price) / 2, snapshot.mid
        )
        self.assertEqual(10, len(snapshot.bid_map))
        self.assertEqual(10, len(snapshot.ask_map))


class FeatureSpecTestCase(unittest.TestCase):
    def test_ob10_v1_contains_expected_features(self) -> None:
        spec = FeatureSpec.ob10_v1()

        names = {f.name for f in spec.features}
        self.assertEqual(spec.version, "ob10_v1")
        self.assertIn("OBI_5", names)
        self.assertIn("OBI_10", names)
        self.assertIn("micro_price", names)
        self.assertIn("micro_price_shift", names)
        self.assertIn("depletion_imbalance", names)
        self.assertIn("add_imbalance", names)
        self.assertIn("DI_ema", names)
        self.assertIn("AI_ema", names)
        self.assertIn("OBI_5_ema", names)

        obi_5 = next(f for f in spec.features if f.name == "OBI_5")
        self.assertIsInstance(obi_5.expr, Imbalance)
        self.assertEqual(DepthQtySum(Side.BID, 5), obi_5.expr.numerator)
        self.assertEqual(DepthQtySum(Side.ASK, 5), obi_5.expr.denominator)

        micro_shift = next(f for f in spec.features if f.name == "micro_price_shift")
        self.assertIsInstance(micro_shift.expr, Diff)
        self.assertIsInstance(micro_shift.expr.left, MicroPrice)
        self.assertIsInstance(micro_shift.expr.right, Mid)

        di_ema = next(f for f in spec.features if f.name == "DI_ema")
        self.assertIsInstance(di_ema.expr, TimeDecayEma)
        self.assertEqual("DI", di_ema.expr.target.name)  # type: ignore[attr-defined]

        ai_ema = next(f for f in spec.features if f.name == "AI_ema")
        self.assertIsInstance(ai_ema.expr, TimeDecayEma)
        self.assertEqual("AI", ai_ema.expr.target.name)  # type: ignore[attr-defined]

        obi_ema = next(f for f in spec.features if f.name == "OBI_5_ema")
        self.assertIsInstance(obi_ema.expr, TimeDecayEma)
        self.assertEqual("OBI_5", obi_ema.expr.name)


class FeatureStateTestCase(unittest.TestCase):
    def test_with_updated_ema_returns_new_state(self) -> None:
        state = FeatureState()
        updated = state.with_updated_ema("DI_ema", 0.1)
        self.assertIsNone(state.last_ts)
        self.assertEqual({}, state.ema_values)
        self.assertEqual({"DI_ema": 0.1}, updated.ema_values)
        self.assertIsNone(updated.last_ts)


if __name__ == "__main__":
    unittest.main()

