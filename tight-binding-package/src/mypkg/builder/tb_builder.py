from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..geometry.types import GeometryLike
from ..physics.configs import TBPhysics

def hermitian_part(mat: NDArray[np.complex128]) -> NDArray[np.complex128]:
    return (mat + mat.conj().T) / 2.0

class TBBuilder:
    """
    Builder layer: GeometryLike + TBPhysics -> Hamiltonian.
    For now: placeholder dense Hermitian matrix (debug).
    Later: COO->CSR using iter_bonds(kind) and PairMatrix blocks.
    """
    def __init__(self, geo: GeometryLike, phys: TBPhysics) -> None:
        self.geo = geo
        self.phys = phys

    def build_hamiltonian_dense_debug(self) -> NDArray[np.complex128]:
        rng = np.random.default_rng(int(self.phys.seed))
        n = self.geo.n_active * self.phys.basis.ndof
        mat = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
        return hermitian_part(mat)