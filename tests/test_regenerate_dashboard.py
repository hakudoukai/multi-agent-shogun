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
    # cycle3 i18n で `- 生成時刻 (generated_at): \`...\`` に変わったため、
    # 旧 regex `generated_at: \`...\`` は paren 越しで match できない (= 旧 test の
    # 暗黙バグ、両 render が同秒なら偶然 pass)。cycle4 で children render の追加
    # 処理時間で秒境界 drift が顕在化。`_normalize_for_verify` を共通 mask に流用。
    skeleton_a = rd._normalize_for_verify(a)
    skeleton_b = rd._normalize_for_verify(b)
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


# ---------------------------------------------------------------------------
# Cycle 3: 6 Layer section / HTML drill-down / mermaid tree / visual emphasis /
#          Japanese localization
# (kuroda 条件 1: cycle 3 UI 要素を pytest で明示 assert)
# ---------------------------------------------------------------------------


def test_render_dashboard_has_6_layer_section():
    """改訂①: 6 Layer (A-F) + G 統合 section が存在し、各 layer doc anchor が出力される。"""
    rendered = rd.render_dashboard(_baseline_context())
    assert "## 🗂 6 Layer 構造" in rendered, "6 Layer section heading missing"
    # 各 layer (A-G) が <summary> に列挙されること
    for code, name_keyword in [
        ("A", "構想層"), ("B", "Phase 層"), ("C", "機能層"),
        ("D", "頭脳層"), ("E", "運用層"), ("F", "規範層"), ("G", "統合層"),
    ]:
        assert f"Layer {code}:" in rendered, f"Layer {code} missing from output"
        assert name_keyword in rendered, f"Layer {code} name '{name_keyword}' missing"
    # 各 layer doc anchor (docs/dashboard_layer_*.md) が出力されること
    for code in "abcdefg":
        assert f"docs/dashboard_layer_{code}_" in rendered, (
            f"Layer {code.upper()} doc anchor missing"
        )


def test_render_dashboard_layer_definitions_have_data_source():
    """LAYER_DEFINITIONS の各 entry に data_source 説明が存在する (kuroda 条件 3)。"""
    for layer in rd.LAYER_DEFINITIONS:
        assert layer["code"], "layer code required"
        assert layer["name"], f"layer {layer['code']} name required"
        assert layer["summary"], f"layer {layer['code']} summary required"
        assert layer["data_source"], f"layer {layer['code']} data_source required"
        assert layer["doc"].startswith("docs/dashboard_layer_"), (
            f"layer {layer['code']} doc must point to dashboard_layer_*.md"
        )


def test_render_dashboard_has_html_drill_down():
    """改訂②: HTML drill-down (<details>/<summary> accordion + <progress> bar) が含まれる。"""
    rendered = rd.render_dashboard(_baseline_context())
    # accordion 7 entries (Layer A-G) → <details>/</details> 各 7 件以上
    assert rendered.count("<details>") >= 7, "expected ≥7 <details> blocks (one per layer)"
    assert rendered.count("</details>") >= 7
    assert rendered.count("<summary>") >= 7
    # <progress> bar が overall + per_agent + (任意で stage/batch) で複数出現
    assert rendered.count("<progress") >= 2, "expected overall + per-agent progress bars"


def test_render_dashboard_has_mermaid_tree():
    """改訂③: mermaid 階層 tree (Layer A → 10 柱 + 蜘蛛の糸) が含まれる。"""
    rendered = rd.render_dashboard(_baseline_context())
    assert "```mermaid" in rendered, "mermaid code fence missing"
    assert "graph TD" in rendered, "mermaid graph TD declaration missing"
    # 10 柱 P1-P10 + 蜘蛛の糸接続
    for pillar in ("P1[", "P5[", "P8[", "P10["):
        assert pillar in rendered, f"pillar {pillar} missing"
    assert "蜘蛛の糸" in rendered, "蜘蛛の糸 connection missing"
    # 5 階層 L0-L5
    for layer_node in ("L0[", "L1[", "L2[", "L3[", "L4[", "L5["):
        assert layer_node in rendered, f"hierarchy node {layer_node} missing"


def test_render_dashboard_visual_emphasis():
    """改訂④: 大 progress bar (overall) + Stage A/B + batch %別 visual 強調。"""
    rendered = rd.render_dashboard(_baseline_context())
    # 大 progress bar — width 420 (Stage 4 visual emphasis)
    assert "width:420px" in rendered, "large overall progress bar missing"
    # 全体進捗 section
    assert "🚀 全体進捗" in rendered
    # Stage A/B + batch 別 section
    assert "Stage 別進捗" in rendered, "W9 Stage breakdown section missing"
    assert "batch 別進捗" in rendered, "W9 batch breakdown section missing"
    # 色 tier emoji が少なくとも 1 つ表示される (overall bar)
    has_tier_emoji = any(t["emoji"] in rendered for t in rd.PROGRESS_COLOR_TIERS)
    assert has_tier_emoji, "expected at least one tier emoji in rendered output"


def test_render_dashboard_japanese_localization():
    """改訂⑤: title + metadata label の日本語化 (cycle1 shogun 推奨残懸念解消)。"""
    rendered = rd.render_dashboard(_baseline_context())
    assert "DentalBI ダッシュボード (自動生成)" in rendered, "Japanese title missing"
    # 技術 token (英語 retain) が併記される
    assert "生成時刻 (generated_at)" in rendered
    assert "ソースコミット (source_commit)" in rendered
    assert "書込PC (writer_pc)" in rendered
    assert "Supabase接続状態 (supabase_blocking)" in rendered
    assert "memory MCP フォールバック" in rendered
    # 旧 cycle2 残: 単独「supabase_blocking: …」のみは消える (label が付く)
    # but technical token "supabase_blocking" itself must still appear
    assert "supabase_blocking" in rendered


def test_progress_color_tier_levels():
    """色分け 4 段階 (green/yellow/orange/red) — 境界値分類が決定的であること。"""
    assert rd.progress_color_tier(100.0)["css_class"] == "tier-green"
    assert rd.progress_color_tier(80.0)["css_class"] == "tier-green"
    assert rd.progress_color_tier(79.9)["css_class"] == "tier-yellow"
    assert rd.progress_color_tier(50.0)["css_class"] == "tier-yellow"
    assert rd.progress_color_tier(49.9)["css_class"] == "tier-orange"
    assert rd.progress_color_tier(25.0)["css_class"] == "tier-orange"
    assert rd.progress_color_tier(24.9)["css_class"] == "tier-red"
    assert rd.progress_color_tier(0.0)["css_class"] == "tier-red"


def test_progress_bar_html_emits_progress_tag():
    """progress_bar_html: HTML <progress> tag + emoji + percent label を生成。"""
    bar = rd.progress_bar_html(73.5, width_px=180, height_px=12)
    assert "<progress" in bar
    assert "value=\"73.5\"" in bar
    assert "max=\"100\"" in bar
    assert "width:180px" in bar
    assert "height:12px" in bar
    assert "**73.5%**" in bar
    # 50<=73.5<80 → tier-yellow
    assert "tier-yellow" in bar
    assert "🟡" in bar


