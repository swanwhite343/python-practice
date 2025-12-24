import hashlib
import json
from typing import Any, Mapping, Final

# Contants
DEFAULT_HASH_LENGTH: Final[int] = 12

# Functions

def stable_hash_from_dict(
    d: Mapping[str, Any],
    length: int = DEFAULT_HASH_LENGTH,
    verbose: bool = False
) -> str:
    
    if length <= 6 or length > 32:
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

# Main

def main() -> None:
    test_dict: dict[str, int] = {"cat": 2, "dog": 3}
    print(stable_hash_from_dict(test_dict, verbose=True))
    
if __name__ == "__main__":
    main()