import numpy as np
from pydantic import BaseModel
from typing import Any
from pathlib import Path
from numpy.typing import NDArray
from .linalg import get_hermitian_part
from .utils import stable_hash_from_dict, DEFAULT_HASH_LENGTH
from .types import LatticeSide, Seed, HoppingAmp, OnsiteChem, LatticeCoord, NonNegInt

class PhysicsConfig(BaseModel):
    nx: LatticeSide
    ny: LatticeSide
    t1x: HoppingAmp
    t1y: HoppingAmp
    mu:  OnsiteChem
    seed: Seed
    
    def get_base_hash(self) -> str:
        data = self.model_dump(mode="json")
        return stable_hash_from_dict(data, length=DEFAULT_HASH_LENGTH)
    
    def prepare_base_dir(self, base: Path) -> Path:
        base_id = f"base_{self.get_base_hash()}"
        base_dir = base / base_id
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_id, base_dir
    
class TightBindingSystem:
    def __init__(self, config: PhysicsConfig):
        self.config: PhysicsConfig = config
        self.removed_sites: set[tuple[NonNegInt, NonNegInt]] = set()
        
    @property
    def num_sites(self) -> NonNegInt:
        return self.config.nx * self.config.ny - len(self.removed_sites)
    
    @property
    def geometry_state(self) -> dict[str, Any]:
        data = {
            "nx": self.config.nx,
            "ny": self.config.ny,
            "removed": [list(site) for site in sorted(self.removed_sites)],
        }
        return data
    
    def get_geometry_hash(self) -> str:
        return stable_hash_from_dict(self.geometry_state, length=DEFAULT_HASH_LENGTH)
    
    def prepare_geometry_dir(self, base: Path) -> Path:
        geo_id = f"geo_{self.get_geometry_hash()}"
        geo_dir = base / geo_id
        geo_dir.mkdir(parents=True, exist_ok=True)
        return geo_id, geo_dir
    
    def remove_site(self, coord: tuple[NonNegInt,NonNegInt]) -> None:
        x, y = coord
        if x < 0 or y < 0:
            raise ValueError("Coordinates must be non-negative")
        self.removed_sites.add(coord)
        
    def build_hamiltonian_dense(self) -> NDArray[np.complex128]: #ToDo: implement correct Hamiltonian
        rng = np.random.default_rng(self.config.seed)
        n_sites = self.num_sites
        rand_matrix_dense = rng.standard_normal((n_sites, n_sites)) + 1.j * rng.standard_normal((n_sites, n_sites))
        hamiltonian_dense = get_hermitian_part(rand_matrix_dense)
        return hamiltonian_dense
    
    def solve(self) -> NDArray[np.float64]:  #ToDo: implement this correctly
        rng = np.random.default_rng(self.config.seed)
        return rng.normal(size=self.config.nx*self.config.ny)

def main() -> None: 
    ...
    # config_test: dict[str, Any] = {
    #     'nx': 3,
    #     'ny': 3,
    #     't1x': 1.0,
    #     't1y': 1.0,
    #     'mu': 1.0,
    #     'seed': 42,
    # }
    
    # model = TBConfig(**config_test)
    # print(model.get_hash(length = 12))
    
if __name__ == "__main__":
    main()