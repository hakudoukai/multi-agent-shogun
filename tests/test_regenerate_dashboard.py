"""tests/test_regenerate_dashboard.py — cmd_020 Stage 2 AC18 gate.

Coverage (per 黒田 audit kuroda_dashboard_design_v0_2_reaudit_20260511, perspective 6):
  - unit: jinja render / progress calc / status enum / memory snapshot
  - snapshot: known input → known output skeleton
  - HTML smoke: generated dashboard.md parses as markdown (heading/table)
  - privacy/redaction: validate_report_privacy.py CLEAN on generated output
  - Supabase timeout fallback: REST failure → cached payload used
  - cache fallback: ETag 304 → cache_hit=True

cycle2 additions (kuroda_cmd020_regenerate_dashboard_py_audit_20260511):
  - F1: verify is time-stable across generated_at drift / git_log relative age
  - F2: live-queue audit-waiting statuses aggregate to stage values, not 'unknown'
  - F3: privacy result classifier separates HIGH/WARN; warned ≠ clean
  - F4: legacy hand-edited dashboard.md is archived once before overwrite

SKIP=0 mandated. Each test must execute deterministically; no network calls.
"""

from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import textwrap
import time
import urllib.error
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import regenerate_dashboard as rd  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_tasks_dir(tmp_path: Path) -> Path:
    tasks = tmp_path / "tasks"
    tasks.mkdir()
    (tasks / "ashigaru1.yaml").write_text(
        textwrap.dedent(
            """
            task:
              task_id: t_done_verified
              assigned_to: ashigaru1
              status: done
              verdict: pass
              completion_gate: open
              evidence_state: complete
              parent_cmd: cmd_test
              bloom_level: L3
              verification_layer:
                shogun_verified: true

            ---

            task:
              task_id: t_done_concerns
              assigned_to: ashigaru1
              status: done
              verdict: pass_with_concerns
              completion_gate: open
              evidence_state: complete

            ---

            task:
              task_id: t_blocked
              assigned_to: ashigaru1
              status: blocked
              evidence_state: blocked_env

            ---

            task:
              task_id: t_in_progress
              assigned_to: ashigaru1
              status: in_progress

            ---

            task:
              task_id: t_assigned
              assigned_to: ashigaru1
              status: assigned
            """
        ).strip(),
        encoding="utf-8",
    )
    (tasks / "ashigaru2.yaml").write_text(
        textwrap.dedent(
            """
            task:
              task_id: t_drafted
              assigned_to: ashigaru2
              status: drafted_pending_kuroda_pre_audit
            """
        ).strip(),
        encoding="utf-8",
    )
    return tasks


@pytest.fixture
def sample_reports_dir(tmp_path: Path) -> Path:
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "kuroda_mainpc_report.yaml").write_text("reports: []\n", encoding="utf-8")
    (reports / "ashigaru1_report.yaml").write_text("reports: []\n", encoding="utf-8")
    return reports


@pytest.fixture
def memory_file(tmp_path: Path) -> Path:
    mem = tmp_path / "MEMORY.md"
    mem.write_text("# Memory\n\n- rule: dashboard generator is sole writer\n", encoding="utf-8")
    return mem


@pytest.fixture
def cache_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    cache = tmp_path / "cache"
    monkeypatch.setattr(rd, "CACHE_DIR", cache)
    return cache


# ---------------------------------------------------------------------------
# Unit: progress formula (AC5)
# ---------------------------------------------------------------------------


def test_progress_blocked_is_zero():
    t = rd.TaskEntry(task_id="x", assigned_to="a", status="blocked", raw_status="blocked")
    assert rd.progress_for_task(t) == 0.0


def test_progress_done_verified_complete_is_100():
    t = rd.TaskEntry(
        task_id="x", assigned_to="a", status="done", raw_status="done",
        verdict="pass", completion_gate="open", evidence_state="complete",
        shogun_verified=True,
    )
    assert rd.progress_for_task(t) == 100.0


