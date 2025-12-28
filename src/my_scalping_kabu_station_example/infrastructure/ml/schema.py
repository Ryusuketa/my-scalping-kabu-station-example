"""Model schema helpers."""

from __future__ import annotations

from typing import List

from my_scalping_kabu_station_example.domain.features.spec import FeatureSpec


def feature_ordering(spec: FeatureSpec) -> List[str]:
    """Return feature names in the order defined by the spec."""

    return [feature.name for feature in spec.features]
