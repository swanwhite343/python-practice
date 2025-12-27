from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasHash(Protocol):
    def get_hash(self, length: int = ...) -> str: ...


@dataclass(frozen=True)
class RunLayout:
    """
    Path/layout helper for simulation runs.

    This module does NOT assume a repository root.
    Pass configs_dir/results_dir from the entry script (e.g., scripts/run_*.py).
    """
    configs_dir: Path
    results_dir: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> RunLayout:
        """
        Convenience constructor for the common repo layout:
          <root>/configs
          <root>/results
        """
        root = project_root.resolve()
        return cls(configs_dir=root / "configs", results_dir=root / "results")

    def ensure_base_dirs(self) -> None:
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_dir(
        self,
        geo: HasHash,
        phys: HasHash,
        solver: HasHash | None = None,
        *,
        length: int = 12,
        mkdir: bool = True,
    ) -> Path:
        """
        Standard run directory layout:
          results_dir / geo_<hash> / phys_<hash> [/ solv_<hash>]
        """
        geo_id = geo.get_hash(length=length)
        phys_id = phys.get_hash(length=length)

        dir_path = self.results_dir / f"geo_{geo_id}" / f"phys_{phys_id}"

        if solver is not None:
            solver_id = solver.get_hash(length=length)
            dir_path = dir_path / f"solv_{solver_id}"

        if mkdir:
            dir_path.mkdir(parents=True, exist_ok=True)

        return dir_path