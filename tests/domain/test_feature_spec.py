import pytest

from my_scalping_kabu_station_example.domain.features import names
from my_scalping_kabu_station_example.domain.features.expr import DepthQtySum, MicroPrice
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.domain.market.types import Side


def test_feature_spec_enforces_unique_names() -> None:
    spec = FeatureSpec(
        version="ob10_v1",
        eps=1e-9,
        features=[FeatureDef(name=names.OBI_5, expr=DepthQtySum(Side.BID, depth=5))],
    )

    with pytest.raises(ValueError):
        spec.add_feature(FeatureDef(name=names.OBI_5, expr=MicroPrice(eps=1e-9)))


def test_expr_describe_includes_parameters() -> None:
    expr = DepthQtySum(Side.ASK, depth=3)
    assert "ASK" in expr.describe()
    assert "3" in expr.describe()
