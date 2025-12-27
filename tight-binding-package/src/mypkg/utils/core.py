import hashlib
import json
import yaml
from typing import Any, Mapping, Final
from pathlib import Path

import logging
log = logging.getLogger(__name__)

# Contants
DEFAULT_HASH_LENGTH: Final[int] = 12

# Functions

def stable_hash_from_dict(
    d: Mapping[str, Any],
    length: int = DEFAULT_HASH_LENGTH,
    verbose: bool = False
) -> str:
    
    if length < 6 or length > 32:
        raise ValueError("Hash length must be between 6 and 32.")
    
    payload = json.dumps(
        d,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    payload_bytes = payload.encode("utf-8")
    digest_full_sha256 = hashlib.sha256(payload_bytes)
    digest_full_hex = digest_full_sha256.hexdigest()
    digest_short_hex = digest_full_hex[:length]
    
    if verbose:
        print("=== DEBUG stable_hash_from_dict ===")
        print("input dict:", d)
        print("payload (json string):", payload)
        print("payload_bytes (utf-8):", payload_bytes)
        print("hash algo:", digest_full_sha256.name, "| digest_size:", digest_full_sha256.digest_size)
        print("sha256 hex digest (full):", digest_full_hex)
        print(f"sha256 hex digest (first {length}):", digest_short_hex)
        print("===================================")
              
    return digest_short_hex

# Load from yaml, and output it as dict
def load_raw(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        config_data = yaml.safe_load(file)
    
    if config_data is None:
        log.error("ValueError: Empty config")
        raise ValueError("Empty config")
    if not isinstance(config_data, dict):
        msg = f"Config root must be a mapping (dict), got {type(config_data).__name__}"
        log.error(msg)
        raise ValueError(msg)
    
    return config_data
    
# Check whether a simulation is already done
def should_skip_existing(path: Path, label: str | None = None) -> bool:
    label = label or path.stem
    if path.exists():
        log.info(f"Skipping: {label} already exists at {path}")
        return True
    return False