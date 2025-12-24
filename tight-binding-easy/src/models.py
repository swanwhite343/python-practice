from pydantic import BaseModel
from typing import Any
from .utils import stable_hash_from_dict
from .types import LatticeSide, Seed, HashLength, HoppingAmp, OnsiteChem

class TBConfig(BaseModel):
    nx: LatticeSide
    ny: LatticeSide
    t1x: HoppingAmp
    t1y: HoppingAmp
    mu:  OnsiteChem
    seed: Seed
    
    def get_hash(self, length: HashLength) -> str:
        data = self.model_dump(mode="json")
        return stable_hash_from_dict(data, length=length)
    
def main() -> None:
    config_test: dict[str, Any] = {
        'nx': 3,
        'ny': 3,
        't1x': 1.0,
        't1y': 1.0,
        'mu': 1.0,
        'seed': 42,
    }
    
    model = TBConfig(**config_test)
    print(model.get_hash(length = 12))
    
if __name__ == "__main__":
    main()