import json
import yaml
import sys
from pathlib import Path
import pandas as pd
from typing import Final

from src.models import PhysicsConfig, TightBindingSystem

PROJECT_ROOT: Final[str] = Path(__file__).resolve().parent
CONFIGS_DIR: Final[str] = PROJECT_ROOT / "configs"
RESULTS_DIR: Final[str] = PROJECT_ROOT / "results"

def main(config_file: str) -> None:
    results_dir  = RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    
    # Load physical system's config from yaml
    with (CONFIGS_DIR / config_file).open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
        
    config = PhysicsConfig(**raw)
    
    run_id  = config.get_hash()
    run_dir = RESULTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    spectrum_path = run_dir / "spectrum.csv"
    if spectrum_path.exists():
        print(f"Skipping: Results for {run_id} already exists.")
        return
    
    # Save exact physical system's config used
    (run_dir / "config.yaml").write_text(
        yaml.safe_dump(raw),
        encoding="utf-8"
    )
    
    # Run (ToDo: implement this correctly)
    system   = TightBindingSystem(config)
    energies = system.solve()
    
    pd.Series(energies).to_csv(spectrum_path, index=False)
    print(f"Saved: {run_id}")
    
if __name__ == "__main__":
    main(sys.argv[1])