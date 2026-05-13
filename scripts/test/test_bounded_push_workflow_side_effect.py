"""Side-effect tests for the bounded-push workflow (worktree + cherry-pick + equality assert).

Scope (= task YAML AC4):
- NOT a unit test for scripts/auto_git_sync.sh. The auto-git-sync coverage stays
  in tests/test_auto_git_sync.py and remains pull-only.
- This test file exercises the side effects of the manual bounded-push workflow
  that ashigaru/karo follow when releasing inline-batch commits: worktree create,
  cherry-pick selected SHAs, pre-push equality diff between expected/actual SHA
  lists, then push.

Three cases:
  1. cherry-pick produces a new SHA even when content is identical (= content-same
     SHA-divergent). The pre-push equality diff must detect the mismatch and abort.
  2. Two parallel cherry-pick attempts produce divergent worktrees (= ahead+behind).
     A subsequent rebase reconciles them into a linear chain consistent with
     bounded-push expectations.
  3. The existing tests/test_auto_git_sync.py file is retained out of scope for
     this task. We assert its existence + that the present bounded-push test does
     not overlap (= different file path).

Refs:
- queue/tasks/subtask_cmd020_scope_contamination_prevention_v2.yaml AC4 / step_4
- scripts/auto_git_sync.sh (= pull-only, unchanged)
"""
from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_AUTO_SYNC_TEST = REPO_ROOT / "tests" / "test_auto_git_sync.py"


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=check, capture_output=True, text=True
    )


def _init_origin_and_clone(tmp_path: Path) -> tuple[Path, Path]:
    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare", "-q", "-b", "main")

    work = tmp_path / "work"
    work.mkdir()
    _git(work, "init", "-q", "-b", "main")
    _git(work, "config", "user.name", "bp-test")
    _git(work, "config", "user.email", "bp@example.local")
    _git(work, "remote", "add", "origin", str(origin))
    # seed initial commit
    (work / "README.md").write_text("seed\n", encoding="utf-8")
    _git(work, "add", "README.md")
    _git(work, "commit", "-m", "seed", "-q")
    _git(work, "push", "-u", "origin", "main", "-q")
    return origin, work


