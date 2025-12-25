import argparse
import yaml
import pandas as pd
from pydantic import Field
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from .models import PhysicsConfig, TightBindingSystem
from .utils import load_raw
from .metadata import collect_metadata, save_metadata, load_metadata
from .path import CONFIGS_DIR, RESULTS_DIR

@dataclass
class Simulation:
    # Required
    args: argparse.Namespace
    # Optional
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    t0: float = Field(default_factory=perf_counter)
    raw: dict = Field(init=False)
    base_config: PhysicsConfig = Field(init=False)
    base_id: str = Field(init=False)
    base_dir: Path = Field(init=False)
    tb_system: TightBindingSystem = Field(init=False)
    geo_id: str = Field(init=False)
    geo_dir: Path = Field(init=False)
    meta_path: Path = Field(init=False)
    meta: dict = Field(init=False)
    existing_meta: dict = Field(init=False)

    def __post_init__(self):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        self.raw = load_raw(CONFIGS_DIR / self.args.config_file)
        self.base_config = PhysicsConfig(**self.raw)
        self.base_id, self.base_dir = self.base_config.prepare_base_dir(RESULTS_DIR)
        self.tb_system = TightBindingSystem(self.base_config)
        self.geo_id, self.geo_dir = self.tb_system.prepare_geometry_dir(base=self.base_dir)
        self.meta_path = self.geo_dir / "metadata.yaml"
        self.meta = collect_metadata()
        self.existing_meta = load_metadata(self.meta_path)
        self.base_path = self.geo_dir / "base_config.yaml"
        self.geo_path = self.geo_dir / "geometry_config.yaml"

    def artifact_csv_path(self, name: str) -> Path:
        return self.geo_dir / f"{name}.csv"
    
    def save_series(self, name: str, values) -> None:
        path = self.artifact_csv_path(name)
        pd.Series(values).to_csv(path, index=False)
    
    def should_skip(self, name: str, suffix: str = ".csv") -> tuple[Path, bool]:
        path = self.artifact_path(name, suffix)
        skip = path.exists() and not self.args.force_rerun
        if skip:
            print(f"Skipping: {name} already exists at {path}")
        return path, skip
    
    # To prevent blindly overruning the preexisting results
    def guard_commits(self):
        stored = self.existing_meta.get("git_commit")
        curr = self.meta.get("git_commit")
        if stored and curr and stored != curr and not self.args.force_rerun:
            raise SystemExit(
                f"Existing results are from {stored}; you’re on {curr}. "
                "Use --force-rerun to overwrite."
            )
 
    def save_metadata(self):
        self.meta["run"] = {
            "started_at": self.started_at.isoformat(),
            "duration_sec": perf_counter() - self.t0,
            "args": vars(self.args),
            "allow_dirty": self.args.allow_dirty,
            "force_rerun": self.args.force_rerun,
            "base_id": self.base_id,
            "geo_id": self.geo_id,
        }
        save_metadata(self.meta_path, self.meta)

    def save_configs(self):
        (self.base_path).write_text(yaml.safe_dump(self.raw), encoding="utf-8")
        (self.geo_path).write_text(yaml.safe_dump(self.tb_system.geometry_state), encoding="utf-8")