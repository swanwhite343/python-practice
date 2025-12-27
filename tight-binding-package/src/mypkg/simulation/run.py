from __future__ import annotations

import logging
import yaml
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from ..utils.core import load_raw
from ..geometry.types import FreezableGeometryLike, Bond
from .configs import SimulationConfig
from .paths import RunLayout
from .metadata import collect_metadata, save_metadata, load_metadata
from .cli import SimArgs
from .metadata import save_git_diff

log = logging.getLogger(__name__)


@dataclass
class Simulation:
    args: SimArgs
    layout: RunLayout

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    t0: float = field(default_factory=perf_counter)

    raw: dict[str, Any] = field(init=False)
    cfg: SimulationConfig = field(init=False)

    geo: FreezableGeometryLike = field(init=False)
    run_dir: Path = field(init=False)

    meta_path: Path = field(init=False)
    meta: dict[str, Any] = field(init=False)
    existing_meta: dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        self.layout.ensure_base_dirs()

        # load config
        cfg_path = self.layout.configs_dir / self.args.config_file
        self.raw = load_raw(cfg_path)

        # validate + cross-check
        self.cfg = SimulationConfig.model_validate(self.raw)

        # build objects
        self.geo = self.cfg.build_geometry()
        phys = self.cfg.physics
        solv = self.cfg.solver

        # decide run_dir by hashes
        self.run_dir = self.layout.run_dir(self.geo, phys, solv)
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # metadata
        self.meta_path = self.run_dir / "metadata.yaml"
        self.meta = collect_metadata()
        self.existing_meta = load_metadata(self.meta_path)

    def artifact_path(self, name: str, suffix: str = "csv") -> Path:
        return self.run_dir / f"{name}.{suffix}"

    def save_series(self, name: str, values) -> None:
        path = self.artifact_path(name, "csv")
        pd.Series(values).to_csv(path, index=False)
        log.info(f"Wrote {name} -> {path}")

    def should_skip(self, name: str, suffix: str = "csv") -> bool:
        path = self.artifact_path(name, suffix)
        skip = path.exists() and not self.args.force_rerun
        if skip:
            log.info(f"Skipping: {name} already exists at {path}")
        return skip

    def guard_commits(self) -> None:
        stored = self.existing_meta.get("git_commit")
        curr = self.meta.get("git_commit")
        if stored and curr and stored != curr and not self.args.force_rerun:
            msg = (
                f"Existing results are from {stored}; you’re on {curr}. "
                "Use --force_rerun to overwrite."
            )
            raise SystemExit(msg)

    def save_metadata(self) -> None:
        self.meta["run"] = {
            "started_at": self.started_at.isoformat(),
            "duration_sec": perf_counter() - self.t0,
            "args": vars(self.args),
            "run_dir": str(self.run_dir),
            "geo_hash": self.geo.get_hash() if hasattr(self.geo, "get_hash") else None,
            "phys_hash": self.cfg.physics.get_hash(),
            "solver_hash": self.cfg.solver.get_hash(),
        }
        save_metadata(self.meta_path, self.meta)

        # --- add here: save git diff if dirty ---
        if self.meta.get("git_dirty", False):
            save_git_diff(self.run_dir)

    def save_config(self) -> None:
        (self.run_dir / "config.yaml").write_text(
            yaml.safe_dump(self.raw), encoding="utf-8"
        )