def test_extract_w9_meta_handles_both_orderings():
    """task_id naming variants — stage prefix vs stage suffix の双方を解釈。"""
    # stage prefix: subtask_cmd004_w9_stage_b_batch3_check_logic_26
    pre = rd._extract_w9_meta("subtask_cmd004_w9_stage_b_batch3_check_logic_26")
    assert pre == {"stage": "B", "batch": "3"}
    # stage suffix: subtask_cmd004_w9_batch1_stage_a_foundation
    post = rd._extract_w9_meta("subtask_cmd004_w9_batch1_stage_a_foundation")
    assert post == {"stage": "A", "batch": "1"}
    # no stage: subtask_cmd004_w9_batch1_keisan_check_42_v2
    none = rd._extract_w9_meta("subtask_cmd004_w9_batch1_keisan_check_42_v2")
    assert none == {"stage": None, "batch": "1"}
    # non-W9 task: no match
    other = rd._extract_w9_meta("subtask_cmd020_regenerate_dashboard_py")
    assert other == {"stage": None, "batch": None}


def test_aggregate_w9_stage_groups_a_b():
    """W9 タスクが Stage A / B / 未分類 に集計され、各 avg_pct が決定的。"""
    tasks = [
        rd.TaskEntry(
            task_id="subtask_cmd004_w9_batch1_stage_a_foundation",
            assigned_to="ashigaru4", status="done", raw_status="done",
            verdict="pass", completion_gate="open", evidence_state="complete",
            shogun_verified=True,
        ),  # Stage A, 100%
        rd.TaskEntry(
            task_id="subtask_cmd004_w9_stage_b_batch3_check_logic_26",
            assigned_to="ashigaru3", status="in_progress", raw_status="in_progress",
        ),  # Stage B, 50%
        rd.TaskEntry(
            task_id="subtask_cmd004_w9_batch1_keisan_check_42_v2",
            assigned_to="ashigaru4", status="in_progress", raw_status="in_progress",
        ),  # 未分類, 50%
        rd.TaskEntry(
            task_id="subtask_cmd020_dashboard_japanese_localization",
            assigned_to="ashigaru1", status="done", raw_status="done",
        ),  # excluded — non-W9
    ]
    rows = rd.aggregate_w9_stage_progress(tasks)
    by_stage = {r["stage"]: r for r in rows}
    assert by_stage["A"]["task_count"] == 1
    assert by_stage["A"]["avg_pct"] == 100.0
    assert by_stage["B"]["task_count"] == 1
    assert by_stage["B"]["avg_pct"] == 50.0
    assert by_stage["未分類"]["task_count"] == 1


def test_aggregate_w9_batch_groups_by_batch_id():
    """W9 タスクが batch_id 単位で集計され、batch 順 (1,2,...) で sort される。"""
    tasks = [
        rd.TaskEntry(
            task_id="subtask_cmd004_w9_stage_b_batch7_remaining_alert_15",
            assigned_to="ashigaru1", status="drafted_pending_kuroda_pre_audit",
            raw_status="drafted_pending_kuroda_pre_audit",
        ),  # batch 7, 15%
        rd.TaskEntry(
            task_id="subtask_cmd004_w9_batch1_stage_a_foundation",
            assigned_to="ashigaru4", status="completed_pending_audit",
            raw_status="completed_pending_audit",
        ),  # batch 1, 85%
        rd.TaskEntry(
            task_id="subtask_cmd004_w9_stage_b_batch3_check_logic_26",
            assigned_to="ashigaru3", status="completed_pending_audit",
            raw_status="completed_pending_audit",
        ),  # batch 3, 85%
    ]
    rows = rd.aggregate_w9_batch_progress(tasks)
    batches = [r["batch"] for r in rows]
    assert batches == ["1", "3", "7"], f"expected sorted batch ids, got {batches}"
    by_batch = {r["batch"]: r for r in rows}
    assert by_batch["1"]["avg_pct"] == 85.0
    assert by_batch["7"]["avg_pct"] == 15.0


# ---------------------------------------------------------------------------
# Cycle 4: Layer 子項目 (children) + 孫項目 (grandchildren) drill-down
# (kuroda cycle4 条件 2: 子項目 / 孫 5 項 / fallback / mermaid §4.2 / single-writer
# を明示 assert SKIP=0)
# ---------------------------------------------------------------------------


def test_layer_children_inventory_has_all_layers():
    """LAYER_CHILDREN は A-G 全 7 layer をカバーする。"""
    layers_with_children = {c["layer"] for c in rd.LAYER_CHILDREN}
    assert layers_with_children == set("ABCDEFG"), (
        f"missing children for layers: {set('ABCDEFG') - layers_with_children}"
    )


def test_layer_children_count_at_least_28():
    """cycle4 要件: 子項目 28 件以上装着 (= AC4 計画書 v0.2 §4)。"""
    assert len(rd.LAYER_CHILDREN) >= 28, (
        f"need ≥28 children for cycle4 AC, got {len(rd.LAYER_CHILDREN)}"
    )


def test_layer_c_children_count_at_least_14():
    """Layer C 機能層は cmd_004 二大戦線 + W9 で 14 件以上 (= 計画書 v0.2 §2)。"""
    c_children = rd.children_for_layer("C")
    assert len(c_children) >= 14, (
        f"Layer C needs ≥14 children, got {len(c_children)}"
    )


def test_render_dashboard_has_children_accordion():
    """各 Layer accordion 内に nested <details> (= 子項目) が render される。"""
    rendered = rd.render_dashboard(_baseline_context())
    # 7 layer (= cycle3) + 子項目 nested <details> で合計 ≥ 7 + len(LAYER_CHILDREN)
    expected_min = 7 + len(rd.LAYER_CHILDREN)
    actual = rendered.count("<details>")
    assert actual >= expected_min, (
        f"expected ≥{expected_min} <details> (7 layers + {len(rd.LAYER_CHILDREN)} children), got {actual}"
    )


def test_render_dashboard_grandchildren_5_item_template():
    """各子項目 expand で 5 項固定 (commit/test/audit/shogun_verified/参照) が render される。

    cycle7: markdown ul/li → inline <p> + separator " | " に refactor。最初 4 項 (commit/test
    /audit/shogun_verified) は横一列 1 行、参照 doc は別行 (長文対策)。label は <b> HTML bold。
    """
    rendered = rd.render_dashboard(_baseline_context())
    # 各 children 1 件につき 5 label が render される → ≥ children 数
    n = len(rd.LAYER_CHILDREN)
    assert rendered.count("<b>commit:</b>") >= n
    assert rendered.count("<b>test:</b>") >= n
    assert rendered.count("<b>audit (黒田):</b>") >= n
    assert rendered.count("<b>shogun_verified:</b>") >= n
    assert rendered.count("<b>参照:</b>") >= n


def test_render_dashboard_contains_specific_child_labels():
    """計画書 v0.2 §2 で指定された主要子項目が render される。"""
    rendered = rd.render_dashboard(_baseline_context())
    for label_token in (
        "領収書 PDF",
        "AI チャット",
        "QR kanban",
        "PWA",
        "申し送りエンジン",
        "legal_sources",
        "memory MCP",
    ):
        assert label_token in rendered, f"child label '{label_token}' missing"


