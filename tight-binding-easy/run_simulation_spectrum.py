import json
import yaml
import sys
from pathlib import Path
import pandas as pd
from typing import Final, Any
import numpy as np
import argparse
from datetime import datetime, timezone
from time import perf_counter

from src.utils import load_raw, should_skip_existing
from src.models import PhysicsConfig, TightBindingSystem
from src.git_utils import repo_state
from src.metadata import collect_metadata, save_metadata, load_metadata

PROJECT_ROOT: Final[str] = Path(__file__).resolve().parent
CONFIGS_DIR: Final[str] = PROJECT_ROOT / "configs"
RESULTS_DIR: Final[str] = PROJECT_ROOT / "results"

def parse_simulation_args():
    p = argparse.ArgumentParser()
    p.add_argument("config_file")
    p.add_argument("--allow_dirty",
                   action="store_true",
                   help="Proceed even if git state is unknown/dirty"
    )
    p.add_argument("--force-rerun",
                   action="store_true",
                   help="Overwrite artifacts even if commits differ or files exists")
    return p.parse_args()

def main() -> None:
    
    started_at = datetime.now(timezone.utc)
    t0 = perf_counter()
    
    args = parse_simulation_args()
    
    # Let the simulation run when either git is clean or --allow_dirty == True
    dirty, reason = repo_state()
    if dirty is None and not args.allow_dirty:
        raise SystemExit(f"Cannot determine git status ({reason}). Use --allow-dirty to proceed.")
    if dirty and not args.allow_dirty:
        raise SystemExit("Repo has uncommitted changes. Commit/stash or rerun with --allow-dirty.")
    
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load physical system's config from yaml
    raw = load_raw(CONFIGS_DIR / args.config_file)
    # Parse yaml data and then create the run directory for that base config
    base_config = PhysicsConfig(**raw)
    base_id, base_dir = base_config.prepare_base_dir(base=RESULTS_DIR)
    
    tb_system = TightBindingSystem(base_config)
    # Modify the geometry:
    # ... (ToDo)
    geo_id, geo_dir = tb_system.prepare_geometry_dir(base=base_dir)
    
    # Guard on the stored data
    meta_path = geo_dir / "metadata.yaml"
    existing_meta = load_metadata(meta_path)
    stored_commit = existing_meta.get("git_commit")
    current_meta = collect_metadata()  # includes git_commit/git_describe/git_dirty
    current_commit = current_meta.get("git_commit")
    
    if stored_commit and current_commit and stored_commit != current_commit and not args.force_rerun:
        print(f"Existing results are from {stored_commit}; you’re on {current_commit}. "
            "Use --force-rerun to overwrite.")
        return

    # Simulations (Closed system)
    hamiltonian = tb_system.build_hamiltonian_dense()
    
    # Spectrum
    spectrum_path = geo_dir / "spectrum.csv"
    if should_skip_existing(spectrum_path, "spectrum") and not args.force_rerun:
        return
    spectrum, _ = np.linalg.eigh(hamiltonian)
    pd.Series(spectrum).to_csv(spectrum_path, index=False)
    print(f"Saved: {base_id}/{geo_id}")
    
    # Save exact physical/geometric configs and metadata used
    current_meta["run"] = {
    "started_at": started_at.isoformat(),
    "duration_sec": perf_counter() - t0,
    "args": vars(args),
    "base_id": base_id,
    "geo_id": geo_id,
    }
    save_metadata(meta_path, current_meta)
    (geo_dir / "geometry_config.yaml").write_text(
        yaml.safe_dump(tb_system.geometry_state),
        encoding="utf-8",
    )
    (geo_dir / "base_config.yaml").write_text(
        yaml.safe_dump(raw),
        encoding="utf-8"
    )
    
if __name__ == "__main__":
    main()