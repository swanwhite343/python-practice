from __future__ import annotations

from typing import Protocol, NewType
from collections.abc import Collection, Iterable
from enum import Enum

GlobalIndex = NewType("GlobalIndex", int)
ActiveIndex = NewType("ActiveIndex", int)
Bond = tuple[ActiveIndex, ActiveIndex]

class GeometryLike(Protocol):
    provided_bond_keys: Collection[str]
    n_global: int
    @property
    def n_active(self) -> int: ...
    def iter_bonds(self, kind: str) -> Iterable[Bond]: ...
    
class BoundaryCondition(str, Enum):
    OPEN = "open"
    PERIODIC = "periodic"