from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Iterator
from ..utils import stable_hash_from_dict, DEFAULT_HASH_LENGTH
from .types import ActiveIndex, GeometryLike

if TYPE_CHECKING:
    from .configs import ChainGeometryConfig

class ChainGeometry(GeometryLike):
    provided_bond_keys = {"nn1", "nn2"}

    def __init__(self, config: ChainGeometryConfig, *, removed_sites=None):
        self.config = config
        self.removed_sites = set(removed_sites or [])
        self.n_global = config.nx

    @property
    def n_active(self) -> int:
        return self.n_global - len(self.removed_sites)

    def iter_bonds(self, kind: str) -> Iterator[tuple[ActiveIndex, ActiveIndex]]:
        raise NotImplementedError

    def get_geometry_hash(self, length: int = DEFAULT_HASH_LENGTH) -> str:
        state = {
            "config": self.config.model_dump(mode="json"),
            "removed_sites": [list(x) for x in sorted(self.removed_sites)],
        }
        return stable_hash_from_dict(state, length)