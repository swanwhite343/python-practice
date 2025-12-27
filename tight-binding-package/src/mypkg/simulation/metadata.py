from __future__ import annotations

import sys
import yaml
from pathlib import Path
import platform
import subprocess
import importlib.metadata as md
from importlib.metadata import PackageNotFoundError
from typing import Any

from .git import git_commit, git_describe, repo_state


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

import subprocess
from pathlib import Path

def git_diff_text() -> str | None:
    """Return `git diff` output, or None if git is unavailable."""
    try:
        return subprocess.check_output(["git", "diff"], text=True)
    except Exception:
        return None

def git_diff_cached_text() -> str | None:
    """Return staged diff (`git diff --cached`)."""
    try:
        return subprocess.check_output(["git", "diff", "--cached"], text=True)
    except Exception:
        return None

def save_git_diff(run_dir: Path) -> None:
    """Save working tree and staged diffs into run_dir."""
    wd = git_diff_text()
    if wd:
        (run_dir / "git_diff.patch").write_text(wd, encoding="utf-8")

    st = git_diff_cached_text()
    if st:
        (run_dir / "git_diff_cached.patch").write_text(st, encoding="utf-8")
