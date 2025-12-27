import argparse

def build_simulation_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("config_file")
    p.add_argument("--allow_dirty", action="store_true",
                   help="Proceed even if git state is unknown/dirty")
    p.add_argument("--force_rerun", action="store_true",
                   help="Overwrite artifacts even if commits differ or files exist")
    return p

def parse_simulation_args():
    return build_simulation_parser().parse_args()