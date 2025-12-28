from decimal import Decimal

import pytest

from my_scalping_kabu_station_example.domain.market.types import (
    PriceKey,
    price_key_from,
)


def test_price_key_from_converts_float_without_binary_artifacts() -> None:
    key = price_key_from(100.1)

    assert isinstance(key, Decimal)
    assert str(key) == "100.1"


def test_price_key_from_accepts_int_and_decimal() -> None:
    assert price_key_from(5) == PriceKey(Decimal("5"))
    assert price_key_from(Decimal("123.45")) == PriceKey(Decimal("123.45"))


def test_price_key_from_rejects_unsupported_types() -> None:
    with pytest.raises(TypeError):
        price_key_from(object())
