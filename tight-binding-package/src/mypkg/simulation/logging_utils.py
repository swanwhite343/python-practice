import logging
from pathlib import Path

def init_run_logger(log_path: Path, level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(  # configure root once
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )
    return logging.getLogger(__name__)

def setup_logging(dir_path: Path) -> logging.Logger:
    return init_run_logger(dir_path / "run.log")