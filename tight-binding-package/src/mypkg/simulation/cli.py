from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class SimArgs:
    config_file: str
    allow_dirty: bool
    force_rerun: bool


def build_simulation_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, dest="config_file")
    p.add_argument("--allow_dirty", action="store_true")
    p.add_argument("--force_rerun", action="store_true")
    return p


def parse_simulation_args() -> SimArgs:
    ns = build_simulation_parser().parse_args()
    return SimArgs(
        config_file=ns.config_file,
        allow_dirty=ns.allow_dirty,
        force_rerun=ns.force_rerun,
    )