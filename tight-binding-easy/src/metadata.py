import sys
import yaml
from pathlib import Path 
import platform
import subprocess
import importlib.metadata as md
from typing import Any
from .git_utils import git_commit, git_describe, repo_state

def collect_metadata() -> dict[str, Any]:
    return {
        "git_commit": git_commit() or "unknown",
        "git_describe": git_describe() or "unknown",
        "git_dirty": repo_state()[0],
        "python_version": sys.version,
        "platform": platform.platform(),
        "packages": {
            "numpy": md.version("numpy"),
            "pydantic": md.version("pydantic"),
            "scipy": md.version("scipy"),
            "pandas": md.version("pandas"),
            "pyyaml": md.version("pyyaml"),
            "numba": md.version("numba"),
        },
    }
    
def load_metadata(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) if path.exists() else {}

def save_metadata(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

def current_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True
        ).strip()
    except Exception:
        return None