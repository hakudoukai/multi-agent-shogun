"""Behavioral re-introduce tests for scripts/lint/check_file_path_owner.sh.

Simulates today's 3 scope_contamination incidents (= ashigaru3 commit 65c917e,
ashigaru7 commit 240dd7a, ashigaru6 commit a25a1b7) plus task-manifest allowlist
authorized/unauthorized cases plus same-owner pass case. Verifies that the
new owner-aware hook rejects the contamination scenarios that the prior
staged-residual-check could not detect.

Refs:
- scripts/lint/check_file_path_owner.sh
- docs/cmd020_scope_contamination_v2_incident_root_cause.md §2 (incident detail)
- queue/tasks/subtask_cmd020_scope_contamination_prevention_v2.yaml AC3
"""
from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / "scripts" / "lint" / "check_file_path_owner.sh"


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


def _init_temp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "test-bootstrap")
    _run_git(repo, "config", "user.email", "test@example.local")
    # Seed: empty commit so HEAD exists
    _run_git(repo, "commit", "--allow-empty", "-m", "seed", "-q")
    return repo


def _write(repo: Path, relpath: str, content: str = "x\n") -> None:
    full = repo / relpath
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")


def _stage(repo: Path, *paths: str) -> None:
    _run_git(repo, "add", *paths)


