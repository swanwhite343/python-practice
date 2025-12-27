from __future__ import annotations

import argparse
import logging
import yaml
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter

from ..utils.core import load_raw
from ..simulation.metadata import collect_metadata, save_metadata, load_metadata
from ..paths import CONFIGS_DIR, RESULTS_DIR

from .configs import SimulationConfig

log = logging.getLogger(__name__)


@dataclass
class Simulation:
    args: argparse.Namespace

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    t0: float = field(default_factory=perf_counter)

    raw: dict = field(init=False)
    cfg: SimulationConfig = field(init=False)

    run_dir: Path = field(init=False)
    meta: dict = field(init=False)
    meta_path: Path = field(init=False)
    existing_meta: dict = field(init=False)

    def __post_init__(self):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        self.raw = load_raw(CONFIGS_DIR / self.args.config_file)

        # Validate + cross-check in one go
        self.cfg = SimulationConfig.model_validate(self.raw)

        geo = self.cfg.geo_hash()
        phys = self.cfg.phys_hash()
        solv = self.cfg.solver_hash()

        self.run_dir = RESULTS_DIR / f"geo_{geo}" / f"phys_{phys}" / f"solv_{solv}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.meta_path = self.run_dir / "metadata.yaml"
        self.meta = collect_metadata()
        self.existing_meta = load_metadata(self.meta_path)

    def artifact_path(self, name: str, suffix: str = "csv") -> Path:
        return self.run_dir / f"{name}.{suffix}"

    def save_series(self, name: str, values) -> None:
        path = self.artifact_path(name)
        pd.Series(values).to_csv(path, index=False)
        log.info(f"Finished: wrote {name} to {path}")

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
            log.error(msg)
            raise SystemExit(msg)

    def save_metadata(self) -> None:
        self.meta["run"] = {
            "started_at": self.started_at.isoformat(),
            "duration_sec": perf_counter() - self.t0,
            "args": vars(self.args),
            "allow_dirty": self.args.allow_dirty,
            "force_rerun": self.args.force_rerun,
            "phys_hash": self.cfg.phys_hash(),
            "geo_hash": self.cfg.geo_hash(),
            "solver_hash": self.cfg.solver_hash(),
            "run_dir": str(self.run_dir),
        }
        save_metadata(self.meta_path, self.meta)
        log.info(f"Finished: wrote metadata to {self.meta_path}")

    def save_config(self) -> None:
        config_path = self.run_dir / "config.yaml"
        config_path.write_text(yaml.safe_dump(self.raw), encoding="utf-8")
        log.info(f"Finished: wrote base config to {config_path}")
