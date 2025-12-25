import subprocess

def repo_state() -> tuple[bool | None, str]:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return bool(out.strip()), "ok"
    except Exception as e:
        return None, f"git unavailable: {e}"
    
def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None
    
def git_describe() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--dirty"],
            text=True,
            stderr=subprocess.DEVNULL,  # optional: silence Git’s message
        ).strip()
    except Exception:
        return None

        