#!/usr/bin/env python3
"""hakudokai_git_guard.py — Git safety guard for multi-agent-shogun.

Implements Axis 6 (git persistence automation) from the R-1 audit:
  1. Block unsafe git operations (pre-execution check)
  2. Periodic git pull (auto-sync)
  3. WIP intermediate commits (auto-save during long tasks)
  4. Push-forget detection (unpushed commits alert)
  5. Conflict early detection

Usage:
  python3 hakudokai_git_guard.py check-command "git reset --hard"
  python3 hakudokai_git_guard.py auto-pull
  python3 hakudokai_git_guard.py wip-commit
  python3 hakudokai_git_guard.py check-unpushed
  python3 hakudokai_git_guard.py check-conflicts
  python3 hakudokai_git_guard.py daemon          # Run all periodic checks
  python3 hakudokai_git_guard.py status           # Show current git safety status
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
HEALTH_FILE = Path("/tmp/hakudokai_git_guard_health.json")
LOG_FILE = Path("/tmp/hakudokai_git_guard.log")

# Daemon intervals (seconds)
PULL_INTERVAL = 300       # 5 min
WIP_INTERVAL = 600        # 10 min
UNPUSHED_INTERVAL = 900   # 15 min
CONFLICT_INTERVAL = 300   # 5 min

# WIP commit thresholds
WIP_MIN_CHANGES = 3       # Minimum changed files to trigger WIP commit
WIP_MAX_UNCOMMITTED_MIN = 30  # Minutes of uncommitted changes before WIP

# ============================================================
# Unsafe command detection
# ============================================================

BLOCKED_PATTERNS = [
    # Tier 1: ABSOLUTE BAN (from CLAUDE.md D001-D008)
    (r"git\s+push\s+.*--force(?!\s*-with-lease)\b", "D003: force push without --force-with-lease"),
    (r"git\s+push\s+-f\b", "D003: force push shorthand"),
    (r"git\s+reset\s+--hard\b", "D004: git reset --hard destroys uncommitted work"),
    (r"git\s+checkout\s+--\s*\.", "D004: git checkout -- . destroys uncommitted work"),
    (r"git\s+checkout\s+--\s+\.", "D004: git checkout -- . destroys uncommitted work"),
    (r"git\s+restore\s+\.", "D004: git restore . destroys uncommitted work"),
    (r"git\s+restore\s+--staged\s+--worktree\s+\.", "D004: git restore destroys uncommitted work"),
    (r"git\s+clean\s+-f", "D004: git clean -f deletes untracked files"),
    (r"rm\s+-rf\s+/(?!\S)", "D001: rm -rf / destroys system"),
    (r"rm\s+-rf\s+/mnt/[cd]/(?!Users/User/projects/)", "D002: rm -rf outside project tree"),
    (r"rm\s+-rf\s+/home/", "D001: rm -rf /home destroys home directory"),
    (r"rm\s+-rf\s+~", "D001: rm -rf ~ destroys home directory"),
]

# Patterns that are safe exceptions (allowlist)
SAFE_PATTERNS = [
    r"git\s+push\s+--force-with-lease",  # Safe alternative to force push
    r"git\s+clean\s+-n",                  # Dry run is safe
    r"git\s+clean\s+--dry-run",           # Dry run is safe
]

# Dangerous path patterns (WSL2-specific)
DANGEROUS_PATHS = [
    r"/mnt/c/Windows",
    r"/mnt/c/Users/[^/]+/AppData",
    r"/mnt/c/Program\s+Files",
    r"/mnt/d/",
]


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, file=sys.stderr)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run_git(*args, timeout=10) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + list(args),
        capture_output=True, cwd=PROJECT_ROOT, timeout=timeout
    )


def update_health(status: str, **extra):
    data = {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        **extra,
    }
    try:
        with open(HEALTH_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# ============================================================
# 1. check-command: Block unsafe git/shell operations
# ============================================================

def check_command(cmd: str) -> tuple[bool, str]:
    """Check if a command is safe to execute.
    Returns (is_safe, reason).
    """
    cmd_normalized = cmd.strip()

    # Check safe patterns first (allowlist)
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, cmd_normalized, re.IGNORECASE):
            return True, "Allowlisted safe pattern"

    # Check blocked patterns
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, cmd_normalized, re.IGNORECASE):
            return False, reason

    # Check dangerous paths in rm/mv/cp commands
    if re.search(r"\b(rm|mv|cp)\b", cmd_normalized):
        for path_pattern in DANGEROUS_PATHS:
            if re.search(path_pattern, cmd_normalized):
                return False, f"Dangerous path detected: {path_pattern}"

    # Check if rm -rf targets are within project tree
    rm_match = re.search(r"rm\s+-rf\s+(\S+)", cmd_normalized)
    if rm_match:
        target = rm_match.group(1)
        try:
            resolved = Path(target).resolve()
            if not str(resolved).startswith(str(PROJECT_ROOT)):
                return False, f"D002: rm -rf target '{target}' is outside project tree"
        except Exception:
            return False, f"Cannot resolve path '{target}', blocking for safety"

    return True, "OK"


# ============================================================
# 2. auto-pull: Periodic git pull with safety checks
# ============================================================

def auto_pull() -> bool:
    """Pull latest changes if safe to do so."""
    # Check for uncommitted changes
    status = run_git("status", "--porcelain", "-z")
    if status.stdout.strip():
        dirty_files = [f for f in status.stdout.decode().split("\0") if f.strip()]
        count = len(dirty_files)
        log(f"auto-pull: SKIPPED — {count} uncommitted changes. Stash or commit first.")
        return False

    # Check current branch
    branch = run_git("rev-parse", "--abbrev-ref", "HEAD")
    branch_name = branch.stdout.decode().strip()
    if branch_name != "main":
        log(f"auto-pull: SKIPPED — on branch '{branch_name}', not main")
        return False

    # Fetch
    fetch = run_git("fetch", "origin", timeout=30)
    if fetch.returncode != 0:
        log(f"auto-pull: fetch failed: {fetch.stderr.decode().strip()}")
        return False

    # Check if behind
    local = run_git("rev-parse", "HEAD").stdout.decode().strip()
    remote = run_git("rev-parse", "origin/main").stdout.decode().strip()

    if local == remote:
        log("auto-pull: already up to date")
        return True

    # Check for divergence
    merge_base = run_git("merge-base", "HEAD", "origin/main").stdout.decode().strip()
    if merge_base != local:
        log("auto-pull: SKIPPED — local and remote have diverged. Manual merge required.")
        _notify("git_guard_diverge", "ローカルとリモートが分岐しています。手動マージが必要です。")
        return False

    # Safe to pull (fast-forward only)
    pull = run_git("pull", "--ff-only", "origin", "main", timeout=30)
    if pull.returncode == 0:
        new_head = run_git("rev-parse", "--short", "HEAD").stdout.decode().strip()
        log(f"auto-pull: updated to {new_head}")
        return True
    else:
        log(f"auto-pull: pull failed: {pull.stderr.decode().strip()}")
        return False


# ============================================================
# 3. wip-commit: Intermediate WIP commits
# ============================================================

def wip_commit() -> bool:
    """Create a WIP commit if there are enough uncommitted changes for long enough."""
    status = run_git("status", "--porcelain")
    if not status.stdout.strip():
        return False

    lines = [l for l in status.stdout.decode().strip().split("\n") if l.strip()]
    if len(lines) < WIP_MIN_CHANGES:
        log(f"wip-commit: only {len(lines)} changes, below threshold ({WIP_MIN_CHANGES})")
        return False

    # Check how long since last commit
    last_commit_time = run_git("log", "-1", "--format=%ct")
    if last_commit_time.returncode != 0:
        return False

    last_ts = int(last_commit_time.stdout.decode().strip())
    elapsed_min = (time.time() - last_ts) / 60

    if elapsed_min < WIP_MAX_UNCOMMITTED_MIN:
        log(f"wip-commit: only {elapsed_min:.0f}min since last commit, below threshold ({WIP_MAX_UNCOMMITTED_MIN}min)")
        return False

    # Create WIP commit
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"wip: auto-save {len(lines)} files ({now})"

    # Stage tracked files only (don't add untracked)
    run_git("add", "-u")
    commit = run_git("commit", "-m", msg)

    if commit.returncode == 0:
        short_hash = run_git("rev-parse", "--short", "HEAD").stdout.decode().strip()
        log(f"wip-commit: created {short_hash} — {msg}")
        return True
    else:
        log(f"wip-commit: commit failed: {commit.stderr.decode().strip()}")
        return False


# ============================================================
# 4. check-unpushed: Detect unpushed commits
# ============================================================

def check_unpushed() -> list[str]:
    """Check for commits not yet pushed to origin/main."""
    result = run_git("log", "--oneline", "origin/main..HEAD")
    if result.returncode != 0:
        log("check-unpushed: failed to compare with origin/main")
        return []

    commits = [l for l in result.stdout.decode().strip().split("\n") if l.strip()]
    if commits:
        # Check age of oldest unpushed commit
        oldest = run_git("log", "--format=%ct", "origin/main..HEAD")
        if oldest.stdout.strip():
            timestamps = oldest.stdout.decode().strip().split("\n")
            oldest_ts = int(timestamps[-1])
            age_hours = (time.time() - oldest_ts) / 3600

            if age_hours > 1:
                log(f"check-unpushed: WARNING — {len(commits)} unpushed commits, oldest {age_hours:.1f}h ago")
                _notify("git_guard_unpushed",
                        f"push忘れ検知: {len(commits)}件のコミットが{age_hours:.1f}時間未pushです。")
            else:
                log(f"check-unpushed: {len(commits)} unpushed commits ({age_hours:.1f}h) — still fresh")
    else:
        log("check-unpushed: all commits pushed")

    return commits


# ============================================================
# 5. check-conflicts: Early conflict detection
# ============================================================

def check_conflicts() -> list[str]:
    """Detect potential merge conflicts by dry-run merge."""
    # Fetch latest
    run_git("fetch", "origin", timeout=30)

    local = run_git("rev-parse", "HEAD").stdout.decode().strip()
    remote = run_git("rev-parse", "origin/main").stdout.decode().strip()

    if local == remote:
        return []

    # Check merge base
    merge_base = run_git("merge-base", "HEAD", "origin/main")
    if merge_base.returncode != 0:
        return []

    base = merge_base.stdout.decode().strip()
    if base == remote:
        # Remote is behind local, no conflict possible
        return []
    if base == local:
        # Local is behind remote, fast-forward possible, no conflict
        return []

    # Diverged — check which files changed on both sides
    local_changes = run_git("diff", "--name-only", f"{base}..HEAD")
    remote_changes = run_git("diff", "--name-only", f"{base}..origin/main")

    local_files = set(local_changes.stdout.decode().strip().split("\n")) if local_changes.stdout.strip() else set()
    remote_files = set(remote_changes.stdout.decode().strip().split("\n")) if remote_changes.stdout.strip() else set()

    conflicts = sorted(local_files & remote_files)
    if conflicts:
        log(f"check-conflicts: POTENTIAL CONFLICTS in {len(conflicts)} files: {', '.join(conflicts[:5])}")
        _notify("git_guard_conflict",
                f"コンフリクト危険: {len(conflicts)}ファイルがローカル・リモート両方で変更されています: {', '.join(conflicts[:3])}")
    else:
        log("check-conflicts: diverged but no overlapping files")

    return conflicts


# ============================================================
# Notification helper
# ============================================================

def _notify(topic: str, message: str):
    """Send ntfy notification via escalation.py."""
    escalation = SCRIPT_DIR / "hakudokai_escalation.py"
    if escalation.exists():
        try:
            subprocess.run(
                [sys.executable, str(escalation), "notify",
                 "--level", "L3a", "--summary", message],
                capture_output=True, timeout=10
            )
        except Exception:
            pass


# ============================================================
# status: Show current git safety status
# ============================================================

def show_status():
    """Print a summary of git safety status."""
    print("=== Git Guard Status ===\n")

    # Branch
    branch = run_git("rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip()
    head = run_git("rev-parse", "--short", "HEAD").stdout.decode().strip()
    print(f"Branch: {branch} ({head})")

    # Uncommitted changes
    status = run_git("status", "--porcelain")
    changes = [l for l in status.stdout.decode().strip().split("\n") if l.strip()]
    print(f"Uncommitted changes: {len(changes)}")

    # Last commit age
    last_ts = run_git("log", "-1", "--format=%ct")
    if last_ts.stdout.strip():
        age_min = (time.time() - int(last_ts.stdout.decode().strip())) / 60
        print(f"Last commit: {age_min:.0f} min ago")

    # Unpushed
    unpushed = run_git("log", "--oneline", "origin/main..HEAD")
    unpushed_lines = [l for l in unpushed.stdout.decode().strip().split("\n") if l.strip()]
    print(f"Unpushed commits: {len(unpushed_lines)}")

    # Divergence
    local = run_git("rev-parse", "HEAD").stdout.decode().strip()
    remote = run_git("rev-parse", "origin/main").stdout.decode().strip()
    if local == remote:
        print("Sync status: UP TO DATE")
    else:
        merge_base = run_git("merge-base", "HEAD", "origin/main").stdout.decode().strip()
        if merge_base == remote:
            print("Sync status: LOCAL AHEAD")
        elif merge_base == local:
            print("Sync status: LOCAL BEHIND")
        else:
            print("Sync status: DIVERGED (potential conflicts)")

    # Health file
    if HEALTH_FILE.exists():
        try:
            with open(HEALTH_FILE) as f:
                health = json.load(f)
            print(f"\nDaemon: {health.get('status', 'unknown')} (last: {health.get('timestamp', '?')})")
        except Exception:
            print("\nDaemon: health file corrupt")
    else:
        print("\nDaemon: not running (no health file)")


# ============================================================
# daemon: Run all periodic checks
# ============================================================

def daemon():
    """Main daemon loop running all periodic checks."""
    log("git_guard daemon starting")
    update_health("running")

    last_pull = 0
    last_wip = 0
    last_unpushed = 0
    last_conflict = 0

    try:
        while True:
            now = time.time()

            if now - last_pull >= PULL_INTERVAL:
                try:
                    auto_pull()
                except Exception as e:
                    log(f"auto-pull error: {e}")
                last_pull = now

            if now - last_wip >= WIP_INTERVAL:
                try:
                    wip_commit()
                except Exception as e:
                    log(f"wip-commit error: {e}")
                last_wip = now

            if now - last_unpushed >= UNPUSHED_INTERVAL:
                try:
                    check_unpushed()
                except Exception as e:
                    log(f"check-unpushed error: {e}")
                last_unpushed = now

            if now - last_conflict >= CONFLICT_INTERVAL:
                try:
                    check_conflicts()
                except Exception as e:
                    log(f"check-conflicts error: {e}")
                last_conflict = now

            update_health("running",
                          last_pull=last_pull,
                          last_wip=last_wip,
                          last_unpushed=last_unpushed,
                          last_conflict=last_conflict)

            time.sleep(30)

    except KeyboardInterrupt:
        log("git_guard daemon stopped (SIGINT)")
        update_health("stopped")
    except Exception as e:
        log(f"git_guard daemon crashed: {e}")
        update_health("crashed", error=str(e))
        raise


# ============================================================
# Main
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    if action == "check-command":
        if len(sys.argv) < 3:
            print("Usage: git_guard.py check-command '<command>'", file=sys.stderr)
            sys.exit(1)
        cmd = " ".join(sys.argv[2:])
        is_safe, reason = check_command(cmd)
        if is_safe:
            print(f"SAFE: {reason}")
            sys.exit(0)
        else:
            print(f"BLOCKED: {reason}", file=sys.stderr)
            log(f"BLOCKED command: {cmd} — {reason}")
            sys.exit(1)

    elif action == "auto-pull":
        ok = auto_pull()
        sys.exit(0 if ok else 1)

    elif action == "wip-commit":
        ok = wip_commit()
        sys.exit(0 if ok else 1)

    elif action == "check-unpushed":
        commits = check_unpushed()
        if commits:
            for c in commits:
                print(c)
        sys.exit(0)

    elif action == "check-conflicts":
        conflicts = check_conflicts()
        if conflicts:
            for f in conflicts:
                print(f)
            sys.exit(1)
        sys.exit(0)

    elif action == "status":
        show_status()

    elif action == "daemon":
        daemon()

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
