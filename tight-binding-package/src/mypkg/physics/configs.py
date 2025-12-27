from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..linalg.core import PairMatrix
from ..utils.core import stable_hash_from_dict, DEFAULT_HASH_LENGTH
from ..types.scalars import Seed
from .types import BasisAxis


class LocalBasisConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    n_orb: int = Field(ge=1)
    n_spin: int = Field(ge=1)
    order: tuple[BasisAxis, BasisAxis] = ("orb", "spin")

    @property
    def ndof(self) -> int:
        return self.n_orb * self.n_spin

    @model_validator(mode="after")
    def _check_order(self):
        if set(self.order) != {"orb", "spin"}:
            raise ValueError("basis.order must be a permutation of ('orb','spin').")
        if self.order[0] == self.order[1]:
            raise ValueError("basis.order must not contain duplicates.")
        return self
    
class TBParams(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    onsite: PairMatrix
    hopping: dict[str, PairMatrix]

    @model_validator(mode="after")
    def _check_minimum(self):
        if not self.hopping:
            raise ValueError("hopping must be non-empty.")
        return self
    
    @model_validator(mode="after")
    def _normalize_hopping(self):
        # When nn1 exists, use it as default vals of nn1x and nn1y.
        if "nn1" in self.hopping:
            hop = dict(self.hopping)
            if "nn1x" not in hop:
                hop["nn1x"] = hop["nn1"]
            if "nn1y" not in hop:
                hop["nn1y"] = hop["nn1"]
            return self.model_copy(update={"hopping": hop})
        return self
    
class ABFluxConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    phi_over_phi0: float = 0.0


class ZeemanConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    # Zeeman term: (1/2) * (Bx*pauli_x + By*pauli_y + Bz*pauli_z)
    # Here Bx,By,Bz are in energy units (same units as hopping t).
    B: tuple[float, float, float] = (0.0, 0.0, 0.0)

    # optional convention
    convention: Literal["half"] = "half"  # means multiply by 1/2 in builder


class FieldConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    ab_flux: ABFluxConfig | None = None
    zeeman: ZeemanConfig | None = None

class PhysicsConfigBase(BaseModel):
    model_config = ConfigDict(frozen=True)
    seed: Seed = 0

    def get_hash(self, length: int = DEFAULT_HASH_LENGTH) -> str:
        return stable_hash_from_dict(self.model_dump(mode="json", exclude=None), length)
 

class TBPhysicsConfigBase(PhysicsConfigBase):
    basis: LocalBasisConfig
    params: TBParams

    @model_validator(mode="after")
    def _check_shapes(self):
        ndof = self.basis.ndof
        T0 = self.params.onsite.to_complex()
        if T0.shape != (ndof, ndof):
            raise ValueError("onsite matrix size != ndof")

        for k, pm in self.params.hopping.items():
            Tk = pm.to_complex()
            if Tk.shape != (ndof, ndof):
                raise ValueError(f"hopping.{k} matrix size != ndof")

        return self


class TBPhysics(TBPhysicsConfigBase):
    model: Literal["tb"]
    fields: FieldConfig | None = None