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
    
def ensure_git_clean(allow_dirty: bool) -> None:
    # Let the simulation run when either git is clean or --allow_dirty == True
    dirty, reason = repo_state()
    if dirty is None and not allow_dirty:
        raise SystemExit(f"Cannot determine git status ({reason}). Use --allow-dirty to proceed.")
    if dirty and not allow_dirty:
        raise SystemExit("Repo has uncommitted changes. Commit/stash or rerun with --allow-dirty.")