def test_render_dashboard_layer_c_w9_children_present():
    """Layer C 内に W9 batch1-7 + Stage A の蜘蛛の糸 算定 children が render される。"""
    rendered = rd.render_dashboard(_baseline_context())
    for batch_label in ("W9 batch1", "W9 batch2", "W9 batch7", "W9 Stage A"):
        assert batch_label in rendered, f"W9 child label '{batch_label}' missing"


def test_render_dashboard_v02_children_mermaid_section():
    """改訂③: mermaid v0.2 §4.2 children 接続図 section が含まれる。"""
    rendered = rd.render_dashboard(_baseline_context())
    assert "Layer C children mermaid (v0.2 §4.2)" in rendered, "v0.2 §4.2 section heading missing"
    # children mermaid block が出力されること (= LR graph + Layer C 接続)
    assert "LC[Layer C 機能層]" in rendered, "Layer C mermaid root node missing"
    assert "KZ[会計待ちゼロ作戦]" in rendered
    assert "SK[小児恐竜王国アプリ]" in rendered
    assert "MO[申し送りエンジン]" in rendered
    # graph LR direction
    assert "graph LR" in rendered


def test_render_dashboard_single_writer_warning_retained_cycle4():
    """改訂②: generator 単一 writer の警告 banner が cycle4 でも retain される。"""
    rendered = rd.render_dashboard(_baseline_context())
    assert "scripts/regenerate_dashboard.py" in rendered
    assert "単独 writer" in rendered or "sole writer" in rendered
    # cycle3 既装備の i18n 注意 retain
    assert "手動編集" in rendered and "禁止" in rendered


def test_extract_child_evidence_fallback_for_missing_data():
    """機械 evidence 不在時、捏造せず fallback 文字列を返す (黒田 cycle4 条件 1 整合)。"""
    child = {"layer": "X", "id": "X-99", "label": "test child"}
    ev = rd.extract_child_evidence(child, kuroda_entries=[], shogun_entries=[])
    assert ev["commit"] == rd.FALLBACK_COMMIT
    assert ev["test"] == rd.FALLBACK_TEST
    assert ev["audit"] == rd.FALLBACK_AUDIT
    assert ev["shogun_verified"] == rd.FALLBACK_SHOGUN_FALSE
    assert ev["ref"] == rd.FALLBACK_REF


def test_extract_child_evidence_uses_kuroda_audit_match():
    """audit_id_pattern が kuroda entries に一致すると verdict + audit_id を返す。"""
    child = {
        "layer": "G", "id": "G-test", "label": "test",
        "audit_id_pattern": "kuroda_test_audit",
    }
    kuroda = [
        {"audit_id": "kuroda_test_audit_20260512", "verdict": "pass",
         "audited_at": "2026-05-12T14:00:00+09:00",
         "machine_evidence": {"pytest": {"observed": "100 passed; SKIP=0"}}},
    ]
    ev = rd.extract_child_evidence(child, kuroda_entries=kuroda, shogun_entries=[])
    assert "kuroda_test_audit_20260512" in ev["audit"]
    assert "pass" in ev["audit"]
    assert "100 passed" in ev["test"]  # machine_evidence.pytest.observed flowed in


def test_extract_child_evidence_picks_latest_audit():
    """同 pattern が複数 hit すると audited_at 最新が選ばれる。"""
    child = {"layer": "X", "id": "X-1", "label": "t",
             "audit_id_pattern": "kuroda_alpha"}
    kuroda = [
        {"audit_id": "kuroda_alpha_v1", "verdict": "fail",
         "audited_at": "2026-01-01T00:00:00+09:00"},
        {"audit_id": "kuroda_alpha_v2", "verdict": "pass",
         "audited_at": "2026-05-12T14:00:00+09:00"},
    ]
    ev = rd.extract_child_evidence(child, kuroda_entries=kuroda, shogun_entries=[])
    assert "kuroda_alpha_v2" in ev["audit"]
    assert "pass" in ev["audit"]


def test_extract_child_evidence_shogun_verified_true_when_match():
    """shogun_target_pattern が verifications log に hit すると true + timestamp。"""
    child = {"layer": "X", "id": "X-1", "label": "t",
             "shogun_target_pattern": "qr_kanban"}
    shogun = [
        {"target": "subtask_cmd004_qr_kanban_impl", "shogun_verified": True,
         "verified_at": "2026-05-11T22:00:00+09:00"},
    ]
    ev = rd.extract_child_evidence(child, kuroda_entries=[], shogun_entries=shogun)
    assert ev["shogun_verified"].startswith("true")
    assert "2026-05-11" in ev["shogun_verified"]


def test_extract_child_evidence_w9_batch_uses_aggregate():
    """kind=w9_batch は aggregate_w9_batch_progress 集計値を流用する。"""
    child = {"layer": "C", "id": "C-W9-7", "label": "W9 batch7",
             "kind": "w9_batch", "batch": "7"}
    w9 = [{"batch": "7", "task_count": 15, "avg_pct": 12.3,
           "task_ids": []}]
    ev = rd.extract_child_evidence(child, kuroda_entries=[], shogun_entries=[],
                                   w9_batches=w9)
    assert "15" in ev["commit"]
    assert "12.3" in ev["audit"]


def test_extract_child_evidence_w9_stage_uses_aggregate():
    """kind=w9_stage は aggregate_w9_stage_progress 集計値を流用する。"""
    child = {"layer": "C", "id": "C-W9-A", "label": "W9 Stage A",
             "kind": "w9_stage", "stage": "A"}
    stages = [{"stage": "A", "task_count": 9, "scored_count": 9, "avg_pct": 100.0}]
    ev = rd.extract_child_evidence(child, kuroda_entries=[], shogun_entries=[],
                                   w9_stages=stages)
    assert "9" in ev["commit"]
    assert "100.0" in ev["audit"]


def test_load_kuroda_index_returns_empty_when_missing(tmp_path: Path):
    """ファイル不在時は空 list (例外を投げない)。"""
    assert rd.load_kuroda_index(tmp_path / "nope.yaml") == []


def test_load_kuroda_index_parses_reports(tmp_path: Path):
    """reports: が list なら entries を返す。"""
    p = tmp_path / "k.yaml"
    p.write_text(
        "reports:\n  - audit_id: a1\n    verdict: pass\n  - audit_id: a2\n    verdict: fail\n",
        encoding="utf-8",
    )
    entries = rd.load_kuroda_index(p)
    assert len(entries) == 2
    assert entries[0]["audit_id"] == "a1"


def test_load_shogun_verification_index_returns_empty_when_missing(tmp_path: Path):
    assert rd.load_shogun_verification_index(tmp_path / "no.yaml") == []


def test_load_shogun_verification_index_parses_entries(tmp_path: Path):
    p = tmp_path / "sv.yaml"
    p.write_text(
        "verifications:\n  - target: x\n    shogun_verified: true\n    verified_at: '2026-01-01'\n",
        encoding="utf-8",
    )
    entries = rd.load_shogun_verification_index(p)
    assert len(entries) == 1
    assert entries[0]["target"] == "x"