def _run_hook(
    repo: Path,
    agent_id: str,
    lint_mode: str = "strict",
) -> tuple[int, str, str]:
    """Invoke hook with explicit agent_id env override (avoids tmux dependency)."""
    env = os.environ.copy()
    env["PRE_COMMIT_AGENT_ID"] = agent_id
    env["SCOPE_CONTAMINATION_LINT_MODE"] = lint_mode
    env.pop("TMUX_PANE", None)
    proc = subprocess.run(
        ["bash", str(HOOK_SCRIPT)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _write_task_pointer(repo: Path, agent: str, shared_files: list[str]) -> None:
    """Create queue/tasks/<agent>.yaml with shared_files_allowlist field."""
    lines = [
        f"task:",
        f"  task_id: test_task_{agent}",
        f"  status: assigned",
        f"shared_files_allowlist:",
    ]
    for sf in shared_files:
        lines.append(f"  - {sf}")
    _write(repo, f"queue/tasks/{agent}.yaml", "\n".join(lines) + "\n")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return _init_temp_repo(tmp_path)


# ---------------------------------------------------------------------------
# AC3 test_1: ashigaru3 commit time, ashigaru2 staged file mixed in → REJECT
# Reproduces 2026-05-12 11:17 ashigaru3 commit f3651ae 混入事故 (= ashigaru2
# dashboard_layer_b_inventory.yaml が ashigaru3 commit に取込された scenario)
# ---------------------------------------------------------------------------
def test_1_ashigaru3_commit_with_ashigaru2_staged_residual_rejected(repo: Path) -> None:
    _write(repo, "queue/reports/ashigaru3_layer_c_report.yaml", "owner: ashigaru3\n")
    _write(repo, "queue/reports/ashigaru2_dashboard_layer_b_inventory.yaml", "owner: ashigaru2\n")
    _stage(
        repo,
        "queue/reports/ashigaru3_layer_c_report.yaml",
        "queue/reports/ashigaru2_dashboard_layer_b_inventory.yaml",
    )
    rc, out, err = _run_hook(repo, agent_id="ashigaru3")
    assert rc == 1, f"hook should REJECT cross-owner staged file; got rc={rc}\nstderr={err}"
    assert "ashigaru2_dashboard_layer_b_inventory.yaml" in err
    assert "path-owner=ashigaru2" in err


# ---------------------------------------------------------------------------
# AC3 test_2: ashigaru6 staged taken into ashigaru3 commit
# Reproduces 9285be2/incident chain in inventory yaml today_incidents.incident_4
# ---------------------------------------------------------------------------
def test_2_ashigaru3_commit_with_ashigaru6_staged_residual_rejected(repo: Path) -> None:
    _write(repo, "queue/reports/ashigaru3_sc_specialty_inventory_report.yaml", "owner: ashigaru3\n")
    _write(repo, "queue/reports/ashigaru6_cmd020_dashboard_layer_f_kihan_render_report.yaml", "owner: ashigaru6\n")
    _stage(
        repo,
        "queue/reports/ashigaru3_sc_specialty_inventory_report.yaml",
        "queue/reports/ashigaru6_cmd020_dashboard_layer_f_kihan_render_report.yaml",
    )
    rc, _out, err = _run_hook(repo, agent_id="ashigaru3")
    assert rc == 1, f"expected REJECT; stderr={err}"
    assert "ashigaru6_cmd020_dashboard_layer_f" in err


# ---------------------------------------------------------------------------
# AC3 test_3: Today's 3 incident scenarios simulated as 3 sub-cases
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "incident,current_agent,staged_paths,expected_violator",
    [
        (
            "incident_1_65c917e",
            "ashigaru3",
            [
                "queue/reports/ashigaru3_subtask_cmd020_sc_specialty_inventory_report.yaml",
                "docs/cmd_020_implementation_required_14_cmd_proposal.md",  # = shared, unauthorized
            ],
            "docs/cmd_020_implementation_required_14_cmd_proposal.md",
        ),
        (
            "incident_2_240dd7a",
            "ashigaru7",
            [
                "docs/dashboard_status_classification_logic.md",  # = shared, unauthorized
                "docs/dashboard_layer_c_function.md",  # = shared, unauthorized
                "docs/dashboard_layer_d_zunou.md",  # = shared, unauthorized
            ],
            "docs/dashboard_layer_c_function.md",
        ),
        (
            "incident_3_a25a1b7",
            "ashigaru6",
            [
                "queue/reports/ashigaru7_subtask_cmd020_implementation_required_14_cmd_proposal_inventory.yaml",
                "queue/reports/ashigaru7_subtask_cmd020_implementation_required_14_cmd_proposal_report.yaml",
                "scripts/test/test_subtask_cmd020_implementation_required_14_cmd_proposal_static_contract.py",
            ],
            "queue/reports/ashigaru7_subtask_cmd020_implementation_required_14_cmd_proposal_inventory.yaml",
        ),
    ],
)
def test_3_today_3_incidents_reject(
    repo: Path,
    incident: str,
    current_agent: str,
    staged_paths: list[str],
    expected_violator: str,
) -> None:
    for p in staged_paths:
        _write(repo, p, f"content: {incident}\n")
    _stage(repo, *staged_paths)
    rc, _out, err = _run_hook(repo, agent_id=current_agent)
    assert rc == 1, f"{incident}: expected REJECT but got rc={rc}\nstderr={err}"
    assert expected_violator in err, (
        f"{incident}: expected mention of {expected_violator} in hook output\nstderr={err}"
    )


# ---------------------------------------------------------------------------
# AC3 test_4: task-manifest allowlisted shared file → PASS for authorized agent
# ---------------------------------------------------------------------------
def test_4_allowlisted_shared_file_passes_for_authorized_agent(repo: Path) -> None:
    _write_task_pointer(repo, "ashigaru2", [".gitignore"])
    _write(repo, ".gitignore", "*.log\n")
    _stage(repo, "queue/tasks/ashigaru2.yaml", ".gitignore")
    rc, _out, err = _run_hook(repo, agent_id="ashigaru2", lint_mode="strict")
    assert rc == 0, (
        f"allowlisted .gitignore + own task pointer should PASS for ashigaru2;"
        f" rc={rc} stderr={err}"
    )


# ---------------------------------------------------------------------------
# AC3 test_5: unauthorized shared file → REJECT in strict mode for ashigaru
# ---------------------------------------------------------------------------
def test_5_unauthorized_shared_file_rejected_in_strict_mode(repo: Path) -> None:
    _write(repo, "config/settings.yaml", "key: value\n")
    _stage(repo, "config/settings.yaml")
    rc, _out, err = _run_hook(repo, agent_id="ashigaru2", lint_mode="strict")
    assert rc == 1, f"unauthorized shared file should REJECT in strict mode; stderr={err}"
    assert "config/settings.yaml" in err
    assert "shared edits" in err or "REJECT" in err


def test_5b_unauthorized_shared_file_warning_only_for_karo(repo: Path) -> None:
    """karo (orchestrator role) → warn-only, not reject (= task spec test_5 後段)."""
    _write(repo, "config/settings.yaml", "key: value\n")
    _stage(repo, "config/settings.yaml")
    rc, _out, err = _run_hook(repo, agent_id="karo", lint_mode="strict")
    assert rc == 0, f"karo orchestrator role should warn-only for unauthorized shared; stderr={err}"
    assert "WARNING" in err


# ---------------------------------------------------------------------------
# AC3 test_6: same-owner file → PASS (owner mapping path)
# ---------------------------------------------------------------------------
def test_6_same_owner_file_passes(repo: Path) -> None:
    _write(repo, "queue/reports/ashigaru2_my_report.yaml", "owner: ashigaru2\n")
    _write(repo, "queue/reports/ashigaru2_my_pytest.log", "ok\n")
    _stage(
        repo,
        "queue/reports/ashigaru2_my_report.yaml",
        "queue/reports/ashigaru2_my_pytest.log",
    )
    rc, _out, err = _run_hook(repo, agent_id="ashigaru2", lint_mode="strict")
    assert rc == 0, f"same-owner files should PASS; stderr={err}"
    assert "OK" in err
