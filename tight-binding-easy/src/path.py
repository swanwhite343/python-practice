from typing import Final
from pathlib import Path

PROJECT_ROOT: Final[str] = Path(__file__).resolve().parent.parent
CONFIGS_DIR: Final[str] = PROJECT_ROOT / "configs"
RESULTS_DIR: Final[str] = PROJECT_ROOT / "results"