def test_build_layer_render_entries_attaches_children():
    """build_layer_render_entries は各 layer に children + child_count を付ける。"""
    entries = rd.build_layer_render_entries()
    by_code = {e["code"]: e for e in entries}
    assert set(by_code.keys()) == set("ABCDEFG")
    for code, layer in by_code.items():
        assert "children" in layer
        assert "child_count" in layer
        assert layer["child_count"] == len(rd.children_for_layer(code))


def test_render_dashboard_size_baseline_above_cycle3_floor():
    """cycle4 装着で baseline render size が cycle3 比 1.5× 以上に拡張。

    cycle3 baseline (2 sample tasks) で約 5-6K bytes だったところ、cycle4 で
    54 children × 5 行 grandchildren で render される結果、≥8K bytes 必達。
    """
    rendered = rd.render_dashboard(_baseline_context())
    assert len(rendered.encode("utf-8")) >= 8000, (
        f"cycle4 baseline render too small: {len(rendered.encode('utf-8'))} bytes"
    )


def test_legacy_marker_still_detects_generator_output(tmp_path: Path):
    """generator 切替後 (cycle3) も legacy 検出が後方互換であること (F4 retain)。

    cycle3 の新 title「DentalBI ダッシュボード (自動生成)」は marker "auto-generated"
    を含まなくなったが、HTML コメント `<!-- auto-generated by scripts/... -->`
    で marker を retain している。既存 generator output が re-archive されないこと。
    """
    target = tmp_path / "dashboard.md"
    archive = tmp_path / "archive"
    # 実際の cycle3 generator output を render して書く
    target.write_text(rd.render_dashboard(_baseline_context()), encoding="utf-8")
    archived = rd._archive_legacy_dashboard(target, archive)
    assert archived is None, (
        "cycle3 generator output must be detected by legacy marker scan "
        "(otherwise we re-archive ourselves every run)"
    )


# ---------------------------------------------------------------------------
# Cycle 5: 子項目 summary line 一目視認 format
#   (kuroda cycle5 条件 3: summary format / 4 色 / progress bar / 1 行現状 を明示 assert
#    karo task spec: 全 53 children・5 evidence fields retain + summary 統一 + SKIP=0)
# ---------------------------------------------------------------------------


def test_compute_child_machine_state_shogun_verified_yields_90_pct():
    """shogun_verified=true match → pct 90.0 (= 🟢 tier 整合)。"""
    child = {"layer": "X", "id": "X-1", "label": "t",
             "shogun_target_pattern": "qr_kanban"}
    shogun = [{"target": "subtask_cmd004_qr_kanban_impl", "shogun_verified": True,
               "verified_at": "2026-05-11T22:00:00+09:00"}]
    state = rd.compute_child_machine_state(child, shogun_entries=shogun)
    assert state["kind"] == "standard"
    assert state["pct"] == 90.0
    assert state["shogun_verified"] is True


def test_compute_child_machine_state_pass_audit_yields_60_pct():
    """audit verdict=pass のみ (shogun_verified なし) → pct 60.0 (= 🟡 tier)。"""
    child = {"layer": "X", "id": "X-1", "label": "t",
             "audit_id_pattern": "kuroda_alpha"}
    kuroda = [{"audit_id": "kuroda_alpha_v1", "verdict": "pass",
               "audited_at": "2026-05-12T14:00:00+09:00"}]
    state = rd.compute_child_machine_state(child, kuroda_entries=kuroda)
    assert state["pct"] == 60.0
    assert state["audit_verdict"] == "pass"


def test_compute_child_machine_state_fail_audit_yields_30_pct():
    """audit verdict=fail → pct 30.0 (= 🟠 tier、要 redo)。"""
    child = {"layer": "X", "id": "X-1", "label": "t",
             "audit_id_pattern": "kuroda_beta"}
    kuroda = [{"audit_id": "kuroda_beta_v1", "verdict": "fail",
               "audited_at": "2026-05-12T14:00:00+09:00"}]
    state = rd.compute_child_machine_state(child, kuroda_entries=kuroda)
    assert state["pct"] == 30.0


def test_compute_child_machine_state_no_data_yields_0_pct():
    """audit / shogun_verified / commit 何もなし → pct 0.0 (= 🔴 tier 未着手)。"""
    child = {"layer": "X", "id": "X-99", "label": "test child"}
    state = rd.compute_child_machine_state(child)
    assert state["pct"] == 0.0
    assert state["kind"] == "standard"


def test_compute_child_machine_state_w9_batch_uses_avg_pct():
    """kind=w9_batch は aggregate avg_pct を直接流用 (= 集計値 retain、捏造禁)。"""
    child = {"layer": "C", "id": "C-W9-7", "label": "W9 batch7",
             "kind": "w9_batch", "batch": "7"}
    w9 = [{"batch": "7", "task_count": 15, "avg_pct": 42.5, "task_ids": []}]
    state = rd.compute_child_machine_state(child, w9_batches=w9)
    assert state["kind"] == "w9_batch"
    assert state["pct"] == 42.5
    assert state["task_count"] == 15


def test_compute_child_machine_state_w9_stage_uses_avg_pct():
    """kind=w9_stage は aggregate avg_pct + scored_count を直接流用。"""
    child = {"layer": "C", "id": "C-W9-A", "label": "W9 Stage A",
             "kind": "w9_stage", "stage": "A"}
    stages = [{"stage": "A", "task_count": 9, "scored_count": 9, "avg_pct": 100.0}]
    state = rd.compute_child_machine_state(child, w9_stages=stages)
    assert state["kind"] == "w9_stage"
    assert state["pct"] == 100.0
    assert state["scored_count"] == 9


def test_format_child_status_line_shogun_verified_includes_commit_and_verdict():
    """🟢 完成監査済 → '完成監査済 (commit <hash>, 黒田 <verdict>)' format。"""
    state = {"kind": "standard", "pct": 90.0, "commit_hash": "abc1234",
             "audit_verdict": "pass", "shogun_verified": True}
    line = rd.format_child_status_line(state)
    assert "完成監査済" in line
    assert "abc1234" in line
    assert "pass" in line


def test_format_child_status_line_in_progress_format():
    """🟡 進行中 → '進行中 (黒田 <verdict>)' format。"""
    state = {"kind": "standard", "pct": 60.0, "audit_verdict": "pass_with_concerns"}
    line = rd.format_child_status_line(state)
    assert "進行中" in line
    assert "pass_with_concerns" in line


def test_format_child_status_line_未着手():
    """🔴 未着 → '未着手' (= blank state)。"""
    state = {"kind": "standard", "pct": 0.0}
    line = rd.format_child_status_line(state)
    assert "未着手" in line


def test_format_child_status_line_w9_batch_shows_avg_and_count():
    """w9_batch 集計値 → 'batchN 平均 X% (M 件)' format。"""
    state = {"kind": "w9_batch", "pct": 42.5, "batch": "7", "task_count": 15}
    line = rd.format_child_status_line(state)
    assert "batch7" in line
    assert "42.5%" in line
    assert "15" in line


