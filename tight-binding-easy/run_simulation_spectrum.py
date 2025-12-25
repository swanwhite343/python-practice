import pandas as pd
import numpy as np
import argparse

from src.git_utils import ensure_git_clean
from src.simulation import Simulation

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
    
    args = parse_simulation_args()
    ensure_git_clean(args.allow_dirty)
    
    run = Simulation(args)
    run.guard_commits()
    
    if run.should_skip("spectrum"):
        print("Spectrum exits. Skipping.")
        return

    # Simulations (Closed system)
    hamiltonian = run.tb_system.build_hamiltonian_dense()
    spectrum, _ = np.linalg.eigh(hamiltonian)
    run.save_series("spectrum", spectrum)
    run.save_metadata()
    run.save_configs()
    
    pd.Series(spectrum).to_csv(run.artifact_csv_path("spectrum"), index=False)

if __name__ == "__main__":
    main()