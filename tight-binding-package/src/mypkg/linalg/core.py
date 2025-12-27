from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import List

from pydantic import RootModel, model_validator
from .types import PairMatrixData

class PairMatrix(RootModel[PairMatrixData]):
    @model_validator(mode="after")
    def _check_square_and_pairs(self):
        mat = self.root
        n = len(mat)
        if n == 0:
            raise ValueError("Matrix must be non-empty.")
        if any(len(row) != n for row in mat):
            raise ValueError("Matrix must be square (n x n).")
        return self

    def to_complex(self) -> np.ndarray:
        arr = np.asarray(self.root, dtype=float)  # shape (n, n, 2)
        if arr.ndim != 3 or arr.shape[-1] != 2:
            raise ValueError(f"Expected shape (n,n,2), got {arr.shape}")
        return arr[..., 0] + 1j * arr[..., 1]