def test_progress_done_pass_unverified_capped_at_75():
    t = rd.TaskEntry(
        task_id="x", assigned_to="a", status="done", raw_status="done",
        verdict="pass", completion_gate="open", evidence_state="complete",
        shogun_verified=False,
    )
    assert rd.progress_for_task(t) == 75.0


def test_progress_pass_with_concerns_is_75():
    t = rd.TaskEntry(task_id="x", assigned_to="a", status="done", raw_status="done",
                    verdict="pass_with_concerns")
    assert rd.progress_for_task(t) == 75.0


def test_progress_in_progress_is_50():
    t = rd.TaskEntry(task_id="x", assigned_to="a", status="in_progress", raw_status="in_progress")
    assert rd.progress_for_task(t) == 50.0


def test_progress_assigned_is_25():
    t = rd.TaskEntry(task_id="x", assigned_to="a", status="assigned", raw_status="assigned")
    assert rd.progress_for_task(t) == 25.0


def test_progress_drafted_is_15():
    t = rd.TaskEntry(task_id="x", assigned_to="a",
                    status="drafted_pending_kuroda_pre_audit",
                    raw_status="drafted_pending_kuroda_pre_audit")
    assert rd.progress_for_task(t) == 15.0


def test_progress_unknown_is_excluded_from_aggregation():
    t = rd.TaskEntry(task_id="x", assigned_to="a", status="unknown", raw_status="unknown")
    assert rd.progress_for_task(t) is None


def test_progress_evidence_missing_caps_to_50():
    t = rd.TaskEntry(
        task_id="x", assigned_to="a", status="done", raw_status="done",
        verdict="pass", completion_gate="open", evidence_state="missing",
        shogun_verified=True,
    )
    assert rd.progress_for_task(t) == 50.0


def test_aggregate_progress_excludes_unknown():
    tasks = [
        rd.TaskEntry(task_id="a", assigned_to="x", status="done", raw_status="done",
                    verdict="pass", completion_gate="open", evidence_state="complete",
                    shogun_verified=True),
        rd.TaskEntry(task_id="b", assigned_to="x", status="unknown", raw_status="unknown"),
        rd.TaskEntry(task_id="c", assigned_to="y", status="in_progress", raw_status="in_progress"),
    ]
    out = rd.aggregate_progress(tasks)
    assert out["leaf_count"] == 2
    assert out["excluded_count"] == 1
    assert out["overall_pct"] == 75.0


# ---------------------------------------------------------------------------
# Unit: local state loading (AC2)
# ---------------------------------------------------------------------------


def test_load_local_state_reads_tasks(sample_tasks_dir: Path, sample_reports_dir: Path):
    state = rd.load_local_state(tasks_dir=sample_tasks_dir, reports_dir=sample_reports_dir)
    ids = [t.task_id for t in state.tasks]
    assert "t_done_verified" in ids
    assert "t_drafted" in ids
    assert "kuroda_mainpc_report.yaml" in state.reports_snapshot
    # dashboard.md must never appear in reports_snapshot
    assert "dashboard.md" not in state.reports_snapshot


def test_load_local_state_excludes_dashboard_md(tmp_path: Path, sample_tasks_dir: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "dashboard.md").write_text("forbidden", encoding="utf-8")
    state = rd.load_local_state(tasks_dir=sample_tasks_dir, reports_dir=reports)
    # the .md is glob'd by *.yaml only so it should not appear at all
    assert "dashboard.md" not in state.reports_snapshot


def test_load_local_state_records_parse_errors(tmp_path: Path, sample_reports_dir: Path):
    bad = tmp_path / "tasks"
    bad.mkdir()
    (bad / "ashigaru1.yaml").write_text("task:\n  task_id: ok\n  status: done\n---\n: : :", encoding="utf-8")
    state = rd.load_local_state(tasks_dir=bad, reports_dir=sample_reports_dir)
    assert state.parse_errors, "parse error must be surfaced, not silently skipped"
    # Absolute paths must be redacted so privacy gate stays green.
    joined = "\n".join(state.parse_errors)
    assert "/home/" not in joined
    assert "/mnt/c/" not in joined


