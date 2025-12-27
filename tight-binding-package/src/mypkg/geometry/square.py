from __future__ import annotations

import logging
import numpy as np
from numpy.typing import NDArray
from collections.abc import Iterator

from ..utils.core import stable_hash_from_dict, DEFAULT_HASH_LENGTH
from .types import GlobalIndex, ActiveIndex, BoundaryCondition, GeometryLike

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .configs import SquareGeometryConfig

log = logging.getLogger(__name__)

class SquareGeometry(GeometryLike):
    provided_bond_keys = {"nn1x", "nn1y", "nn2"}

    def __init__(self, config: SquareGeometryConfig, *, removed_sites: set[tuple[int, int]] | None = None) -> None:
        self.config = config
        self.removed_sites: set[tuple[int, int]] = set(removed_sites or [])
        self.n_global: int = config.nx * config.ny
        self._maps_dirty: bool = True
        self._frozen: bool = False
        self._global_to_active_idx: NDArray[np.intp] | None = None
        self._active_to_global_idx: NDArray[np.intp] | None = None

    @property
    def n_active(self) -> int:
        return self.n_global - len(self.removed_sites)

    def freeze(self) -> None:
        self._frozen = True
        self._ensure_maps()

    def _invalidate_maps(self) -> None:
        self._maps_dirty = True

    def get_geometry_hash(self, length: int = DEFAULT_HASH_LENGTH) -> str:
        geometry_state = {
            "config": self.config.model_dump(mode="json"),
            "removed_sites": [list(xy) for xy in sorted(self.removed_sites)],
        }
        return stable_hash_from_dict(geometry_state, length)

    def ensure_coord_in_bounds(self, coord: tuple[int, int]) -> None:
        x, y = coord
        if not (0 <= x < self.config.nx and 0 <= y < self.config.ny):
            log.error(
                f"Out-of-bounds coordinate ({x}, {y}); "
                f"valid range x:[0, {self.config.nx}), y:[0, {self.config.ny}),"
            )
            raise ValueError(f"Coordinates out of bounds: ({x}, {y})")

    def remove_site(self, coord: tuple[int, int], *, wrap: bool = False) -> None:
        if self._frozen:
            msg = "Geometry is frozen; cannot modify removed_sites."
            log.error(msg)
            raise RuntimeError(msg)

        x, y = coord
        if wrap:
            x, y = self.wrap_xy(x, y)
        else:
            self.ensure_coord_in_bounds((x, y))

        coord_wrapped = (x, y)
        if coord_wrapped not in self.removed_sites:
            self.removed_sites.add(coord_wrapped)
            self._invalidate_maps()

    def xy_to_global(self, x: int, y: int) -> GlobalIndex:
        self.ensure_coord_in_bounds((x, y))
        return GlobalIndex(x + self.config.nx * y)

    def global_to_xy(self, global_idx: GlobalIndex) -> tuple[int, int]:
        global_i = int(global_idx)
        nx = self.config.nx
        return (global_i % nx, global_i // nx)

    def wrap_xy(self, x: int, y: int) -> tuple[int, int]:
        nx, ny = self.config.nx, self.config.ny
        if self.config.boundary_x == BoundaryCondition.PERIODIC:
            x %= nx
        if self.config.boundary_y == BoundaryCondition.PERIODIC:
            y %= ny
        return x, y

    def _rebuild_index_maps(self) -> None:
        nx = self.config.nx
        n_global = self.n_global

        global_to_active_idx = np.full(n_global, -1, dtype=np.intp)

        removed_mask = np.zeros(n_global, dtype=bool)
        for (x, y) in self.removed_sites:
            removed_mask[x + nx * y] = True

        self._active_to_global_idx = np.flatnonzero(~removed_mask).astype(np.intp)
        global_to_active_idx[self._active_to_global_idx] = np.arange(self._active_to_global_idx.size, dtype=np.intp)

        self._global_to_active_idx = global_to_active_idx
        self._maps_dirty = False

    def _ensure_maps(self) -> None:
        if self._maps_dirty or self._global_to_active_idx is None or self._active_to_global_idx is None:
            self._rebuild_index_maps()

    def global_to_active(self, i_global: GlobalIndex) -> ActiveIndex | None:
        self._ensure_maps()
        assert self._global_to_active_idx is not None
        i = int(self._global_to_active_idx[int(i_global)])
        return None if i < 0 else ActiveIndex(i)

    def active_to_global(self, i_active: ActiveIndex) -> GlobalIndex:
        self._ensure_maps()
        assert self._active_to_global_idx is not None
        return GlobalIndex(int(self._active_to_global_idx[int(i_active)]))

    def neighbor_xy(self, x: int, y: int, dx: int, dy: int) -> tuple[int, int] | None:
        nx, ny = self.config.nx, self.config.ny
        xx, yy = x + dx, y + dy

        if self.config.boundary_x == BoundaryCondition.PERIODIC:
            xx %= nx
        else:
            if not (0 <= xx < nx):
                return None

        if self.config.boundary_y == BoundaryCondition.PERIODIC:
            yy %= ny
        else:
            if not (0 <= yy < ny):
                return None

        return xx, yy

    def neighbor_global(self, x: int, y: int, dx: int, dy: int) -> GlobalIndex | None:
        out = self.neighbor_xy(x, y, dx, dy)
        if out is None:
            return None
        xx, yy = out
        return GlobalIndex(xx + self.config.nx * yy)

    def neighbor_active(self, i_act: ActiveIndex, dx: int, dy: int) -> ActiveIndex | None:
        i_global = self.active_to_global(i_act)
        x, y = self.global_to_xy(i_global)
        j_global = self.neighbor_global(x, y, dx, dy)
        if j_global is None:
            return None
        return self.global_to_active(j_global)

    def iter_bonds(self, kind: str) -> Iterator[tuple[ActiveIndex, ActiveIndex]]:
        if kind == "nn1x":
            shifts = [(+1, 0)]
        elif kind == "nn1y":
            shifts = [(0, +1)]
        elif kind == "nn2":
            shifts = [(+1, +1), (-1, +1)]
        else:
            raise ValueError(f"Unknown bond kind: {kind}")

        for i in range(self.n_active):
            i_act = ActiveIndex(i)
            for dx, dy in shifts:
                j_act = self.neighbor_active(i_act, dx, dy)
                if j_act is None:
                    continue
                yield i_act, j_act


from .configs import SquareGeometryConfig 