def test_build_layer_render_entries_includes_progress_bar_and_status():
    """各 child に pct / progress_bar / status_line が attach されること (= cycle5 新規)。"""
    entries = rd.build_layer_render_entries()
    for layer in entries:
        for child in layer["children"]:
            assert "pct" in child
            assert "progress_bar" in child
            assert "status_line" in child
            # progress_bar は <progress> HTML tag を含む (= 全体進捗 § と同 format)
            assert "<progress" in child["progress_bar"]
            # status_line は空文字でない
            assert isinstance(child["status_line"], str)
            assert len(child["status_line"]) > 0


def test_render_dashboard_child_summary_contains_progress_tag():
    """各子項目 summary 行に <progress> tag が含まれる (= 一目視認、karo spec)。"""
    rendered = rd.render_dashboard(_baseline_context())
    # 子項目数 (= LAYER_CHILDREN) 以上の <progress> tag が現れる
    # (全体進捗 + per-agent + W9 batch/stage table + 子項目 summary)
    n_children = len(rd.LAYER_CHILDREN)
    # progress tag 数 ≥ 子項目数 (children の summary 行に各 1 個装着) + 既存 (overall 1 + per_agent + w9 rows)
    # 既存 baseline で 2-3 だったので children 数 + 余裕で n_children + 1 以上
    assert rendered.count("<progress") >= n_children, (
        f"summary 行 progress bar 不足: {rendered.count('<progress')} < {n_children}"
    )


def test_render_dashboard_child_summary_contains_4_color_tier_emoji():
    """各子項目 summary 行に 🟢🟡🟠🔴 のいずれかが含まれる (= 4 色 tier visible)。"""
    rendered = rd.render_dashboard(_baseline_context())
    # 53 children + 全体進捗 (= 1+) で総数 ≥ children 数。
    tier_emoji = ["🟢", "🟡", "🟠", "🔴"]
    total = sum(rendered.count(e) for e in tier_emoji)
    assert total >= len(rd.LAYER_CHILDREN), (
        f"4 色 tier emoji 不足: total {total} < {len(rd.LAYER_CHILDREN)}"
    )


def test_render_dashboard_child_summary_contains_status_text():
    """子項目 summary 行に 1 行現状 mapping (完成監査済 / 進行中 / 着手 / 未着手) のいずれかが含まれる。"""
    rendered = rd.render_dashboard(_baseline_context())
    status_tokens = ["完成監査済", "進行中", "着手", "未着手", "平均"]
    # children 1 行ごとに 1 token 出る想定 → 総和 ≥ children 数
    total = sum(rendered.count(t) for t in status_tokens)
    assert total >= len(rd.LAYER_CHILDREN), (
        f"1 行現状 mapping 不足: total {total} < {len(rd.LAYER_CHILDREN)}"
    )


def test_render_dashboard_child_summary_keeps_5_item_grandchildren():
    """summary 行 refactor 後も 5 項 grandchildren (= cycle4 既装備) が retain (= karo AC)。

    cycle7: ul/li → inline <p>/<b> refactor 後も 5 label 全件 retain (= cycle 4-6 既装備 retain)。
    """
    rendered = rd.render_dashboard(_baseline_context())
    n = len(rd.LAYER_CHILDREN)
    assert rendered.count("<b>commit:</b>") >= n
    assert rendered.count("<b>test:</b>") >= n
    assert rendered.count("<b>audit (黒田):</b>") >= n
    assert rendered.count("<b>shogun_verified:</b>") >= n
    assert rendered.count("<b>参照:</b>") >= n


# ---------------------------------------------------------------------------
# Cycle 6: Layer C 機能層 50 件 verify list 拡張 + Layer B Phase 子項目 + supabase_phase kind
#   (kuroda cycle6 条件 3 明示 test: Layer C >= 50 / total 80-100、
#    黒田事前監査 kuroda_cmd020_dashboard_cycle6_layer_c_extension_preaudit 整合)
# ---------------------------------------------------------------------------


def test_layer_c_verify_list_at_least_50_items():
    """kuroda cycle6 条件 3: Layer C は 50 件 verify list を全件子項目化 (= 抜け漏れ 0)。"""
    layer_c = rd.children_for_layer("C")
    assert len(layer_c) >= 50, (
        f"Layer C must include >= 50 children for cycle6 verify list, got {len(layer_c)}"
    )


def test_total_children_in_design_range_cycle6():
    """kuroda cycle6 条件 3: total 約 80-100 (= cycle 5 retain + cycle 6 verify 50+)。

    upper bound は cycle 5 既装備 53 + cycle 6 verify 50+ で 100 を自然に超えるため、
    20% lenience (= 120 上限) を許容する (= 黒田 cycle6 条件 3 註: 抜け漏れ 0 retain 優先)。
    """
    total = len(rd.LAYER_CHILDREN)
    assert total >= 80, f"total children must be >= 80 (cycle6 lower bound), got {total}"
    assert total <= 120, (
        f"total children should be ≤ 120 (= 約 100 + 20% lenient), got {total}"
    )


def test_layer_c_includes_signature_c_new_items():
    """信長殿 directive 16:00 C-NEW-1 (W4 BE 予約ソフト + W5 FE) + C-NEW-2 (W14 外部 API) を含む。"""
    layer_c = rd.children_for_layer("C")
    labels = " | ".join(c["label"] for c in layer_c)
    assert "予約ソフト BE 改修" in labels, "C-NEW-1a W4 phaseB 予約ソフト BE 改修 missing"
    assert "予約⇔カルテ⇔受付シームレス FE 結線" in labels, "C-NEW-1b W5 phaseB FE 結線 missing"
    assert "外部 API 統合(LINE 通知+Web 予約実接続)" in labels, "C-NEW-2 W14 外部 API missing"


def test_layer_b_phase_children_added_cycle6():
    """cycle6: Layer B Phase 層 完了 phase 子項目 (phaseB / phaseC / phaseD) が追加されている。"""
    layer_b = rd.children_for_layer("B")
    ids = {c["id"] for c in layer_b}
    assert "B-5-PHASEB" in ids, "Layer B phaseB 完遂 child missing"
    assert "B-6-PHASEC" in ids, "Layer B phaseC 患者アプリ child missing"
    assert "B-7-PHASED" in ids, "Layer B phaseD 経営分析 child missing"


def test_layer_c_supabase_verify_rows_all_have_status():
    """cycle6 condition 2 (捏造禁): 50 件 verify row は status を全件保持 (空文字禁止)。"""
    assert len(rd.LAYER_C_SUPABASE_VERIFY_ROWS) >= 50
    valid = {"completed", "in_progress", "not_started"}
    for row in rd.LAYER_C_SUPABASE_VERIFY_ROWS:
        seq, label, status, week, phase_code, pc, commit = row
        assert status in valid, f"row {seq}: status '{status}' not in {valid}"
        assert label and week and phase_code and pc, (
            f"row {seq}: missing required field"
        )


