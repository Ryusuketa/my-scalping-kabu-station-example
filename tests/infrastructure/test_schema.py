from my_scalping_kabu_station_example.domain.features.expr import Const
from my_scalping_kabu_station_example.domain.features.spec import FeatureDef, FeatureSpec
from my_scalping_kabu_station_example.infrastructure.ml.schema import feature_ordering


def test_feature_ordering_preserves_spec_order() -> None:
    spec = FeatureSpec(
        version="v1",
        eps=1e-9,
        params={},
        features=[FeatureDef("a", Const(1.0)), FeatureDef("b", Const(2.0))],
    )

    ordering = feature_ordering(spec)

    assert ordering == ["a", "b"]