def test_1_cherry_pick_yields_new_sha_and_equality_diff_detects_mismatch(
    tmp_path: Path,
) -> None:
    """cherry-pick produces new SHA; pre-push equality diff must detect divergence."""
    _origin, work = _init_origin_and_clone(tmp_path)

    # Advance main by one commit so the cherry-pick target has a different parent
    # than the feature branch base. Without this, cherry-pick onto an identical
    # parent reproduces the source SHA (= no side effect to test).
    (work / "base.txt").write_text("base\n", encoding="utf-8")
    _git(work, "add", "base.txt")
    _git(work, "commit", "-m", "advance main base", "-q")
    _git(work, "push", "origin", "main", "-q")

    # Create a feature branch from before main advanced (HEAD~1)
    _git(work, "checkout", "-q", "-b", "feature", "HEAD~1")
    (work / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(work, "add", "feature.txt")
    _git(work, "commit", "-m", "add feature", "-q")
    feature_sha = _git(work, "rev-parse", "HEAD").stdout.strip()

    # Bounded-push workflow: worktree add + cherry-pick onto origin/main (= advanced base)
    wt_path = tmp_path / "boundedwt"
    _git(work, "worktree", "add", "-q", str(wt_path), "origin/main")
    _git(wt_path, "config", "user.name", "bp-test")
    _git(wt_path, "config", "user.email", "bp@example.local")
    _git(wt_path, "cherry-pick", feature_sha)
    cherry_sha = _git(wt_path, "rev-parse", "HEAD").stdout.strip()

    # Cherry-pick produces a new SHA (different from source) even though content matches
    assert cherry_sha != feature_sha, (
        "Expected cherry-pick to produce a new SHA; got identical SHA which would indicate "
        "the test is not exercising the side effect under inspection."
    )

    # Pre-push equality diff: expected (= feature_sha) vs actual (= cherry_sha)
    actual_list = _git(wt_path, "log", "origin/main..HEAD", "--format=%H").stdout.strip()
    expected_list = feature_sha
    assert actual_list != expected_list, (
        "Equality diff must surface the SHA mismatch; if these were equal the bounded-push "
        "would mistakenly proceed without operator awareness."
    )

    # Cleanup
    _git(work, "worktree", "remove", "--force", str(wt_path))


def test_2_parallel_cherry_picks_rebase_to_linear_consistent_chain(
    tmp_path: Path,
) -> None:
    """Two concurrent ashigaru bounded-push attempts → divergent worktrees, then rebase reconciles."""
    _origin, work = _init_origin_and_clone(tmp_path)

    # Build two feature commits on main side
    _git(work, "checkout", "-q", "main")
    (work / "a.txt").write_text("a\n", encoding="utf-8")
    _git(work, "add", "a.txt")
    _git(work, "commit", "-m", "ashigaru1: add a", "-q")
    sha_a = _git(work, "rev-parse", "HEAD").stdout.strip()

    (work / "b.txt").write_text("b\n", encoding="utf-8")
    _git(work, "add", "b.txt")
    _git(work, "commit", "-m", "ashigaru2: add b", "-q")
    sha_b = _git(work, "rev-parse", "HEAD").stdout.strip()

    # ashigaru1 worktree: cherry-pick A only
    wt1 = tmp_path / "wt_ashigaru1"
    _git(work, "worktree", "add", "-q", str(wt1), "origin/main")
    _git(wt1, "config", "user.name", "bp-test")
    _git(wt1, "config", "user.email", "bp@example.local")
    _git(wt1, "cherry-pick", sha_a)
    # ashigaru1 pushes
    _git(wt1, "push", "origin", "HEAD:main", "-q")

    # ashigaru2 worktree (= already in race) tries to cherry-pick B from stale origin/main
    wt2 = tmp_path / "wt_ashigaru2"
    _git(work, "worktree", "add", "-q", str(wt2), sha_a + "~1")  # = origin/main before ashigaru1 pushed
    _git(wt2, "config", "user.name", "bp-test")
    _git(wt2, "config", "user.email", "bp@example.local")
    _git(wt2, "cherry-pick", sha_b)

    # Now ashigaru2 fetches and discovers ahead+behind
    _git(wt2, "fetch", "origin", "-q")
    behind_ahead = _git(
        wt2, "rev-list", "--left-right", "--count", "origin/main...HEAD"
    ).stdout.strip()
    behind_str, ahead_str = behind_ahead.split()
    assert int(behind_str) >= 1 and int(ahead_str) >= 1, (
        f"Expected ahead+behind divergent state; got behind={behind_str} ahead={ahead_str}"
    )

    # Rebase reconciles: ashigaru2 rebases onto origin/main → linear chain
    _git(wt2, "rebase", "origin/main")
    final_behind_ahead = _git(
        wt2, "rev-list", "--left-right", "--count", "origin/main...HEAD"
    ).stdout.strip()
    final_behind, final_ahead = final_behind_ahead.split()
    assert int(final_behind) == 0 and int(final_ahead) == 1, (
        f"After rebase, expected behind=0 ahead=1 (linear); got behind={final_behind} ahead={final_ahead}"
    )

    # Cleanup
    _git(work, "worktree", "remove", "--force", str(wt1))
    _git(work, "worktree", "remove", "--force", str(wt2))


def test_3_existing_auto_git_sync_test_is_retained_and_out_of_scope() -> None:
    """tests/test_auto_git_sync.py exists separately and is NOT modified by this task."""
    assert LEGACY_AUTO_SYNC_TEST.is_file(), (
        f"Expected legacy pull-only coverage at {LEGACY_AUTO_SYNC_TEST}; absence would mean "
        "the auto-git-sync pull-only contract is unguarded."
    )
    # Sanity: the legacy test covers pull-only behavior
    text = LEGACY_AUTO_SYNC_TEST.read_text(encoding="utf-8")
    # The legacy test should exercise auto_git_sync.sh (= the pull-only daemon).
    assert "auto_git_sync" in text, (
        "Legacy file content does not reference auto_git_sync — coverage may have drifted."
    )
    # And this bounded-push test must live at a separate path (= no overlap).
    this_test = Path(__file__).resolve()
    assert this_test != LEGACY_AUTO_SYNC_TEST, "scope overlap with legacy auto-git-sync test"
    assert this_test.parent.name == "test" and this_test.parent.parent.name == "scripts", (
        "bounded-push side-effect test must live under scripts/test/ to keep scope distinct"
    )