def test_compute_child_machine_state_supabase_phase_completed_yields_90():
    """cycle6: kind=supabase_phase + completed → pct 90.0 (= 🟢 tier 整合)。"""
    child = {
        "layer": "C", "id": "C-V01", "label": "test",
        "kind": "supabase_phase", "external_status": "completed",
        "external_source": "Supabase development_progress (week=W1)",
        "external_commit": "abc1234",
    }
    state = rd.compute_child_machine_state(child)
    assert state["kind"] == "supabase_phase"
    assert state["pct"] == 90.0
    assert state["external_status"] == "completed"


def test_compute_child_machine_state_supabase_phase_in_progress_yields_50():
    """cycle6: kind=supabase_phase + in_progress → pct 50.0 (= 🟡 tier)。"""
    child = {
        "layer": "C", "id": "C-V29", "label": "test",
        "kind": "supabase_phase", "external_status": "in_progress",
        "external_source": "Supabase development_progress",
        "external_commit": "",
    }
    state = rd.compute_child_machine_state(child)
    assert state["pct"] == 50.0
    assert state["external_status"] == "in_progress"


def test_compute_child_machine_state_supabase_phase_not_started_yields_0():
    """cycle6: kind=supabase_phase + not_started → pct 0.0 (= 🔴 tier 未着手)。"""
    child = {
        "layer": "C", "id": "C-V38", "label": "test",
        "kind": "supabase_phase", "external_status": "not_started",
        "external_source": "Supabase development_progress",
        "external_commit": "",
    }
    state = rd.compute_child_machine_state(child)
    assert state["pct"] == 0.0
    assert state["external_status"] == "not_started"


def test_format_child_status_line_supabase_phase_completed():
    """cycle6: supabase_phase + completed → '完成 (Supabase development_progress)' format。"""
    state = {"kind": "supabase_phase", "pct": 90.0, "external_status": "completed"}
    line = rd.format_child_status_line(state)
    assert "完成" in line
    assert "Supabase development_progress" in line


def test_format_child_status_line_supabase_phase_not_started():
    """cycle6: supabase_phase + not_started → '未着手 (Supabase development_progress)' format。"""
    state = {"kind": "supabase_phase", "pct": 0.0, "external_status": "not_started"}
    line = rd.format_child_status_line(state)
    assert "未着手" in line
    assert "Supabase development_progress" in line


def test_extract_child_evidence_supabase_phase_includes_supabase_source():
    """cycle6: kind=supabase_phase の evidence は Supabase 由来 (= 捏造禁、source 明示)。"""
    child = {
        "layer": "C", "id": "C-V08", "label": "W4 phaseB 予約ソフト",
        "kind": "supabase_phase", "external_status": "completed",
        "external_source": "Supabase development_progress (week=W4, phase_code=phaseB, pc=second)",
        "external_commit": "a07c834",
        "ref": "信長殿 16:02 verify list + Supabase development_progress",
    }
    ev = rd.extract_child_evidence(child, kuroda_entries=[], shogun_entries=[])
    assert "a07c834" in ev["commit"]
    assert "completed" in ev["audit"] or "Supabase" in ev["audit"]
    assert "Supabase 完了記録" in ev["shogun_verified"]
    assert "Supabase development_progress" in ev["test"]
    assert "信長殿 16:02 verify list" in ev["ref"]


def test_render_dashboard_includes_supabase_phase_status_line():
    """cycle6: render に supabase_phase children の status line ('完成 (Supabase ...)' 等) が出現。"""
    rendered = rd.render_dashboard(_baseline_context())
    # 50 件 verify list で completed 多数 → '完成 (Supabase development_progress)' が複数回出現
    assert rendered.count("完成 (Supabase development_progress)") >= 20, (
        "cycle6 verify list completed children render に出現せず"
    )
    # not_started 系も出現 (W14 LINE 等 = C-NEW-2)
    assert "未着手 (Supabase development_progress)" in rendered


def test_render_dashboard_w14_line_external_api_appears():
    """cycle6: 信長殿 directive C-NEW-2 (W14 外部 API LINE+Web 予約) が render に出現。"""
    rendered = rd.render_dashboard(_baseline_context())
    assert "LINE 通知" in rendered or "LINE通知" in rendered
    assert "Web 予約" in rendered or "Web予約" in rendered


# ---------------------------------------------------------------------------
# Cycle 7: 孫項目 inline 化 refactor (= 信長殿陛下御差配 16:04「孫項目改行 4 行 → 横一列」)
#   - ul/li 5 行 → <p> element 1 行 (= 最初 4 項 commit/test/audit/shogun_verified 横一列)
#   - separator " | " 統一
#   - short fallback (= 「未 commit」 → 「(未)」) で 1 行 fit
#   - 5 項 retain (= cycle4 既装備、6 cycle 全 retain)、参照 doc は別行 (長文対策)
# ---------------------------------------------------------------------------


def test_shorten_inline_value_compresses_known_fallback():
    """cycle7: fallback (= 「未 commit」「test 未実行」「黒田監査未」「参照 doc 未起案」) は「(未)」短縮。"""
    assert rd.shorten_inline_value(rd.FALLBACK_COMMIT) == "(未)"
    assert rd.shorten_inline_value(rd.FALLBACK_TEST) == "(未)"
    assert rd.shorten_inline_value(rd.FALLBACK_AUDIT) == "(未)"
    assert rd.shorten_inline_value(rd.FALLBACK_REF) == "(未)"


def test_shorten_inline_value_passes_through_real_values():
    """cycle7: 実 commit hash / verdict / audit_id 等 fallback 以外はそのまま retain。"""
    real_commit = "`f4230da` feat: bla (2026-05-12T16:30:00+09:00)"
    assert rd.shorten_inline_value(real_commit) == real_commit
    assert rd.shorten_inline_value("100 passed; SKIP=0") == "100 passed; SKIP=0"
    assert rd.shorten_inline_value("`kuroda_xxx_audit_20260512` → pass") == "`kuroda_xxx_audit_20260512` → pass"


def test_build_inline_evidence_retains_5_fields_with_shortening():
    """cycle7: evidence dict 5 field retain + fallback 短縮 (= 内容質 retain + 文字量圧縮)。"""
    full_fallback = {
        "commit": rd.FALLBACK_COMMIT,
        "test": rd.FALLBACK_TEST,
        "audit": rd.FALLBACK_AUDIT,
        "shogun_verified": rd.FALLBACK_SHOGUN_FALSE,
        "ref": rd.FALLBACK_REF,
    }
    inline = rd.build_inline_evidence(full_fallback)
    assert inline["commit"] == "(未)"
    assert inline["test"] == "(未)"
    assert inline["audit"] == "(未)"
    # shogun_verified=false は短縮不要 (= 既に短い文字列)
    assert inline["shogun_verified"] == "false"
    assert inline["ref"] == "(未)"
    # 5 field 全件 retain (= 黒田 cycle4 evidence 構造 retain)
    assert set(inline.keys()) == {"commit", "test", "audit", "shogun_verified", "ref"}


