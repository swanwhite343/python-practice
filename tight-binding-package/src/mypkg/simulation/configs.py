from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator
from typing import Any

from ..geometry.config_union import GeometryConfig
from ..geometry.types import FreezableGeometryLike  # 追加した Protocol
from ..physics.configs import TBPhysics
from ..solver.configs import SolverConfig


class SimulationConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    geometry: GeometryConfig      # ✅ config を読む
    physics: TBPhysics
    solver: SolverConfig

    defects: Any | None = None
    perturbations: Any | None = None
    
    def build_geometry(self) -> FreezableGeometryLike:
        geo = self.geometry.build(removed_sites=None)  # ✅ build は config が持つ
        geo.freeze()                                   # ✅ Protocol にあるのでIDEもOK
        return geo

    @model_validator(mode="after")
    def _cross_check(self):
        geo = self.geometry.build(removed_sites=None)

        hop_keys = set(self.physics.params.hopping.keys())
        provided = set(getattr(geo, "provided_bond_keys", set()))
        bad = hop_keys - provided
        if bad:
            raise ValueError(
                f"Unsupported hopping keys for {type(geo).__name__}: {sorted(bad)}"
            )

        fields = getattr(self.physics, "fields", None)
        if fields is not None and getattr(fields, "ab_flux", None) is not None:
            if not getattr(self.geometry, "supports_ab_flux", False):
                raise ValueError("ab_flux is set but geometry does not support it")

        return self
