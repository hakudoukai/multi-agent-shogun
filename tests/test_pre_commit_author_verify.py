"""tests/test_pre_commit_author_verify.py — cmd_inbox_reform cycle 17 黒田 v2 P0#2/#3 fix.

``scripts/pre_commit_author_verify.sh`` の挙動 pin:

  - whitelist agent_id × in-sync config       → exit 0 + 無設定変更
  - whitelist agent_id × drift config         → exit 0 + drift 補正 (reset)
  - whitelist agent_id × unset (= 初期) config → exit 0 + 新規 set
  - whitelist 外 agent_id                       → exit 2 + commit 阻止 + 無設定
  - agent_id 未取得 (= env 全不在)              → exit 1 + commit 続行可

SKIP=0 — 全 5 case を SKIP なしで pin。
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
SCRIPT = REPO_DIR / "scripts" / "pre_commit_author_verify.sh"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=str(repo), check=True)
    return repo


def _run(
    repo: Path,
    *,
    agent_id: str | None = None,
    use_tmux_env: bool = False,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    # 親環境からの汚染を排除 (= ashigaru4 本人 tmux 配下で test 走らせるため)
    env.pop("TMUX_PANE", None)
    env.pop("PRE_COMMIT_AGENT_ID", None)
    env.pop("PRE_COMMIT_REPO_ROOT", None)

    if agent_id is not None:
        if use_tmux_env:
            env["TMUX_PANE"] = "%fake"
            env["PRE_COMMIT_AGENT_ID"] = agent_id
        else:
            env["PRE_COMMIT_AGENT_ID"] = agent_id
    env["PRE_COMMIT_REPO_ROOT"] = str(repo)

    return subprocess.run(
        ["bash", str(SCRIPT)],
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
# Tests
# ---------------------------------------------------------------------------

def test_unset_config_is_initialized_for_whitelist_agent(fake_repo: Path) -> None:
    """初期 unset → wrapper が agent_id 値で set し exit 0。"""
    result = _run(fake_repo, agent_id="ashigaru4")
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert _git_local_get(fake_repo, "user.name") == "ashigaru4"
    assert _git_local_get(fake_repo, "user.email") == "ashigaru4@multi-agent-shogun.local"


def test_drift_config_is_corrected_for_whitelist_agent(fake_repo: Path) -> None:
    """drift 状態 (= 他 agent 値) を wrapper が agent_id 値に補正、exit 0。"""
    # 事前に別 agent 値で local config を汚染
    subprocess.run(
        ["git", "-C", str(fake_repo), "config", "--local", "user.name", "ashigaru5"],
        check=True,
    )
    subprocess.run(
        [
            "git", "-C", str(fake_repo), "config", "--local", "user.email",
            "ashigaru5@multi-agent-shogun.local",
        ],
        check=True,
    )

    result = _run(fake_repo, agent_id="ashigaru4")
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert _git_local_get(fake_repo, "user.name") == "ashigaru4"
    assert _git_local_get(fake_repo, "user.email") == "ashigaru4@multi-agent-shogun.local"
    assert "drift detected" in result.stderr


def test_in_sync_config_passes_without_change(fake_repo: Path) -> None:
    """既に整合の場合は無変更で exit 0。"""
    subprocess.run(
        ["git", "-C", str(fake_repo), "config", "--local", "user.name", "ashigaru4"],
        check=True,
    )
    subprocess.run(
        [
            "git", "-C", str(fake_repo), "config", "--local", "user.email",
            "ashigaru4@multi-agent-shogun.local",
        ],
        check=True,
    )

    result = _run(fake_repo, agent_id="ashigaru4")
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert "verify pass" in result.stderr
    assert _git_local_get(fake_repo, "user.name") == "ashigaru4"


def test_whitelist_outsider_blocks_commit(fake_repo: Path) -> None:
    """whitelist 外 agent_id → exit 2 + 無設定 + warning。"""
    result = _run(fake_repo, agent_id="maeda")
    assert result.returncode == 2, f"stderr={result.stderr}"
    # config は触れない
    assert _git_local_get(fake_repo, "user.name") == ""
    assert _git_local_get(fake_repo, "user.email") == ""
    assert "whitelist" in result.stderr


def test_no_agent_id_falls_back_to_personal_dev_mode(fake_repo: Path) -> None:
    """agent_id 未取得 (= 個人開発) → exit 1 で commit 続行可、config 不変。"""
    result = _run(fake_repo, agent_id=None)
    assert result.returncode == 1, f"stderr={result.stderr}"
    assert _git_local_get(fake_repo, "user.name") == ""
