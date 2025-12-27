from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict

from ..types.scalars import LatticeSide
from ..utils.core import stable_hash_from_dict, DEFAULT_HASH_LENGTH
from .types import BoundaryCondition, GeometryLike

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .square import SquareGeometry
    from .chain import ChainGeometry
    from .ab_ring import ABRingGeometry
    from .honeycomb import HoneycombGeometry
    
class GeometryConfigBase(BaseModel):
    model_config = ConfigDict(frozen=True)

    def get_hash(self, length: int = DEFAULT_HASH_LENGTH) -> str:
        return stable_hash_from_dict(self.model_dump(mode="json", exclude=None), length)
    
    def build(self, *, removed_sites: Any = None) -> GeometryLike:
        raise NotImplementedError
    
    
class ChainGeometryConfig(GeometryConfigBase):
    lattice: Literal["chain"]
    nx: LatticeSide
    boundary_x: BoundaryCondition

    @property
    def dim(self) -> int: return 1
    
    def build(self, *, removed_sites: set[tuple[int]] | None =None) -> ChainGeometry:
        from .chain import ChainGeometry
        return ChainGeometry(self, removed_sites=removed_sites)


class ABRingGeometryConfig(GeometryConfigBase):
    lattice: Literal["ab_ring"]
    nx: LatticeSide
    boundary_x: BoundaryCondition = BoundaryCondition.PERIODIC
    supports_ab_flux: bool = True
    
    def build(self, *, removed_sites: set[tuple[int]] | None = None) -> ABRingGeometry:
        from .ab_ring import ABRingGeometry
        return ABRingGeometry(self, removed_sites=removed_sites)
    

class SquareGeometryConfig(GeometryConfigBase):
    lattice: Literal["square"]
    nx: LatticeSide
    ny: LatticeSide
    boundary_x: BoundaryCondition
    boundary_y: BoundaryCondition
    supports_ab_flux: bool = False
    
    @property
    def dim(self) -> int: return 2
    
    def build(self, *, removed_sites: set[tuple[int, int]] | None =None) -> SquareGeometry:
        from .square import SquareGeometry
        return SquareGeometry(self, removed_sites=removed_sites)

class HoneycombGeometryConfig(GeometryConfigBase):
    lattice: Literal["honeycomb"]
    nx: LatticeSide
    ny: LatticeSide
    boundary_x: BoundaryCondition
    boundary_y: BoundaryCondition
    supports_ab_flux: bool = False
    
    @property
    def dim(self) -> int: return 2

    def build(self, *, removed_sites: set[tuple[int, int, int]] | None = None) -> HoneyCombGeometry:
        from .honeycomb import HoneycombGeometry
        return HoneycombGeometry(self, removed_sites=removed_sites)

