import json
import yaml
import sys
from pathlib import Path
import pandas as pd
from typing import Final
import numpy as np

from src.utils import load_raw, should_skip_existing
from src.models import PhysicsConfig, TightBindingSystem

PROJECT_ROOT: Final[str] = Path(__file__).resolve().parent
CONFIGS_DIR: Final[str] = PROJECT_ROOT / "configs"
RESULTS_DIR: Final[str] = PROJECT_ROOT / "results"

def main(config_file: str) -> None:
    
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load physical system's config from yaml
    raw = load_raw(CONFIGS_DIR / config_file)
    # Parse yaml data and then create the run directory for that base config
    base_config = PhysicsConfig(**raw)
    base_id, base_dir = base_config.prepare_base_dir(base=RESULTS_DIR)
    
    # Modify the base_config
    
    # impurity_sets = [
    #     [{"x": 2, "y": 2, "strength": 0.1}],
    #     [{"x": 2, "y": 2, "strength": 1.}],
    # ]
    
    impurity = {"x": 2, "y": 2, "strength": 0.1} # ToDo: from a file
    
    tb_system = TightBindingSystem(base_config)
    geo_id, geo_dir = tb_system.prepare_geometry_dir(base=base_dir)
    
    # Simulations (Closed system)
    hamiltonian = tb_system.build_hamiltonian_dense()
    
    # Spectrum
    spectrum_path = geo_dir / "spectrum.csv"
    if should_skip_existing(spectrum_path, "spectrum"):
        return
    spectrum, _ = np.linalg.eigh(hamiltonian)
    pd.Series(spectrum).to_csv(spectrum_path, index=False)
    print(f"Saved: {base_id}/{geo_id}")
    
    # Save exact physical system's config used
    (geo_dir / "base_config.yaml").write_text(
        yaml.safe_dump(raw),
        encoding="utf-8"
    )
    (geo_dir / "geometry_config.yaml").write_text(
        yaml.safe_dump(tb_system.geometry_state),
        encoding="utf-8"
    )
    
if __name__ == "__main__":
    main(sys.argv[1])