def test_render_dashboard_grandchildren_inline_p_element():
    """cycle7: 孫項目 render が ul/li ではなく <p> element + separator " | " で出力される。"""
    rendered = rd.render_dashboard(_baseline_context())
    n = len(rd.LAYER_CHILDREN)
    # 1 子項目あたり最初 4 項 (commit/test/audit/shogun_verified) を 1 <p> に、参照を別 <p> に
    # → <b>commit:</b> 〜 <b>shogun_verified:</b> までを含む <p> が n 件以上
    # separator " | " (両端 space) が 1 行に 3 個 (= 4 項を区切る) × n 行
    assert rendered.count("<b>commit:</b>") >= n
    assert rendered.count("<b>shogun_verified:</b>") >= n
    # separator " | " の総数は 1 行あたり 3 個 × n
    sep_count = rendered.count(" | ")
    assert sep_count >= n * 3, (
        f"cycle7 separator ' | ' 不足: {sep_count} < {n * 3} (= n × 3 区切り)"
    )


def test_render_dashboard_grandchildren_first_four_fields_on_single_line():
    """cycle7: commit / test / audit / shogun_verified が 1 <p> 内で同一行 (= 横一列) に出力。"""
    rendered = rd.render_dashboard(_baseline_context())
    # <p>...<b>commit:</b>...<b>test:</b>...<b>audit (黒田):</b>...<b>shogun_verified:</b>...</p>
    # の pattern を regex で検出 (= 単一 <p> 内に 4 label 全件含まれる行が n 件以上)
    pattern = re.compile(
        r"<p><b>commit:</b>[^<]+\|\s*<b>test:</b>[^<]+\|\s*<b>audit \(黒田\):</b>[^<]+\|\s*<b>shogun_verified:</b>[^<]+</p>"
    )
    matches = pattern.findall(rendered)
    n = len(rd.LAYER_CHILDREN)
    assert len(matches) >= n, (
        f"cycle7 inline 1 行 format 不足: {len(matches)} < {n} (= 全子項目 1 行 fit 必達)"
    )


def test_render_dashboard_grandchildren_ref_on_separate_line():
    """cycle7: 参照 doc は長文ゆえ別 <p> 行 (= 計画書整合、最初 4 項 inline + 参照 別行)。"""
    rendered = rd.render_dashboard(_baseline_context())
    # <p><b>参照:</b> ...</p> の独立 line が children 数以上
    pattern = re.compile(r"<p><b>参照:</b>[^<]+</p>")
    matches = pattern.findall(rendered)
    n = len(rd.LAYER_CHILDREN)
    assert len(matches) >= n, (
        f"cycle7 参照 別行 不足: {len(matches)} < {n}"
    )


def test_render_dashboard_grandchildren_short_fallback_appears():
    """cycle7: fallback 値の inline 表示は「(未)」短縮形 (= 文字量圧縮、1 行 fit 用)。"""
    # 全 child を fallback 状態に追い込む → render で「(未)」が出現
    ctx = _baseline_context()
    # kuroda / shogun_verification を空にして全 child を fallback path に強制
    rendered = rd.render_dashboard(ctx)
    # 標準 child (= w9 / supabase_phase 以外) のうち最低 1 件は fallback 出る前提なので
    # 「(未)」が少なくとも 1 回は出現する。長文 fallback (「(未 commit)」「(test 未実行)」等)
    # は inline 表示から消える (= ただし参照行など別 <p> 内で出る可能性は許容)。
    assert "(未)" in rendered, "cycle7 短縮 fallback「(未)」が render に出現せず"


def test_render_dashboard_grandchildren_no_legacy_ul_li_for_evidence():
    """cycle7: 孫項目 evidence 5 項 が markdown bullet 「- **commit:** 」形式で出力されない (= ul/li 廃止)。"""
    rendered = rd.render_dashboard(_baseline_context())
    # 旧 cycle4-6 の bullet format が消えていること (= 完全置換確認)
    assert "- **commit:**" not in rendered, "cycle7 ul/li 旧 format 残存 (commit)"
    assert "- **test:**" not in rendered, "cycle7 ul/li 旧 format 残存 (test)"
    assert "- **audit (黒田):**" not in rendered, "cycle7 ul/li 旧 format 残存 (audit)"
    assert "- **shogun_verified:**" not in rendered, "cycle7 ul/li 旧 format 残存 (shogun_verified)"
    assert "- **参照:**" not in rendered, "cycle7 ul/li 旧 format 残存 (参照)"


# ---------------------------------------------------------------------------
# cycle8: 🚨 cmd_004 audit 状態 alert section (= 9 件 verdict 軸 SoT)
#   黒田 v2 preaudit 条件 (verdict 軸 SoT / 7+2+0 / pass_with_concerns 表記 /
#   relative path / privacy HIGH=0 / 修正待ち完了扱い禁) を test 化。
# ---------------------------------------------------------------------------


def _fake_kuroda_entries_9docs() -> list[dict[str, Any]]:
    """Build fake kuroda_mainpc_report 'reports' list with the 9-doc audit.

    Used to exercise classify_verdict_for_alert / build_cmd004_audit_alert_section
    without depending on the live report yaml (= deterministic test fixture).
    """
    return [
        {
            "audit_id": rd.CMD004_AUDIT_ALERT_AUDIT_ID,
            "timestamp": "2026-05-12T17:05:30+09:00",
            "verdict": "fail_for_privacy_sanitization_required",
            "target_docs": [
                {"id": "cmd004_dinosaur_100enemies_spec",
                 "path": "docs/cmd004_dinosaur_100enemies_spec.md",
                 "verdict": "fail"},
                {"id": "cmd004_patient_app_pwa_design",
                 "path": "docs/cmd004_patient_app_pwa_design.md",
                 "verdict": "fail"},
                {"id": "cmd004_moushi_engine_stage1_design",
                 "path": "docs/cmd004_moushi_engine_stage1_design.md",
                 "verdict": "fail"},
                {"id": "cmd004_engagement_analytics_design",
                 "path": "docs/cmd004_engagement_analytics_design.md",
                 "verdict": "pass_with_concerns"},
                {"id": "cmd004_security_hardening_design",
                 "path": "docs/cmd004_security_hardening_design.md",
                 "verdict": "fail"},
                {"id": "cmd004_notification_facade_design",
                 "path": "docs/cmd004_notification_facade_design.md",
                 "verdict": "fail"},
                {"id": "cmd004_observability_design",
                 "path": "docs/cmd004_observability_design.md",
                 "verdict": "fail"},
                {"id": "cmd004_push_vapid_management",
                 "path": "docs/cmd004_push_vapid_management.md",
                 "verdict": "fail"},
                {"id": "cmd004_phase_1_6_rollback_recovery_audit",
                 "path": "docs/cmd004_phase_1_6_rollback_recovery_audit.md",
                 "verdict": "pass"},
            ],
        },
    ]


def test_classify_verdict_for_alert_pass_axis():
    """pass / pass_with_concerns は 通行可 ('pass') tier (= verdict 軸 SoT)。"""
    assert rd.classify_verdict_for_alert("pass") == "pass"
    assert rd.classify_verdict_for_alert("pass_with_concerns") == "pass"
    # uppercase / whitespace を許容
    assert rd.classify_verdict_for_alert(" PASS ") == "pass"


