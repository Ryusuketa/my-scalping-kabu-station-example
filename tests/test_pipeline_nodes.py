import csv
import tempfile
import unittest
from datetime import datetime

from my_scalping_kabu_station_example.domain.order_book import (
    Level,
    OrderBookSnapshot,
    OrderBookUpdate,
)
from my_scalping_kabu_station_example.domain.types import to_price_key
from my_scalping_kabu_station_example.infra.persistence import (
    CsvHistoryStore,
    InMemorySnapshotBuffer,
)
from my_scalping_kabu_station_example.service.pipeline import NormalizeNode, PersistAndBufferNode


class StubHistoryStore:
    def __init__(self) -> None:
        self.snapshots: list[OrderBookSnapshot] = []

    def append(self, snapshot: OrderBookSnapshot) -> None:
        self.snapshots.append(snapshot)


class NormalizeNodeTestCase(unittest.TestCase):
    def test_normalize_node_builds_snapshot(self) -> None:
        update = OrderBookUpdate(
            ts=datetime(2024, 1, 1, 0, 0, 0),
            symbol="TEST",
            bids=[(100.1, 1.0), (100.2, 2.0), (100.0, 3.0)],
            asks=[(100.3, 1.5), (100.4, 1.0), (100.25, 2.0)],
        )

        node = NormalizeNode()
        snapshot = node.normalize(update)

        self.assertEqual(update.ts, snapshot.ts)
        self.assertEqual(update.symbol, snapshot.symbol)
        # Best bid should be the highest price
        self.assertEqual(to_price_key(100.2), snapshot.best_bid_price)
        # Best ask should be the lowest price
        self.assertEqual(to_price_key(100.25), snapshot.best_ask_price)
        self.assertEqual(3, len(snapshot.bid_levels))
        self.assertEqual(3, len(snapshot.ask_levels))
        self.assertEqual(snapshot.bid_levels[0].price, snapshot.best_bid_price)
        self.assertEqual(snapshot.ask_levels[0].price, snapshot.best_ask_price)


class PersistAndBufferNodeTestCase(unittest.TestCase):
    def test_persist_and_buffer_node_appends_and_returns_previous(self) -> None:
        store = StubHistoryStore()
        buffer = InMemorySnapshotBuffer()
        node = PersistAndBufferNode(history_store=store, buffer=buffer)

        first = OrderBookSnapshot.from_levels(
            ts=datetime(2024, 1, 1, 0, 0, 0),
            symbol="TEST",
            bid_levels=[Level(to_price_key(100), 1.0)],
            ask_levels=[Level(to_price_key(101), 2.0)],
        )
        prev = node.persist_and_buffer(first)
        self.assertIsNone(prev)
        self.assertEqual([first], store.snapshots)
        self.assertEqual(first, buffer.previous())

        second = OrderBookSnapshot.from_levels(
            ts=datetime(2024, 1, 1, 0, 0, 1),
            symbol="TEST",
            bid_levels=[Level(to_price_key(100), 1.5)],
            ask_levels=[Level(to_price_key(101), 2.5)],
        )
        prev = node.persist_and_buffer(second)
        self.assertEqual(first, prev)
        self.assertEqual([first, second], store.snapshots)
        self.assertEqual(second, buffer.previous())


class CsvHistoryStoreTestCase(unittest.TestCase):
    def test_csv_history_store_writes_fixed_columns(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory()
        path = f"{tmp_dir.name}/history.csv"
        store = CsvHistoryStore(path)

        snapshot = OrderBookSnapshot.from_levels(
            ts=datetime(2024, 1, 1, 0, 0, 0),
            symbol="TEST",
            bid_levels=[
                Level(to_price_key(100 + i * 0.1), i + 1) for i in range(2)
            ],
            ask_levels=[
                Level(to_price_key(100.5 + i * 0.1), i + 3) for i in range(2)
            ],
        )

        store.append(snapshot)
        store.append(snapshot)

        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(2, len(rows))
        self.assertIn("bid_p10", rows[0])
        self.assertEqual(str(snapshot.bid_levels[0].price), rows[0]["bid_p1"])
        self.assertEqual(str(snapshot.ask_levels[0].price), rows[0]["ask_p1"])
        self.assertEqual(str(snapshot.bid_levels[1].price), rows[0]["bid_p2"])
        self.assertEqual("", rows[0]["bid_p10"])  # empty columns render as empty string

        tmp_dir.cleanup()


class InMemorySnapshotBufferTestCase(unittest.TestCase):
    def test_in_memory_snapshot_buffer_tracks_previous(self) -> None:
        buffer = InMemorySnapshotBuffer()
        self.assertIsNone(buffer.previous())

        snap1 = OrderBookSnapshot.from_levels(
            ts=datetime(2024, 1, 1, 0, 0, 0),
            symbol="TEST",
            bid_levels=[Level(to_price_key(100), 1.0)],
            ask_levels=[Level(to_price_key(101), 1.0)],
        )
        snap2 = OrderBookSnapshot.from_levels(
            ts=datetime(2024, 1, 1, 0, 0, 1),
            symbol="TEST",
            bid_levels=[Level(to_price_key(100.1), 1.0)],
            ask_levels=[Level(to_price_key(101.1), 1.0)],
        )

        self.assertIsNone(buffer.update(snap1))
        self.assertEqual(snap1, buffer.previous())
        self.assertEqual(snap1, buffer.update(snap2))
        self.assertEqual(snap2, buffer.previous())


if __name__ == "__main__":
    unittest.main()
