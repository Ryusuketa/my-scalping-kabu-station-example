"""CSV-based history store."""

from __future__ import annotations


class CsvHistoryStore:
    def append(self, snapshot):
        raise NotImplementedError