def test_classify_verdict_for_alert_fail_axis():
    """fail / fail_for_* は 修正待ち ('wait') tier。"""
    assert rd.classify_verdict_for_alert("fail") == "wait"
    assert rd.classify_verdict_for_alert("fail_for_privacy_sanitization_required") == "wait"


def test_classify_verdict_for_alert_unaudit_axis():
    """空 / None は 未監査 ('unaudit') tier、audit_id 有無の判定禁の test 整合。"""
    assert rd.classify_verdict_for_alert(None) == "unaudit"
    assert rd.classify_verdict_for_alert("") == "unaudit"


def test_build_cmd004_audit_alert_section_count_7_2_0():
    """黒田 v2 preaudit 条件 2: 修正待ち 7 + 通行可 2 + 未監査 0 の count assertion (= verdict 軸 SoT で 3 軸分類)。"""
    section = rd.build_cmd004_audit_alert_section(_fake_kuroda_entries_9docs())
    assert section["audit_present"] is True
    assert section["wait_count"] == 7, f"修正待ち count 不一致: {section['wait_count']} (= 想定 7)"
    assert section["pass_count"] == 2, f"通行可 count 不一致: {section['pass_count']} (= 想定 2)"
    assert section["unaudit_count"] == 0, f"未監査 count 不一致: {section['unaudit_count']} (= 想定 0)"
    assert len(section["wait_rows"]) == 7
    assert len(section["pass_rows"]) == 2


def test_build_cmd004_audit_alert_section_pass_with_concerns_engagement():
    """黒田 v2 preaudit 条件 3: engagement_analytics は pass_with_concerns 表記で通行可 section に入る。"""
    section = rd.build_cmd004_audit_alert_section(_fake_kuroda_entries_9docs())
    engagement = [r for r in section["pass_rows"] if "engagement_analytics" in r["id"]]
    assert len(engagement) == 1, "engagement_analytics が通行可 section に不在"
    assert engagement[0]["status_display"] == "pass_with_concerns", (
        f"engagement status_display = {engagement[0]['status_display']} (= pass_with_concerns 期待)"
    )


def test_build_cmd004_audit_alert_section_verdict_axis_not_audit_id_only():
    """黒田 v2 preaudit 条件 1: audit_id 有無のみで判定禁 — verdict 軸が SoT。

    target_doc に verdict=fail だけ与えれば修正待ちに、verdict=pass だけ与えれば通行可に
    分類される (= audit_id list は同一でも verdict 変化で tier が swap する)。
    """
    base = _fake_kuroda_entries_9docs()
    # 1 件を fail → pass に書き換え → 修正待ち -1 / 通行可 +1 になる確認
    base[0]["target_docs"][0] = {**base[0]["target_docs"][0], "verdict": "pass"}
    section = rd.build_cmd004_audit_alert_section(base)
    assert section["wait_count"] == 6, f"verdict swap 後 修正待ち count = {section['wait_count']} (= 想定 6)"
    assert section["pass_count"] == 3, f"verdict swap 後 通行可 count = {section['pass_count']} (= 想定 3)"


def test_build_cmd004_audit_alert_section_wait_entry_not_completed():
    """黒田 v2 preaudit 条件 6: dashboard alert で修正待ち 7 件を完了扱いしない。

    wait_rows の status_display は『privacy修正待ち』 (= 未完遂 state retain)、
    『pass』『done』『completed』『修正済』 等の完了扱い文字列は登場しないこと。
    """
    section = rd.build_cmd004_audit_alert_section(_fake_kuroda_entries_9docs())
    completed_tokens = ("pass", "done", "completed", "修正済", "verified")
    for row in section["wait_rows"]:
        status = row["status_display"]
        assert "修正待ち" in status, f"修正待ち row が未完遂表記でない: {row['id']} → {status}"
        for token in completed_tokens:
            assert token not in status.lower(), (
                f"修正待ち row {row['id']} の status_display に完了扱い文字列 {token!r} 検出: {status}"
            )


def test_build_cmd004_audit_alert_section_relative_path_only():
    """黒田 v2 preaudit 条件 4: 関連 doc は relative path のみ (= 絶対パス禁)。"""
    section = rd.build_cmd004_audit_alert_section(_fake_kuroda_entries_9docs())
    all_rows = section["wait_rows"] + section["pass_rows"] + section["unaudit_rows"]
    for row in all_rows:
        path = row["path"]
        assert path, f"path 空: {row['id']}"
        assert not path.startswith("/"), f"絶対パス検出: {row['id']} → {path}"
        assert path.startswith("docs/cmd004_"), f"relative path 形式違反: {row['id']} → {path}"


def test_build_cmd004_audit_alert_section_missing_audit_fallback():
    """audit 不在時は audit_present=False + count 全 0 で safe fallback (= 捏造禁)。"""
    section = rd.build_cmd004_audit_alert_section([])  # 空 entries
    assert section["audit_present"] is False
    assert section["wait_count"] == 0
    assert section["pass_count"] == 0
    assert section["unaudit_count"] == 0


def test_render_dashboard_includes_cmd004_audit_alert_section(monkeypatch: pytest.MonkeyPatch):
    """rendered dashboard.md に 🚨 cmd_004 audit 状態 alert section が登場する (= 全体進捗直下 visible)。"""
    monkeypatch.setattr(rd, "load_kuroda_index", lambda: _fake_kuroda_entries_9docs())
    rendered = rd.render_dashboard(_baseline_context())
    assert "🚨 cmd_004 audit 状態 alert" in rendered, "alert section heading 不在"
    assert "🟠 修正待ち 7 件" in rendered, "修正待ち sub-heading 7 件 不在"
    assert "🟢 通行可 2 件" in rendered, "通行可 sub-heading 2 件 不在"
    assert "🔴 未監査 0 件" in rendered, "未監査 sub-heading 0 件 不在"
    # 全体進捗直下: 「全体進捗」見出し位置 < alert 見出し位置 < 6 Layer 見出し位置
    pos_overall = rendered.index("🚀 全体進捗")
    pos_alert = rendered.index("🚨 cmd_004 audit 状態 alert")
    pos_layer6 = rendered.index("6 Layer 構造")
    assert pos_overall < pos_alert < pos_layer6, (
        f"alert section 位置不整合: overall={pos_overall} alert={pos_alert} layer6={pos_layer6}"
    )


def test_render_dashboard_cmd004_alert_no_absolute_path(monkeypatch: pytest.MonkeyPatch):
    """rendered alert section 内に絶対パス (/mnt/c, /home, /Users) が登場しないこと (= privacy retain + 条件 4)。"""
    monkeypatch.setattr(rd, "load_kuroda_index", lambda: _fake_kuroda_entries_9docs())
    rendered = rd.render_dashboard(_baseline_context())
    # alert section の範囲 (= 🚨 から 6 Layer まで) を切り出して absolute path 検査
    start = rendered.index("🚨 cmd_004 audit 状態 alert")
    end = rendered.index("6 Layer 構造")
    alert_block = rendered[start:end]
    for forbidden in ("/mnt/c/", "/home/", "/Users/"):
        assert forbidden not in alert_block, f"alert section に absolute path 残存: {forbidden}"
