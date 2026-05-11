"""tests/test_auto_git_sync.py — cycle2 P0-1 unit tests

Bare repo fixture + integration tests for ``scripts/auto_git_sync.sh``
(= pull-only mode, F007 遵守 refactor 後の版).

Covered scenarios:
  (a) FF pull          — local が remote ancestor のとき pull --ff-only が走り status=ff_pulled
  (b) divergent HALT   — local/remote 双方が unique commit を持つとき HALT (non_ff_divergent)
  (c) up_to_date       — local == remote のとき no-op、status=up_to_date
  (d) local_ahead F007 — local ahead で auto-push せず log "local_ahead_awaiting_manual_push"
  (e) flock 二重起動禁  — concurrent execution は SKIPPED (exit 0、log 不変)
  (f) stash dirty pull — dirty working tree + FF pull は stash → pull → pop で成立

Note (cycle2 fix 補足):
  旧版 (auto-commit + auto-push) を前提とした P0-2 (privacy head-200) と
  P0-3 (auto commit allowlist) は、pull-only refactor で privacy gate / auto commit
  そのものが script から削除済、構造的解消 (moot)。本 test は新版の挙動を pin する。

Implementation note:
  scripts/auto_git_sync.sh は ``.gitignore`` 対象ゆえ production script を直接編集せず、
  fixture で hardcoded path (REPO_ROOT, LOCK_FILE) を sed-replace した
  ローカルコピーを実行する。
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest


REPO_DIR = Path(__file__).resolve().parent.parent
SCRIPT_SRC = REPO_DIR / "scripts" / "auto_git_sync.sh"

if not SCRIPT_SRC.is_file():
    pytest.skip(  # noqa: PT005 — only triggered when script absent (= cross-PC missing)
        f"auto_git_sync.sh not found at {SCRIPT_SRC} (gitignored, may not exist on this PC)",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git(cwd, *args, env=None):
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
        env=env,
        timeout=30,
    )


def _prepare_workspace(tmp_path: Path) -> dict:
    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(remote)],
        check=True,
        capture_output=True,
        timeout=15,
    )

    local = tmp_path / "local"
    subprocess.run(
        ["git", "clone", str(remote), str(local)],
        check=True,
        capture_output=True,
        timeout=15,
    )
    _git(local, "config", "user.email", "test@example.com")
    _git(local, "config", "user.name", "test")

    (local / "README.md").write_text("# test\n")
    _git(local, "add", "README.md")
    _git(local, "commit", "-m", "initial")
    _git(local, "push", "-u", "origin", "main")

    (local / "scripts").mkdir(exist_ok=True)

    # Copy the production script with hardcoded paths replaced for test isolation.
    src_text = SCRIPT_SRC.read_text()
    lock_file = tmp_path / "auto_git_sync.lock"

    needle_repo = 'REPO_ROOT="$HOME/projects/multi-agent-shogun-newbuild"'
    needle_lock = 'LOCK_FILE="/run/user/$(id -u)/auto_git_sync.lock"'
    assert needle_repo in src_text, (
        "scripts/auto_git_sync.sh layout changed; update fixture's sed-replace needle"
    )
    assert needle_lock in src_text, (
        "scripts/auto_git_sync.sh LOCK_FILE layout changed; update fixture"
    )
    modified = src_text.replace(
        needle_repo, f'REPO_ROOT="{local}"'
    ).replace(
        needle_lock, f'LOCK_FILE="{lock_file}"'
    )
    script = local / "scripts" / "auto_git_sync_under_test.sh"
    script.write_text(modified)
    script.chmod(0o755)

    return {
        "remote": remote,
        "local": local,
        "script": script,
        "lock": lock_file,
        "log": local / "queue" / "reports" / "auto_sync_log.yaml",
    }


def _make_other_clone(tmp_path: Path, remote: Path, name: str) -> Path:
    other = tmp_path / name
    subprocess.run(
        ["git", "clone", str(remote), str(other)],
        check=True,
        capture_output=True,
        timeout=15,
    )
    _git(other, "config", "user.email", "other@example.com")
    _git(other, "config", "user.name", "other")
    return other


def _exec_sync(workspace: dict, *, extra_env=None, args=()):
    env = os.environ.copy()
    env["PC_ID"] = "test_pc"
    env["AUTO_GIT_SYNC_REMOTE"] = "origin"
    env["AUTO_GIT_SYNC_BRANCH"] = "main"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(workspace["script"]), *args],
        cwd=str(workspace["local"]),
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


@pytest.fixture
def workspace(tmp_path: Path) -> dict:
    return _prepare_workspace(tmp_path)


# ---------------------------------------------------------------------------
# (a) FF pull
# ---------------------------------------------------------------------------

class TestFastForwardPull:
    def test_ff_pull_when_remote_ahead(self, tmp_path, workspace):
        other = _make_other_clone(tmp_path, workspace["remote"], "other_a")
        (other / "queue").mkdir(exist_ok=True)
        (other / "queue" / "x.yaml").write_text("a: 1\n")
        _git(other, "add", "queue/x.yaml")
        _git(other, "commit", "-m", "other commit")
        _git(other, "push", "origin", "main")

        before = _git(workspace["local"], "rev-parse", "HEAD").stdout.strip()
        result = _exec_sync(workspace)
        assert result.returncode == 0, f"stderr={result.stderr!r}"

        after = _git(workspace["local"], "rev-parse", "HEAD").stdout.strip()
        assert after != before, "expected HEAD to advance via FF pull"
        assert (workspace["local"] / "queue" / "x.yaml").exists()

        log_text = workspace["log"].read_text()
        assert "status=ff_pulled" in log_text


# ---------------------------------------------------------------------------
# (b) divergent HALT (auto-merge 厳禁)
# ---------------------------------------------------------------------------

class TestDivergentHalt:
    def test_divergent_halts_without_auto_merge(self, tmp_path, workspace):
        # local diverges (commit only on local)
        (workspace["local"] / "scripts" / "z.sh").write_text("echo local\n")
        _git(workspace["local"], "add", "scripts/z.sh")
        _git(workspace["local"], "commit", "-m", "local commit")
        local_head_before = _git(
            workspace["local"], "rev-parse", "HEAD"
        ).stdout.strip()

        # other PC also diverges with unrelated commit
        other = _make_other_clone(tmp_path, workspace["remote"], "other_b")
        (other / "queue").mkdir(exist_ok=True)
        (other / "queue" / "y.yaml").write_text("b: 2\n")
        _git(other, "add", "queue/y.yaml")
        _git(other, "commit", "-m", "other commit")
        _git(other, "push", "origin", "main")

        result = _exec_sync(workspace)
        assert result.returncode != 0, "expected HALT on divergent"

        # HEAD must not have moved (= no auto-merge)
        local_head_after = _git(
            workspace["local"], "rev-parse", "HEAD"
        ).stdout.strip()
        assert local_head_after == local_head_before

        log_text = workspace["log"].read_text()
        assert "non_ff_divergent" in log_text


# ---------------------------------------------------------------------------
# (c) up_to_date — no-op
# ---------------------------------------------------------------------------

class TestUpToDate:
    def test_up_to_date_is_no_op(self, workspace):
        before = _git(workspace["local"], "rev-parse", "HEAD").stdout.strip()
        result = _exec_sync(workspace)
        assert result.returncode == 0, f"stderr={result.stderr!r}"

        after = _git(workspace["local"], "rev-parse", "HEAD").stdout.strip()
        assert after == before

        log_text = workspace["log"].read_text()
        assert "status=up_to_date" in log_text


# ---------------------------------------------------------------------------
# (d) local_ahead — F007 遵守 (auto-push 禁、halt せず log のみ)
# ---------------------------------------------------------------------------

class TestLocalAheadF007:
    def test_local_ahead_does_not_push_and_does_not_halt(self, workspace):
        # Local advances, remote stays put
        (workspace["local"] / "scripts" / "k.sh").write_text("echo k\n")
        _git(workspace["local"], "add", "scripts/k.sh")
        _git(workspace["local"], "commit", "-m", "local-only commit")

        local_head = _git(workspace["local"], "rev-parse", "HEAD").stdout.strip()
        remote_head_before = subprocess.run(
            ["git", "--git-dir", str(workspace["remote"]), "rev-parse", "refs/heads/main"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
        assert local_head != remote_head_before

        result = _exec_sync(workspace)
        assert result.returncode == 0, f"stderr={result.stderr!r}"

        # F007: remote must NOT have advanced (script must not push)
        remote_head_after = subprocess.run(
            ["git", "--git-dir", str(workspace["remote"]), "rev-parse", "refs/heads/main"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
        assert remote_head_after == remote_head_before, "F007 violation: script must not auto-push"

        log_text = workspace["log"].read_text()
        assert "local_ahead_awaiting_manual_push" in log_text


# ---------------------------------------------------------------------------
# (e) flock 二重起動禁 — concurrent run skipped
# ---------------------------------------------------------------------------

class TestFlockExclusive:
    def test_concurrent_run_is_skipped(self, workspace):
        lock = workspace["lock"]
        lock.parent.mkdir(parents=True, exist_ok=True)

        # Hold the lock externally for 10 s.
        holder = subprocess.Popen(
            ["flock", "-x", str(lock), "sleep", "10"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            time.sleep(0.4)  # let `flock -x` acquire
            result = _exec_sync(workspace)
            # SKIPPED path: exit 0, message on stderr, no work performed
            assert result.returncode == 0
            stderr_lower = result.stderr.lower()
            assert "skipped" in stderr_lower and "lock" in stderr_lower

            # No pull_cycle entry was written by the skipped run.
            if workspace["log"].exists():
                assert "pull_cycle" not in workspace["log"].read_text()
        finally:
            holder.terminate()
            try:
                holder.wait(timeout=3)
            except subprocess.TimeoutExpired:
                holder.kill()
                holder.wait(timeout=3)


# ---------------------------------------------------------------------------
# (f) Dirty tree + FF pull via stash → pull → pop
# ---------------------------------------------------------------------------

class TestDirtyTreeFFPull:
    def test_dirty_tree_ff_pull_via_stash(self, tmp_path, workspace):
        # Remote advances
        other = _make_other_clone(tmp_path, workspace["remote"], "other_f")
        (other / "queue").mkdir(exist_ok=True)
        (other / "queue" / "x.yaml").write_text("a: 1\n")
        _git(other, "add", "queue/x.yaml")
        _git(other, "commit", "-m", "other commit")
        _git(other, "push", "origin", "main")

        # Local has dirty tracked-file modification
        readme = workspace["local"] / "README.md"
        readme.write_text(readme.read_text() + "WIP\n")
        assert _git(workspace["local"], "status", "--porcelain").stdout.strip() != ""

        result = _exec_sync(workspace)
        assert result.returncode == 0, f"stderr={result.stderr!r}"

        # FF pull happened
        log_text = workspace["log"].read_text()
        assert "status=ff_pulled" in log_text

        # Dirty modification is restored (= stash pop succeeded)
        assert "WIP" in readme.read_text()

        # The remote file is now present locally
        assert (workspace["local"] / "queue" / "x.yaml").exists()


# ---------------------------------------------------------------------------
# (sanity) Production script parses cleanly under bash -n
# ---------------------------------------------------------------------------

class TestScriptSyntax:
    def test_bash_n_clean(self):
        result = subprocess.run(
            ["bash", "-n", str(SCRIPT_SRC)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