def test_redact_paths_strips_absolute_paths():
    msg = 'error in "/home/user/x.yaml" and /mnt/c/Windows/Foo'
    out = rd._redact_paths(msg)
    assert "/home/user" not in out
    assert "/mnt/c/Windows" not in out
    assert "<redacted-path>" in out


# ---------------------------------------------------------------------------
# Unit: memory snapshot fallback (AC3)
# ---------------------------------------------------------------------------


def test_memory_snapshot_present(memory_file: Path):
    snap = rd.load_memory_snapshot(memory_file)
    assert snap["available"] is True
    assert snap["source"].endswith("MEMORY.md")
    assert snap["byte_size"] > 0


def test_memory_snapshot_missing(tmp_path: Path):
    snap = rd.load_memory_snapshot(tmp_path / "does_not_exist.md")
    assert snap["available"] is False
    assert "missing" in snap["reason"]


# ---------------------------------------------------------------------------
# Unit: Supabase ETag cache + timeout fallback (AC1)
# ---------------------------------------------------------------------------


class _MockOpener:
    """urllib opener stub that returns scripted responses."""

    def __init__(self, responses: list[Any]):
        self._responses = list(responses)
        self.requests: list[urllib.request.Request] = []

    def open(self, req, timeout=None):  # noqa: ANN001 — match urllib signature
        self.requests.append(req)
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


class _FakeHTTPResponse:
    def __init__(self, body: bytes, status: int = 200, etag: str | None = None):
        self._body = body
        self.status = status
        self.headers = {"ETag": etag} if etag else {}

    def read(self) -> bytes:
        return self._body


def test_fetch_table_200_writes_cache(tmp_path: Path, cache_dir: Path):
    opener = _MockOpener([_FakeHTTPResponse(b'[{"id":1}]', etag='"abc"')])
    tbl = {"name": "form_templates", "strategy": "full", "select": "id"}
    result = rd.fetch_table(tbl, "https://example.test", "anon-key", opener=opener)
    assert result.status == 200
    assert result.cache_hit is False
    assert result.row_count == 1
    cache_path, etag_path = rd._cache_paths("form_templates")
    assert cache_path.exists() and etag_path.exists()
    assert etag_path.read_text(encoding="utf-8") == '"abc"'


def test_fetch_table_304_uses_cache(cache_dir: Path):
    cache_path, etag_path = rd._cache_paths("legal_sources")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps([{"id": 1}, {"id": 2}]), encoding="utf-8")
    etag_path.write_text('"v1"', encoding="utf-8")
    err = urllib.error.HTTPError("u", 304, "Not Modified", {}, io.BytesIO(b""))
    opener = _MockOpener([err])
    result = rd.fetch_table({"name": "legal_sources", "strategy": "diff", "select": "id"},
                            "https://example.test", "anon-key", opener=opener)
    assert result.status == 304
    assert result.cache_hit is True
    assert result.row_count == 2


def test_fetch_table_permission_denied(cache_dir: Path):
    err = urllib.error.HTTPError("u", 401, "Unauthorized", {}, io.BytesIO(b""))
    opener = _MockOpener([err])
    result = rd.fetch_table({"name": "form_templates", "strategy": "full", "select": "id"},
                            "https://example.test", "anon-key", opener=opener)
    assert result.permission_denied is True
    assert result.status == 401


def test_fetch_table_timeout_uses_stale_cache(cache_dir: Path):
    cache_path, _etag = rd._cache_paths("design_decisions")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps([{"id": "dd-001"}]), encoding="utf-8")
    opener = _MockOpener([TimeoutError("simulated")])
    result = rd.fetch_table({"name": "design_decisions", "strategy": "full", "select": "id"},
                            "https://example.test", "anon-key", opener=opener)
    assert result.cache_hit is True
    assert result.row_count == 1


