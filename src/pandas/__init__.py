from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Tuple


def isna(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    return False


@dataclass
class _Timestamp:
    value: datetime

    def to_pydatetime(self) -> datetime:
        return self.value


def to_datetime(value: Any) -> _Timestamp:
    if isinstance(value, _Timestamp):
        return value
    if hasattr(value, "to_pydatetime"):
        return _Timestamp(value.to_pydatetime())  # type: ignore[arg-type]
    if isinstance(value, datetime):
        return _Timestamp(value)
    return _Timestamp(datetime.fromisoformat(str(value)))


class Series:
    def __init__(self, data: Dict[str, Any]):
        self._data = dict(data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def items(self):
        return self._data.items()

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


class DataFrame:
    def __init__(self, data: Iterable[Dict[str, Any]] | None = None):
        rows = list(data) if data is not None else []
        self._rows: List[Dict[str, Any]] = [dict(row) for row in rows]
        self.columns = list({k for row in self._rows for k in row})

    def iterrows(self) -> Iterator[Tuple[int, Series]]:
        for idx, row in enumerate(self._rows):
            yield idx, Series(row)

    def reset_index(self, drop: bool = False) -> "DataFrame":
        if drop:
            return DataFrame(self._rows)
        new_rows = []
        for idx, row in enumerate(self._rows):
            new_row = dict(row)
            new_row["index"] = idx
            new_rows.append(new_row)
        return DataFrame(new_rows)

    def to_dicts(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in self._rows]

    def __len__(self) -> int:
        return len(self._rows)


class _Testing:
    @staticmethod
    def assert_frame_equal(left: DataFrame, right: DataFrame, rtol: float = 1e-9, atol: float = 0.0) -> None:
        if len(left) != len(right):
            raise AssertionError(f"DataFrame length mismatch: {len(left)} != {len(right)}")

        left_rows = left.to_dicts()
        right_rows = right.to_dicts()

        for idx, (lrow, rrow) in enumerate(zip(left_rows, right_rows)):
            keys = set(lrow.keys()) | set(rrow.keys())
            for key in keys:
                lv = lrow.get(key)
                rv = rrow.get(key)
                if isna(lv) and isna(rv):
                    continue
                if isinstance(lv, (int, float)) and isinstance(rv, (int, float)):
                    if not math.isclose(lv, rv, rel_tol=rtol, abs_tol=atol):
                        raise AssertionError(f"Row {idx} column {key} mismatch: {lv} != {rv}")
                else:
                    if lv != rv:
                        raise AssertionError(f"Row {idx} column {key} mismatch: {lv} != {rv}")


testing = _Testing()

__all__ = ["DataFrame", "Series", "isna", "to_datetime", "testing"]
