from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator
import numpy as np
from numpy.typing import NDArray
import logging

from ..utils.core import DEFAULT_HASH_LENGTH, stable_hash_from_dict

log = logging.getLogger(__name__)


class EquilibriumConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    temperature: float = Field(0.0, ge=0.0)  # energy units (k_B=1)
    mu: float = 0.0                          # tune Fermi energy


class SolverConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    eta: float = Field(..., gt=0)
    w_min: float
    w_max: float
    n_w: int = Field(..., ge=2)

    equilibrium: EquilibriumConfig | None = None

    @model_validator(mode="after")
    def _check_ranges(self):
        if not (self.w_min < self.w_max):
            msg = "w_min must be < w_max"
            log.error(msg)
            raise ValueError(msg)
        return self

    @property
    def energy_grid(self) -> NDArray[np.float64]:
        return np.linspace(self.w_min, self.w_max, self.n_w, dtype=np.float64)

    def get_hash(self, length: int = DEFAULT_HASH_LENGTH) -> str:
        return stable_hash_from_dict(self.model_dump(mode="json", exclude=None), length)
