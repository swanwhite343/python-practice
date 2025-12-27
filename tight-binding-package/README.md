(In progress. This is for Mac users.)

### git clone

### Setting up

1. Create and activate a virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

    (Optional) Exact snapshot
    ```bash
    pip install -r requirements.lock
    ```

## Setup (reproducible dev environment)

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate            # macOS/Linux
python -m pip install --upgrade pip
pip install -e ".[dev]" -c requirements-lock.txt

python scripts/<script>.py --config <config>.yaml
```

## Project structure (what goes where)

This repository follows a separation-of-concerns layout so that lattice geometry, physical parameters, Hamiltonian construction, numerical solvers, and run orchestration can evolve independently.

### `src/mypkg/geometry/`
**Lattice geometry only.**
- Lattice shape/size (nx, ny), boundary conditions, defects (removed sites)
- Global↔active index maps
- Neighbor queries and bond enumeration `iter_bonds(kind)`
- No local Hilbert space (spin/orbital) and no TB parameters

### `src/mypkg/physics/`
**Local Hilbert space + tight-binding parameters.**
- Local basis config: `n_orb`, `n_spin`, ordering convention
- TB parameters: onsite/hopping matrices (by bond kind)
- Optional external fields (e.g., AB flux, Zeeman)
- Does not know about a specific lattice layout

### `src/mypkg/builder/`
**Hamiltonian construction layer.**
- Turns `(geometry + physics)` into a Hamiltonian representation
- Uses `geometry.iter_bonds(kind)` and `physics.params`
- Starts with dense implementations for testing, then moves to sparse (COO→CSR)
- No file I/O, no run directories

### `src/mypkg/solver/`
**Numerical solvers and solver configuration.**
- Computation settings: `eta`, energy grid, equilibrium `(mu, T)`, etc.
- Functions/classes that compute observables from a Hamiltonian (e.g., spectra, Green’s functions, NEGF quantities)
- Should not do file I/O or manage results directories

### `src/mypkg/simulation/`
**Run orchestration (experiment driver).**
- Reads YAML configs / CLI args
- Cross-checks consistency (e.g., hopping keys vs geometry, AB flux support)
- Creates `run_dir` paths based on stable hashes
- Saves outputs and metadata, handles “skip existing results” logic
- Calls builder + solver; simulation itself should not contain core math

### `src/mypkg/linalg/`
**Linear algebra utilities and matrix representations.**
- Helpers like “Hermitian part”, conversions, small linear-algebra routines
- Data models for matrices (e.g., PairMatrix) and conversion to NumPy arrays

### `src/mypkg/types/`
**Lightweight shared types only.**
- Simple scalar types (Seed, LatticeSide, etc.), small enums, NewType indices
- Avoid heavy imports here (NumPy, simulation code, etc.) to prevent cycles

### `src/mypkg/utils/`
**Generic utilities.**
- Stable hashing, YAML loading helpers, small non-domain-specific helpers
- If a helper is run-specific (metadata, run directory rules), prefer `simulation/`

## Why this layout (R&D standard)
This is a common R&D pattern: separate the “scientific model” (geometry/physics), the “construction” step (builder), the “numerics” (solver), and the “execution workflow” (simulation). It reduces circular dependencies, improves testability, and makes it easier to add new lattices or solvers without rewriting everything.