def test_fetch_table_timeout_no_cache(cache_dir: Path):
    opener = _MockOpener([TimeoutError("no cache available")])
    result = rd.fetch_table({"name": "procedure_codes_audit", "strategy": "full", "select": "id"},
                            "https://example.test", "anon-key", opener=opener)
    assert result.cache_hit is False
    assert result.error and "no cache" in result.error or result.error.startswith("network:")


def test_supabase_preflight_missing_credentials_blocks(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    report = rd.supabase_preflight(tables=[{"name": "form_templates", "strategy": "full", "select": "id"}])
    assert report["blocking"] is True
    assert report["tables"][0]["permission_denied"] is True


def test_supabase_preflight_writes_yaml_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    out = tmp_path / "preflight.yaml"
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    report = rd.supabase_preflight(tables=[{"name": "form_templates", "strategy": "full", "select": "id"}])
    rd.write_preflight_report(report, out)
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["blocking"] is True
    assert loaded["tables"][0]["name"] == "form_templates"


# ---------------------------------------------------------------------------
# Snapshot + HTML smoke + jinja (AC4)
# ---------------------------------------------------------------------------


def _baseline_context() -> dict[str, Any]:
    tasks = [
        rd.TaskEntry(task_id="a", assigned_to="ashigaru1", status="done", raw_status="done",
                    verdict="pass", completion_gate="open", evidence_state="complete",
                    shogun_verified=True),
        rd.TaskEntry(task_id="b", assigned_to="ashigaru2", status="in_progress", raw_status="in_progress"),
    ]
    return rd.build_context(
        state=rd.LoadedState(tasks=tasks, source_commit="deadbee", git_log=[]),
        supabase_report={"blocking": False, "tables": [], "schema_version": 1},
        memory_snapshot={"available": True, "source": "memory/MEMORY.md", "byte_size": 123, "head_lines": []},
        writer_pc="mainpc",
    )


def test_render_dashboard_has_warning_header():
    rendered = rd.render_dashboard(_baseline_context())
    assert "auto-generated" in rendered
    assert "scripts/regenerate_dashboard.py" in rendered
    assert "source_commit" in rendered


def test_render_dashboard_includes_task_table():
    rendered = rd.render_dashboard(_baseline_context())
    assert "| ashigaru1 |" in rendered
    assert "| ashigaru2 |" in rendered


def test_render_dashboard_html_smoke():
    """Parses as well-formed markdown: at least 1 H1, 1 table."""
    rendered = rd.render_dashboard(_baseline_context())
    h1_lines = [ln for ln in rendered.splitlines() if ln.startswith("# ") and not ln.startswith("##")]
    assert len(h1_lines) >= 1
    # markdown table = header row followed by separator
    sep_rows = [ln for ln in rendered.splitlines() if re.match(r"^\|[\s\-:\|]+\|$", ln)]
    assert len(sep_rows) >= 3


def test_render_dashboard_snapshot_stable():
    a = rd.render_dashboard(_baseline_context())
    b = rd.render_dashboard(_baseline_context())
    # generated_at differs per call, strip it before comparing the structural skeleton
    skeleton_a = re.sub(r"generated_at: `[^`]+`", "generated_at: `STAMP`", a)
    skeleton_b = re.sub(r"generated_at: `[^`]+`", "generated_at: `STAMP`", b)
    assert skeleton_a == skeleton_b


# ---------------------------------------------------------------------------
# Privacy gate (AC18 redaction)
# ---------------------------------------------------------------------------


def test_render_dashboard_passes_privacy_gate(tmp_path: Path):
    rendered = rd.render_dashboard(_baseline_context())
    out = tmp_path / "dashboard.yaml"
    # validate_report_privacy.py scans yaml/json; wrap rendered text as scannable content.
    yaml.safe_dump({"dashboard": rendered}, out.open("w"), allow_unicode=True)
    script = REPO_ROOT / "scripts" / "validate_report_privacy.py"
    if not script.exists():
        pytest.fail("validate_report_privacy.py missing — AC18 privacy gate cannot run")
    proc = subprocess.run(
        [sys.executable, str(script), str(out)],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, f"privacy gate failed: {proc.stdout}\n{proc.stderr}"


# ---------------------------------------------------------------------------
# Lock + writer-pc gate (AC6)
# ---------------------------------------------------------------------------


def test_generation_lock_is_exclusive(tmp_path: Path):
    lock = tmp_path / "lock"
    with rd.generation_lock(lock):
        with pytest.raises(BlockingIOError):
            with rd.generation_lock(lock):
                pass


def test_secondpc_must_use_verify(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    code = rd.main(["--writer-pc", "secondpc", "--output", str(tmp_path / "x.md")])
    assert code == 1, "SC primary write must be rejected"


def test_head_match_helper():
    assert rd.git_head_match("aaaaaaa", "aaaaaaa") is True
    assert rd.git_head_match("aaaaaaa", "bbbbbbb") is False
    assert rd.git_head_match("aaaaaaa", None) is True


# ---------------------------------------------------------------------------
# End-to-end dry run (smoke)
# ---------------------------------------------------------------------------


def test_main_dry_run_writes_nothing(
    sample_tasks_dir: Path,
    sample_reports_dir: Path,
    memory_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    output = tmp_path / "out.md"
    monkeypatch.setattr(rd, "QUEUE_TASKS_DIR", sample_tasks_dir)
    monkeypatch.setattr(rd, "QUEUE_REPORTS_DIR", sample_reports_dir)
    monkeypatch.setattr(rd, "MEMORY_FILE", memory_file)
    monkeypatch.setattr(rd, "LOCK_FILE", tmp_path / "lock")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)

    code = rd.main([
        "--dry-run", "--no-supabase",
        "--memory-snapshot", str(memory_file),
        "--output", str(output),
    ])
    assert code == 0
    captured = capsys.readouterr().out
    assert "auto-generated" in captured
    assert not output.exists(), "dry-run must not touch output path"


def test_main_writes_output_under_lock(
    sample_tasks_dir: Path,
    sample_reports_dir: Path,
    memory_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    output = tmp_path / "dashboard_out.md"
    monkeypatch.setattr(rd, "QUEUE_TASKS_DIR", sample_tasks_dir)
    monkeypatch.setattr(rd, "QUEUE_REPORTS_DIR", sample_reports_dir)
    monkeypatch.setattr(rd, "MEMORY_FILE", memory_file)
    monkeypatch.setattr(rd, "LOCK_FILE", tmp_path / "lock")
    monkeypatch.setattr(rd, "PREFLIGHT_REPORT", tmp_path / "preflight.yaml")
    monkeypatch.setattr(rd, "ARCHIVE_DIR", tmp_path / "archive")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    code = rd.main([
        "--no-supabase",
        "--memory-snapshot", str(memory_file),
        "--output", str(output),
    ])
    assert code == 0
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "auto-generated" in content
    assert "t_done_verified" in content


# ---------------------------------------------------------------------------
# F1 cycle2: verify must be stable across wall-clock drift
# (kuroda audit verify_time_delta — write tmp → sleep 2 → --verify rc=1)
# ---------------------------------------------------------------------------


def test_verify_ignores_generated_at_drift(tmp_path: Path):
    """F1 regression: verify must succeed when generated_at differs.

    Reproduces kuroda 21:47 audit finding (verify_time_delta). Two contexts
    that differ ONLY in their generated_at timestamp must hash-equal under
    verify_dashboard.
    """
    base = _baseline_context()
    rendered_a = rd.render_dashboard(base)
    base2 = dict(base)
    base2["generated_at"] = "2099-01-01T00:00:00+09:00"
    rendered_b = rd.render_dashboard(base2)
    # Sanity: only generated_at differs between the two strings.
    assert rendered_a != rendered_b
    target = tmp_path / "dashboard.md"
    target.write_text(rendered_a, encoding="utf-8")
    assert rd.verify_dashboard(rendered_b, target) is True, (
        "verify must ignore generated_at drift (AC6 SC verify-only)"
    )


def test_verify_ignores_git_log_age_drift(tmp_path: Path):
    """F1 regression: relative git age (e.g. '2 minutes ago' → '5 minutes ago')
    must not trip verify."""
    base = _baseline_context()
    base_with_log = dict(base)
    base_with_log["git_log"] = [
        {"hash": "abc1234", "subject": "feat: x", "age": "2 minutes ago"},
        {"hash": "def5678", "subject": "fix: y", "age": "1 hour ago"},
    ]
    rendered_old = rd.render_dashboard(base_with_log)
    drifted = dict(base_with_log)
    drifted["git_log"] = [
        {"hash": "abc1234", "subject": "feat: x", "age": "5 minutes ago"},
        {"hash": "def5678", "subject": "fix: y", "age": "2 hours ago"},
    ]
    rendered_new = rd.render_dashboard(drifted)
    assert rendered_old != rendered_new
    target = tmp_path / "dashboard.md"
    target.write_text(rendered_old, encoding="utf-8")
    assert rd.verify_dashboard(rendered_new, target) is True


def test_verify_detects_actual_content_change(tmp_path: Path):
    """F1 negative: a real content change (task list, etc.) must still mismatch."""
    base = _baseline_context()
    target = tmp_path / "dashboard.md"
    target.write_text(rd.render_dashboard(base), encoding="utf-8")
    different = dict(base)
    different["source_commit"] = "0000000"
    assert rd.verify_dashboard(rd.render_dashboard(different), target) is False


def test_verify_against_just_written_output_is_time_stable(
    sample_tasks_dir: Path,
    sample_reports_dir: Path,
    memory_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """F1 end-to-end: write via main() → sleep → render again → verify.

    Mirrors the kuroda machine_evidence reproducer (write then sleep 2
    then --verify) without spawning a subprocess.
    """
    output = tmp_path / "dashboard_out.md"
    monkeypatch.setattr(rd, "QUEUE_TASKS_DIR", sample_tasks_dir)
    monkeypatch.setattr(rd, "QUEUE_REPORTS_DIR", sample_reports_dir)
    monkeypatch.setattr(rd, "MEMORY_FILE", memory_file)
    monkeypatch.setattr(rd, "LOCK_FILE", tmp_path / "lock")
    monkeypatch.setattr(rd, "PREFLIGHT_REPORT", tmp_path / "preflight.yaml")
    monkeypatch.setattr(rd, "ARCHIVE_DIR", tmp_path / "archive")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)

    args = [
        "--no-supabase",
        "--memory-snapshot", str(memory_file),
        "--output", str(output),
    ]
    assert rd.main(args) == 0
    # Wait long enough to advance the seconds component of generated_at.
    time.sleep(1.1)
    verify_code = rd.main(args + ["--verify"])
    assert verify_code == 0, "verify after time drift must succeed (AC6)"


# ---------------------------------------------------------------------------
# F2 cycle2: STATUS_ENUM + stage values for live audit-waiting statuses
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,expected",
    [
        ("ready_for_audit", 70.0),
        ("audit_pending", 80.0),
        ("completed_pending_audit", 85.0),
        ("done_pending_audit", 90.0),
        ("audit_pending_verification", 95.0),
        ("failed", 0.0),
        ("pending", 10.0),
    ],
)
def test_progress_stage_value_for_live_status(status: str, expected: float):
    """F2: live-queue audit-waiting statuses must map to explicit stage values
    (not be excluded as 'unknown' as cycle1 did)."""
    t = rd.TaskEntry(task_id="x", assigned_to="a", status=status, raw_status=status)
    score = rd.progress_for_task(t)
    assert score == expected, (
        f"{status} should be stage value {expected}, got {score}"
    )


def test_progress_done_without_verdict_is_75_not_zero():
    """F2: done without verdict yet must be 75% (audit awaits), not 0%."""
    t = rd.TaskEntry(task_id="x", assigned_to="a", status="done", raw_status="done")
    assert rd.progress_for_task(t) == 75.0


@pytest.fixture
def live_status_tasks_dir(tmp_path: Path) -> Path:
    """Fixture mirroring the production status set found in queue/tasks/."""
    tasks = tmp_path / "tasks"
    tasks.mkdir()
    (tasks / "ashigaru1.yaml").write_text(
        textwrap.dedent(
            """
            task:
              task_id: t_audit_pending
              assigned_to: ashigaru1
              status: audit_pending

            ---

            task:
              task_id: t_completed_pending_audit
              assigned_to: ashigaru1
              status: completed_pending_audit

            ---

            task:
              task_id: t_done_pending_audit
              assigned_to: ashigaru1
              status: done_pending_audit

            ---

            task:
              task_id: t_ready_for_audit
              assigned_to: ashigaru1
              status: ready_for_audit
            """
        ).strip(),
        encoding="utf-8",
    )
    return tasks


def test_live_status_set_no_excluded_as_unknown(
    live_status_tasks_dir: Path, sample_reports_dir: Path
):
    """F2 integration (audit recommendation): production audit-waiting statuses
    must aggregate, not become 'unknown' (which excluded them from %)."""
    state = rd.load_local_state(
        tasks_dir=live_status_tasks_dir, reports_dir=sample_reports_dir
    )
    assert state.tasks, "fixture must load 4 tasks"
    excluded = [t.task_id for t in state.tasks if rd.progress_for_task(t) is None]
    assert excluded == [], f"these must not be 'unknown': {excluded}"
    for t in state.tasks:
        score = rd.progress_for_task(t)
        assert score is not None and score > 0, (
            f"{t.task_id} ({t.raw_status}) -> {score}"
        )
    agg = rd.aggregate_progress(state.tasks)
    assert agg["leaf_count"] == 4
    assert agg["excluded_count"] == 0
    # Average of 70/80/85/90 = 81.25 → rounds to 81.2 or 81.3 depending on banker's.
    assert agg["overall_pct"] >= 80.0


# ---------------------------------------------------------------------------
# F3 cycle2: privacy result classifier (HIGH/WARN separation)
# ---------------------------------------------------------------------------


def test_classify_privacy_clean_requires_zero_warn():
    """F3: clean iff HIGH 0 AND WARN 0 — WARN-only is NOT clean."""
    assert (
        rd.classify_privacy_result([{"high": [], "warn": []}]) == rd.PRIVACY_CLEAN
    )


def test_classify_privacy_warn_only_is_warned_not_clean():
    """F3: WARN-only result must classify as 'warned'.

    Cycle1 report incorrectly called this 'CLEAN' even though privacy gate
    surfaced 4 WARN entries. New language: 'warned' communicates HIGH=0 but
    WARN>0.
    """
    result = rd.classify_privacy_result(
        [{"high": [], "warn": [{"pattern": "digit_id_candidate"}] * 4}]
    )
    assert result == rd.PRIVACY_WARNED
    assert result != rd.PRIVACY_CLEAN


def test_classify_privacy_high_is_blocked():
    """F3: any HIGH violation must be 'blocked' (release-blocker)."""
    assert (
        rd.classify_privacy_result(
            [{"high": [{"pattern": "api_key"}], "warn": []}]
        )
        == rd.PRIVACY_BLOCKED
    )


def test_classify_privacy_accepts_single_dict():
    assert (
        rd.classify_privacy_result({"high": [], "warn": []}) == rd.PRIVACY_CLEAN
    )


def test_classify_privacy_aggregates_across_files():
    """F3: WARN in any file → 'warned' even if other files are clean."""
    result = rd.classify_privacy_result(
        [
            {"high": [], "warn": []},
            {"high": [], "warn": [{"pattern": "x"}]},
        ]
    )
    assert result == rd.PRIVACY_WARNED


# ---------------------------------------------------------------------------
# F4 cycle2: archive legacy dashboard.md before generator overwrites
# ---------------------------------------------------------------------------


def test_archive_legacy_dashboard_first_run(tmp_path: Path):
    """F4: first run with hand-edited dashboard.md must archive it."""
    target = tmp_path / "dashboard.md"
    archive = tmp_path / "archive"
    target.write_text(
        "# 🏯 Multi-Agent Shogun — Dashboard\n\n手動編集 legacy 内容。\n",
        encoding="utf-8",
    )
    archived = rd._archive_legacy_dashboard(target, archive)
    assert archived is not None, "legacy dashboard must be archived"
    assert archived.exists()
    assert archived.read_text(encoding="utf-8").startswith("# 🏯 Multi-Agent Shogun")
    # Archive name format: dashboard_legacy_YYYYMMDD.md
    assert archived.name.startswith("dashboard_legacy_")
    assert archived.name.endswith(".md")


def test_archive_skipped_for_generator_output(tmp_path: Path):
    """F4: generator output must NOT be re-archived (idempotent)."""
    target = tmp_path / "dashboard.md"
    archive = tmp_path / "archive"
    target.write_text(
        "# DentalBI Dashboard (auto-generated)\n\n"
        "*Generated by scripts/regenerate_dashboard.py*\n",
        encoding="utf-8",
    )
    archived = rd._archive_legacy_dashboard(target, archive)
    assert archived is None, "generator output must not re-archive"
    assert not archive.exists() or not any(archive.iterdir())


def test_archive_skipped_when_target_absent(tmp_path: Path):
    """F4: nothing to archive when target file does not exist."""
    target = tmp_path / "no_dashboard.md"
    archive = tmp_path / "archive"
    archived = rd._archive_legacy_dashboard(target, archive)
    assert archived is None


def test_archive_dedupes_same_day(tmp_path: Path):
    """F4: multiple legacy contents in one day must each get a unique name."""
    archive = tmp_path / "archive"
    target1 = tmp_path / "dashboard.md"
    target1.write_text("legacy v1", encoding="utf-8")
    a1 = rd._archive_legacy_dashboard(target1, archive)
    # Replace with a different legacy content and archive again.
    target1.write_text("legacy v2", encoding="utf-8")
    a2 = rd._archive_legacy_dashboard(target1, archive)
    assert a1 is not None and a2 is not None
    assert a1 != a2, "second archive must get a unique suffix"
    assert a1.read_text(encoding="utf-8") == "legacy v1"
    assert a2.read_text(encoding="utf-8") == "legacy v2"


def test_write_output_archives_before_overwrite(tmp_path: Path):
    """F4 end-to-end: write_output() must archive legacy before overwriting."""
    target = tmp_path / "dashboard.md"
    archive = tmp_path / "archive"
    target.write_text("legacy hand-edited content", encoding="utf-8")
    rd.write_output(
        "# DentalBI Dashboard (auto-generated)\n\nnew content via scripts/regenerate_dashboard.py\n",
        target,
        archive_dir=archive,
    )
    # Target now holds new generator output.
    assert "auto-generated" in target.read_text(encoding="utf-8")
    # Archive holds the previous legacy content.
    archived_files = list(archive.glob("dashboard_legacy_*.md"))
    assert len(archived_files) == 1
    assert archived_files[0].read_text(encoding="utf-8") == "legacy hand-edited content"
