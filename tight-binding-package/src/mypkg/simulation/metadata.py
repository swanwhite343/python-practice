from __future__ import annotations

import sys
import yaml
from pathlib import Path
import platform
import subprocess
import importlib.metadata as md
from importlib.metadata import PackageNotFoundError
from typing import Any

from ..utils.git import git_commit, git_describe, repo_state


def _pkg_version(name: str) -> str:
    try:
        return md.version(name)
    except PackageNotFoundError:
        return "not-installed"


def collect_metadata() -> dict[str, Any]:
    dirty, _details = repo_state()

    return {
        "git_commit": git_commit() or "unknown",
        "git_describe": git_describe() or "unknown",
        "git_dirty": bool(dirty),
        "python_version": sys.version,
        "platform": platform.platform(),
        "packages": {
            "numpy": _pkg_version("numpy"),
            "pydantic": _pkg_version("pydantic"),
            "scipy": _pkg_version("scipy"),
            "pandas": _pkg_version("pandas"),
            "pyyaml": _pkg_version("pyyaml"),
            "numba": _pkg_version("numba"),
        },
    }


def load_metadata(p: Path) -> dict[str, Any]:
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_metadata(p: Path, data: dict[str, Any]) -> None:
    p.write_text(yaml.safe_dump(data), encoding="utf-8")


def current_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None
