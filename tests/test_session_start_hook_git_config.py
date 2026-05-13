"""tests/test_session_start_hook_git_config.py — cmd_inbox_reform cycle 17 (Rule 13).

Verifies the ``scripts/session_start_hook.sh`` extension that auto-sets
``git config --local user.name`` / ``user.email`` per session-start agent_id.

Trial matrix (= AC 黒田 P0 fix #4 整合、10 種 whitelist + 1 種 unknown = 11 trials):

    Whitelist (must set config):
        shogun, karo, gunshi,
        ashigaru1, ashigaru2, ashigaru3, ashigaru4,
        ashigaru5, ashigaru6, ashigaru7

    Unknown (must skip + warn):
        maeda (= persona alias for ashigaru4, not in whitelist)

SKIP=0 — no module-level or per-test skip directives. ``session_start_hook.sh``
is tracked in scripts/ and is always present alongside this test file.

Test approach:
  1. Per test, create a tmpdir with a fresh ``git init`` repo and copy the hook
     script into ``scripts/``.
  2. Stub ``tmux`` via a fake script on ``PATH`` that echoes the desired
     ``FAKE_AGENT_ID`` when asked for ``#{@agent_id}``.
  3. Set ``SESSION_START_HOOK_REPO_ROOT`` to the tmp repo so the hook's git
     config writes land in the tmp repo, not the real workspace.
  4. Run the hook end-to-end (always exits 0) and inspect the resulting
     ``--local`` config + stdout/log for the expected warning surface.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
HOOK = REPO_DIR / "scripts" / "session_start_hook.sh"

WHITELIST = [
    "shogun",
    "karo",
    "gunshi",
    "ashigaru1",
    "ashigaru2",
    "ashigaru3",
    "ashigaru4",
    "ashigaru5",
    "ashigaru6",
    "ashigaru7",
]
UNKNOWN_AGENT_ID = "maeda"  # persona alias for ashigaru4, intentionally non-whitelist


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "logs").mkdir()
    (repo / "queue" / "inbox").mkdir(parents=True)
    shutil.copy(HOOK, repo / "scripts" / "session_start_hook.sh")
    subprocess.run(["git", "init", "-q"], cwd=str(repo), check=True)
    return repo


@pytest.fixture
def fake_tmux(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    fake = bin_dir / "tmux"
    fake.write_text(textwrap.dedent("""\
        #!/usr/bin/env bash
        # Fake tmux for session_start_hook tests.
        # Returns ${FAKE_AGENT_ID:-} for @agent_id queries; empty for everything else.
        for arg in "$@"; do
            case "$arg" in
                *@agent_id*) echo "${FAKE_AGENT_ID:-}"; exit 0 ;;
            esac
        done
        echo ""
        exit 0
    """))
    fake.chmod(0o755)
    return bin_dir


def _run_hook(repo: Path, fake_tmux_dir: Path, agent_id: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PATH"] = f"{fake_tmux_dir}:{env['PATH']}"
    env["TMUX_PANE"] = "%0"
    env["FAKE_AGENT_ID"] = agent_id
    env["SESSION_START_HOOK_REPO_ROOT"] = str(repo)
    return subprocess.run(
        ["bash", str(repo / "scripts" / "session_start_hook.sh")],
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _git_local_get(repo: Path, key: str) -> str:
    cp = subprocess.run(
        ["git", "-C", str(repo), "config", "--local", "--get", key],
        capture_output=True,
        text=True,
    )
    return cp.stdout.strip()


# ---------------------------------------------------------------------------
# Tests — 10 whitelist trials
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("agent_id", WHITELIST)
def test_whitelist_agent_sets_local_user(agent_id: str, fake_repo: Path, fake_tmux: Path) -> None:
    """For each whitelist agent_id, hook must set --local user.name and user.email."""
    result = _run_hook(fake_repo, fake_tmux, agent_id)
    assert result.returncode == 0, f"hook must exit 0 for {agent_id}, got {result.returncode}"
    assert _git_local_get(fake_repo, "user.name") == agent_id
    assert _git_local_get(fake_repo, "user.email") == f"{agent_id}@multi-agent-shogun.local"


# ---------------------------------------------------------------------------
# Test — 1 unknown trial (whitelist 外 = skip + warn)
# ---------------------------------------------------------------------------

def test_unknown_agent_id_skips_and_warns(fake_repo: Path, fake_tmux: Path) -> None:
    """Non-whitelist agent_id must trigger warning and leave --local config unset."""
    result = _run_hook(fake_repo, fake_tmux, UNKNOWN_AGENT_ID)
    assert result.returncode == 0

    # 1) Local config must NOT be set for the unknown agent.
    assert _git_local_get(fake_repo, "user.name") == "", (
        "unknown agent_id must NOT set user.name"
    )
    assert _git_local_get(fake_repo, "user.email") == "", (
        "unknown agent_id must NOT set user.email"
    )

    # 2) Whitelist 外 warning must surface (stdout for agent context, or log fallback).
    log_path = fake_repo / "logs" / "session_start_hook.log"
    log_text = log_path.read_text() if log_path.exists() else ""
    surfaced = result.stdout + result.stderr + log_text
    assert "whitelist 外" in surfaced, (
        "unknown agent_id must surface whitelist-out warning, "
        f"got:\nstdout={result.stdout!r}\nstderr={result.stderr!r}\nlog={log_text!r}"
    )
    # 3) The whitelist text must enumerate all 10 known agent_ids for diagnostics.
    for known in WHITELIST:
        assert known in surfaced, f"warning must enumerate whitelist member {known}"
