import numpy as np
from pydantic import BaseModel
from typing import Any
from numpy.typing import NDArray
from .utils import stable_hash_from_dict, DEFAULT_HASH_LENGTH
from .types import LatticeSide, Seed, HashLength, HoppingAmp, OnsiteChem

class PhysicsConfig(BaseModel):
    nx: LatticeSide
    ny: LatticeSide
    t1x: HoppingAmp
    t1y: HoppingAmp
    mu:  OnsiteChem
    seed: Seed
    
    def get_hash(self, length: HashLength = DEFAULT_HASH_LENGTH) -> str:
        data = self.model_dump(mode="json")
        return stable_hash_from_dict(data, length=length)
    
class TightBindingSystem:
    def __init__(self, config: PhysicsConfig):
        self.config: PhysicsConfig = config
    
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