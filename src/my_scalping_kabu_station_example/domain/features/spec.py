"""Feature specification definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional

from my_scalping_kabu_station_example.domain.features.expr import Expr


@dataclass(frozen=True)
class FeatureDef:
    """Named feature with expression AST."""

    name: str
    expr: Expr


@dataclass
class FeatureSpec:
    """Specifies a consistent feature set and parameters."""

    version: str
    eps: float
    params: Mapping[str, object] = field(default_factory=dict)
    features: List[FeatureDef] = field(default_factory=list)

    def __post_init__(self) -> None:
        names = [feature.name for feature in self.features]
        if len(names) != len(set(names)):
            raise ValueError("Feature names must be unique within a spec")

    def add_feature(self, feature: FeatureDef) -> None:
        self.features.append(feature)
        self.__post_init__()

    def get(self, name: str) -> Optional[FeatureDef]:
        return next((f for f in self.features if f.name == name), None)

    @classmethod
    def from_features(
        cls,
        version: str,
        eps: float,
        features: Iterable[FeatureDef],
        params: Optional[Dict[str, object]] = None,
    ) -> "FeatureSpec":
        return cls(
            version=version, eps=eps, params=params or {}, features=list(features)
        )
