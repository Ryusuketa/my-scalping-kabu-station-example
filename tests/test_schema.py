import unittest
from datetime import datetime

from my_scalping_kabu_station_example.domain.order_book import Level
from my_scalping_kabu_station_example.domain.schema.snapshot import OrderBookSnapshotSchema
from my_scalping_kabu_station_example.domain.types import to_price_key


class OrderBookSnapshotSchemaTestCase(unittest.TestCase):
    def test_from_levels_pads_to_fixed_depth(self) -> None:
        ts_iso = datetime(2024, 1, 1, 0, 0, 0).isoformat()
        bids = [Level(price=to_price_key(100 + i * 0.1), quantity=i + 1) for i in range(2)]
        asks = [Level(price=to_price_key(100.5 + i * 0.1), quantity=i + 3) for i in range(1)]

        schema = OrderBookSnapshotSchema.from_levels(ts_iso=ts_iso, symbol="TEST", bid_levels=bids, ask_levels=asks)

        self.assertEqual(10, len(schema.bid_prices))
        self.assertEqual(10, len(schema.bid_quantities))
        self.assertEqual(10, len(schema.ask_prices))
        self.assertEqual(10, len(schema.ask_quantities))
        self.assertEqual(schema.bid_prices[0], bids[0].price)
        self.assertEqual(schema.bid_quantities[0], bids[0].quantity)
        self.assertIsNone(schema.bid_prices[-1])
        self.assertIsNone(schema.bid_quantities[-1])
        self.assertEqual(schema.ask_prices[0], asks[0].price)
        self.assertEqual(schema.ask_quantities[0], asks[0].quantity)
        self.assertIsNone(schema.ask_prices[-1])
        self.assertIsNone(schema.ask_quantities[-1])


if __name__ == "__main__":
    unittest.main()
