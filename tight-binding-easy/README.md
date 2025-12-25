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

### Simulations

```bash
# git status sensitive
python run_simulation.py <path-to-base-config-yaml>

# git status insensitive
python run_simulation.py <path-to-base-config-yaml> --allow_dirty
```