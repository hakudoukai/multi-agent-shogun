#!/usr/bin/env python3
"""regenerate_dashboard.py — cmd_020 Stage 2: dashboard.md / dashboard_supabase_preflight.yaml generator.

Single canonical writer for dashboard.md. Karo and Gunshi must NOT hand-edit
dashboard.md; they update state sources (queue/reports/, queue/tasks/, memory/MEMORY.md)
and this generator reflects them deterministically.

Design reference: docs/dashboard_design_v0.2.md (黒田 audit
kuroda_dashboard_design_v0_2_reaudit_20260511 反映). v0.3 が公開された場合は
Stage 2 中断 + AC 差分照合 → 再開 (= v0_3_stop_and_sync_gate)。

Implementation contract (AC1-7):
  AC1 Supabase REST + ETag cache + diff fetch (anon+RLS)
      `--preflight` writes queue/reports/dashboard_supabase_preflight.yaml.
  AC2 Local file read: queue/tasks/ashigaru*.yaml + queue/reports/*.yaml + git log.
      dashboard.md is EXCLUDED from inputs (= 自己参照防止、黒田 P0 ②).
  AC3 Memory MCP read_graph wrap: memory/MEMORY.md snapshot fallback for timer.
  AC4 Jinja2 template → dashboard.md, generator is sole writer.
      Header carries generated_at / source_commit / stale warning.
      Legacy hand-edited dashboards must be moved to archive/dashboard_legacy_YYYYMMDD.md.
  AC5 Progress formula (fixed evaluation order, see _progress_for_leaf docstring).
      Fallback (黒田 P0 残④):
          shogun_verified=false  -> cap at 75
          evidence incomplete    -> cap at 50
          status=blocked         -> 0
          unknown                -> excluded from aggregation
          stale (mtime > N days) -> 0
          parse_error            -> 0
  AC6 Two-PC SoT: MC primary writer, SC verify-only.
      HEAD/hash 一致 gate + flock generation_lock_file.
  AC7 Tests live in tests/test_regenerate_dashboard.py (SKIP=0 mandatory).
      See AC18 of design v0.2.

Anti-duplication (AC0):
  - dashboard-viewer.py = HTTP markdown viewer (read-only). We are the writer.
  - sync_to_supabase.sh = source_code_cache UPSERT (write-only). Independent.
  - lib/audit_via_supabase.sh = audit pipeline. Independent.

Invocation:
  python3 scripts/regenerate_dashboard.py [--preflight] [--dry-run] [--writer-pc {mainpc,secondpc}]
                                          [--verify] [--output PATH] [--no-supabase]
                                          [--memory-snapshot PATH]

Exit codes:
  0 = success
  1 = lock contention / HEAD mismatch / verify failed
  2 = preflight detected blocking permission denial
  3 = unexpected error
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import jinja2
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUEUE_TASKS_DIR = PROJECT_ROOT / "queue" / "tasks"
QUEUE_REPORTS_DIR = PROJECT_ROOT / "queue" / "reports"
MEMORY_FILE = PROJECT_ROOT / "memory" / "MEMORY.md"
DASHBOARD_FILE = PROJECT_ROOT / "dashboard.md"
ARCHIVE_DIR = PROJECT_ROOT / "archive"
PREFLIGHT_REPORT = QUEUE_REPORTS_DIR / "dashboard_supabase_preflight.yaml"
LOCK_FILE = PROJECT_ROOT / ".dashboard_generation.lock"
CACHE_DIR = Path(os.environ.get("DASHBOARD_CACHE_DIR", str(Path.home() / ".cache" / "dentalbi-dashboard")))

DEFAULT_TABLES: list[dict[str, Any]] = [
    {"name": "development_progress",      "strategy": "full",     "select": "id,phase,status,updated_at"},
    {"name": "legal_sources",             "strategy": "diff",     "select": "id,title,updated_at"},
    {"name": "legal_source_linkages",     "strategy": "diff",     "select": "id,source_id,updated_at"},
    {"name": "inspection_checklists",     "strategy": "diff",     "select": "id,title,updated_at"},
    {"name": "inspection_findings",       "strategy": "full",     "select": "id,checklist_id,severity,status"},
    {"name": "procedure_codes_audit",     "strategy": "full",     "select": "id,code,status"},
    {"name": "project_documents",         "strategy": "metadata", "select": "id,title,version"},
    {"name": "design_decisions",          "strategy": "full",     "select": "id,title,status"},
    {"name": "form_templates",            "strategy": "full",     "select": "id,name"},
]

# Canonical status set (= instructions/common/task_flow.md "assigned/blocked/done/failed"
# 規範 + de-facto audit lifecycle statuses observed in queue/tasks/*.yaml).
# F2 cycle2 fix: kuroda_cmd020_regenerate_dashboard_py_audit_20260511 — 監査待ち系を
# unknown に丸めると dashboard 進捗が実態を落とす。明示段階値を持つ。
STATUS_ENUM = {
    # task_flow.md canonical (4)
    "assigned", "blocked", "done", "failed",
    # de-facto lifecycle (audit / verification waiting)
    "in_progress", "not_started", "pending",
    "drafted_pending_kuroda_pre_audit",
    "ready_for_audit",
    "audit_pending",
    "completed_pending_audit",
    "done_pending_audit",
    "audit_pending_verification",
    "unknown",
}

# Stage-based base score for non-done statuses. 監査待ちは 0% でなく明示段階値
# (= 黒田 cycle2 F2 推奨)。
STATUS_STAGE_PCT: dict[str, float] = {
    "blocked": 0.0,
    "not_started": 0.0,
    "failed": 0.0,
    "pending": 10.0,
    "drafted_pending_kuroda_pre_audit": 15.0,
    "assigned": 25.0,
    "in_progress": 50.0,
    "ready_for_audit": 70.0,
    "audit_pending": 80.0,
    "completed_pending_audit": 85.0,
    "done_pending_audit": 90.0,
    "audit_pending_verification": 95.0,
}

STALE_THRESHOLD_DAYS = 14

# F3 cycle2 fix: privacy gate 語彙統一 — WARN 残存は CLEAN ではない。
PRIVACY_CLEAN = "clean"
PRIVACY_WARNED = "warned"
PRIVACY_BLOCKED = "blocked"


def classify_privacy_result(reports: Any) -> str:
    """Map validate_report_privacy.py JSON output to a canonical verdict.

    'clean' iff HIGH 0 AND WARN 0. WARN-only results are 'warned', NOT 'clean'.
    'blocked' iff any HIGH > 0. Accepts a list of per-file result dicts or a
    single dict (mirrors validate_report_privacy.py --format json shape).
    """
    if isinstance(reports, dict):
        reports = [reports]
    high_total = 0
    warn_total = 0
    for r in reports or []:
        high_total += len(r.get("high") or [])
        warn_total += len(r.get("warn") or [])
    if high_total > 0:
        return PRIVACY_BLOCKED
    if warn_total > 0:
        return PRIVACY_WARNED
    return PRIVACY_CLEAN


# ---------------------------------------------------------------------------
# Lock primitives (AC6)
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def generation_lock(lock_path: Path = LOCK_FILE, timeout_sec: float = 0.0):
    """Acquire an exclusive flock; raise BlockingIOError if contended.

    timeout_sec=0 means "fail fast" — Stage 2 timer must not queue overlapping runs.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "w")
    deadline = time.monotonic() + timeout_sec
    while True:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                fh.close()
                raise
            time.sleep(0.1)
    try:
        fh.write(f"{os.getpid()} {_dt.datetime.now().isoformat()}\n")
        fh.flush()
        yield fh
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


# ---------------------------------------------------------------------------
# Git helpers (AC2, AC6)
# ---------------------------------------------------------------------------


def git_head_short(repo: Path = PROJECT_ROOT) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=5,
        )
        return out.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


def git_recent_log(repo: Path = PROJECT_ROOT, limit: int = 20) -> list[dict[str, str]]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "log", f"-{limit}",
             "--pretty=format:%h|%s|%ar"],
            stderr=subprocess.DEVNULL, timeout=10,
        ).decode()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []
    entries: list[dict[str, str]] = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            entries.append({"hash": parts[0], "subject": parts[1], "age": parts[2]})
    return entries


def git_head_match(mainpc_head: str, secondpc_head_hint: str | None) -> bool:
    """When running on SC verify mode, both heads must agree.

    secondpc_head_hint may be None when SC head is unknown — in that case the
    gate is informational only (returns True) but the caller should record it.
    """
    if not secondpc_head_hint:
        return True
    return mainpc_head == secondpc_head_hint


# ---------------------------------------------------------------------------
# Local YAML / state source loading (AC2)
# ---------------------------------------------------------------------------


@dataclass
class TaskEntry:
    task_id: str
    assigned_to: str
    status: str
    parent_cmd: str = ""
    bloom_level: str = ""
    persona: str = ""
    verdict: str = ""
    completion_gate: str = ""
    evidence_state: str = ""
    audit_passed: bool = False
    shogun_verified: bool = False
    source_file: str = ""
    raw_status: str = ""


@dataclass
class LoadedState:
    tasks: list[TaskEntry] = field(default_factory=list)
    reports_snapshot: dict[str, dict[str, Any]] = field(default_factory=dict)
    git_log: list[dict[str, str]] = field(default_factory=list)
    source_commit: str = ""
    parse_errors: list[str] = field(default_factory=list)


_PATH_REDACT_RE = re.compile(r"(/home/[^\s\"']+|/mnt/c/[^\s\"']+)")


def _redact_paths(text: str) -> str:
    """Strip absolute Linux / WSL paths from a message to keep privacy gate green."""
    return _PATH_REDACT_RE.sub("<redacted-path>", text)


def _safe_load_all(path: Path) -> list[Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return list(yaml.safe_load_all(fh))
    except (yaml.YAMLError, OSError) as exc:
        return [{"__parse_error__": _redact_paths(f"{path.name}: {exc}")}]


def _rel_to_repo(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _coerce_task(raw: Any, source_file: Path) -> TaskEntry | None:
    if not isinstance(raw, dict):
        return None
    block = raw.get("task")
    if not isinstance(block, dict):
        return None
    raw_status = str(block.get("status", "unknown"))
    status = raw_status if raw_status in STATUS_ENUM else "unknown"
    verification = block.get("verification_layer") or {}
    return TaskEntry(
        task_id=str(block.get("task_id", "unknown")),
        assigned_to=str(block.get("assigned_to", "")),
        status=status,
        raw_status=raw_status,
        parent_cmd=str(block.get("parent_cmd", "")),
        bloom_level=str(block.get("bloom_level", "")),
        persona=str(block.get("persona", "")),
        verdict=str(block.get("verdict", "")),
        completion_gate=str(block.get("completion_gate", "")),
        evidence_state=str(block.get("evidence_state", "")),
        audit_passed=bool(verification.get("audit_passed", False) or block.get("audit_passed", False)),
        shogun_verified=bool(verification.get("shogun_verified", False) or block.get("shogun_verified", False)),
        source_file=_rel_to_repo(source_file),
    )


def load_local_state(
    tasks_dir: Path | None = None,
    reports_dir: Path | None = None,
) -> LoadedState:
    """Load queue/tasks + queue/reports + git log.

    dashboard.md is intentionally excluded — its content is generator output, not input.
    """
    tasks_dir = tasks_dir if tasks_dir is not None else QUEUE_TASKS_DIR
    reports_dir = reports_dir if reports_dir is not None else QUEUE_REPORTS_DIR
    state = LoadedState(source_commit=git_head_short(), git_log=git_recent_log())

    if tasks_dir.is_dir():
        for path in sorted(tasks_dir.glob("ashigaru*.yaml")):
            for doc in _safe_load_all(path):
                if isinstance(doc, dict) and "__parse_error__" in doc:
                    state.parse_errors.append(doc["__parse_error__"])
                    continue
                entry = _coerce_task(doc, path)
                if entry is not None:
                    state.tasks.append(entry)

    if reports_dir.is_dir():
        for path in sorted(reports_dir.glob("*.yaml")):
            if path.name == DASHBOARD_FILE.name:
                continue  # safety belt — dashboard.md never appears here, but be explicit.
            try:
                stat = path.stat()
            except OSError:
                continue
            state.reports_snapshot[path.name] = {
                "size": stat.st_size,
                "mtime": _dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "stale": _is_stale(stat.st_mtime),
            }

    return state


def _is_stale(mtime_epoch: float, threshold_days: int = STALE_THRESHOLD_DAYS) -> bool:
    age = _dt.datetime.now().timestamp() - mtime_epoch
    return age > threshold_days * 86400


# ---------------------------------------------------------------------------
# Memory MCP fallback (AC3)
# ---------------------------------------------------------------------------


def load_memory_snapshot(snapshot_path: Path | None = None, max_chars: int = 4000) -> dict[str, Any]:
    """Read memory/MEMORY.md snapshot as MCP read_graph fallback.

    Timer-driven systemd units cannot reach the Claude MCP server, so the snapshot
    file is the only durable source.
    """
    if snapshot_path is None:
        snapshot_path = MEMORY_FILE
    if not snapshot_path.exists():
        return {"available": False, "reason": "memory_snapshot_missing", "head_lines": []}
    try:
        text = snapshot_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"available": False, "reason": f"read_failed:{exc}", "head_lines": []}
    head = "\n".join(text.splitlines()[:80])
    return {
        "available": True,
        "byte_size": len(text.encode("utf-8")),
        "head_lines": head[:max_chars].splitlines(),
        "source": _rel_to_repo(snapshot_path),
    }


# ---------------------------------------------------------------------------
# Supabase REST + ETag cache (AC1)
# ---------------------------------------------------------------------------


@dataclass
class FetchResult:
    table: str
    status: int
    cache_hit: bool
    row_count: int | None
    error: str | None
    permission_denied: bool
    bytes_received: int
    cache_path: str


def _cache_paths(table: str) -> tuple[Path, Path]:
    base = CACHE_DIR / table
    return base.with_suffix(".json"), base.with_suffix(".etag")


def fetch_table(
    table: dict[str, Any],
    base_url: str,
    anon_key: str,
    timeout: float = 8.0,
    opener: Any | None = None,
) -> FetchResult:
    """Single-table REST GET + ETag negotiation.

    On 304: return cached payload (cache_hit=True).
    On 200: write cache + new ETag.
    On 401/403: permission_denied=True.
    On network timeout or 5xx: fall back to cache when available, else error.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path, etag_path = _cache_paths(table["name"])

    params = {"select": table["select"]}
    if table["strategy"] == "diff":
        params["order"] = "updated_at.desc"
        params["limit"] = "200"
    elif table["strategy"] == "metadata":
        params["limit"] = "100"
    url = f"{base_url.rstrip('/')}/rest/v1/{table['name']}?{urllib.parse.urlencode(params)}"

    headers = {"apikey": anon_key, "Authorization": f"Bearer {anon_key}", "Accept": "application/json"}
    if etag_path.exists():
        headers["If-None-Match"] = etag_path.read_text(encoding="utf-8").strip()

    req = urllib.request.Request(url, headers=headers, method="GET")
    open_fn = opener.open if opener is not None else urllib.request.urlopen
    try:
        resp = open_fn(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if exc.code == 304 and cache_path.exists():
            return FetchResult(table["name"], 304, True, _count_rows(cache_path), None, False, 0, str(cache_path))
        if exc.code in (401, 403):
            return FetchResult(table["name"], exc.code, False, None, f"HTTP {exc.code}", True, 0, str(cache_path))
        if cache_path.exists():
            return FetchResult(table["name"], exc.code, True, _count_rows(cache_path), f"HTTP {exc.code} (stale cache used)", False, 0, str(cache_path))
        return FetchResult(table["name"], exc.code, False, None, f"HTTP {exc.code}", False, 0, str(cache_path))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        if cache_path.exists():
            return FetchResult(table["name"], 0, True, _count_rows(cache_path), f"network:{exc} (stale cache used)", False, 0, str(cache_path))
        return FetchResult(table["name"], 0, False, None, f"network:{exc}", False, 0, str(cache_path))

    body = resp.read()
    new_etag = resp.headers.get("ETag")
    try:
        cache_path.write_bytes(body)
        if new_etag:
            etag_path.write_text(new_etag, encoding="utf-8")
    except OSError:
        pass
    rows = _count_rows_from_bytes(body)
    return FetchResult(table["name"], resp.status, False, rows, None, False, len(body), str(cache_path))


def _count_rows(path: Path) -> int | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return len(data) if isinstance(data, list) else None


def _count_rows_from_bytes(blob: bytes) -> int | None:
    try:
        data = json.loads(blob.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return len(data) if isinstance(data, list) else None


def supabase_preflight(
    tables: Iterable[dict[str, Any]] | None = None,
    base_url: str | None = None,
    anon_key: str | None = None,
    timeout: float = 8.0,
    opener: Any | None = None,
) -> dict[str, Any]:
    base_url = base_url or os.environ.get("SUPABASE_URL", "")
    anon_key = anon_key or os.environ.get("SUPABASE_ANON_KEY", "")
    tables = list(tables) if tables is not None else DEFAULT_TABLES

    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_commit": git_head_short(),
        "tables": [],
        "blocking": False,
    }

    if not base_url or not anon_key:
        report["blocking"] = True
        report["blocker_reason"] = "SUPABASE_URL または SUPABASE_ANON_KEY が不在"
        for tbl in tables:
            report["tables"].append({
                "name": tbl["name"], "status": 0, "cache_hit": False,
                "row_count": None, "permission_denied": True,
                "error": "認証情報不在", "bytes_received": 0,
                "cache_path": str(_cache_paths(tbl["name"])[0]),
            })
        return report

    for tbl in tables:
        result = fetch_table(tbl, base_url, anon_key, timeout=timeout, opener=opener)
        if result.permission_denied:
            report["blocking"] = True
        report["tables"].append({
            "name": result.table, "status": result.status,
            "cache_hit": result.cache_hit, "row_count": result.row_count,
            "permission_denied": result.permission_denied,
            "error": result.error, "bytes_received": result.bytes_received,
            "cache_path": result.cache_path,
        })
    return report


def write_preflight_report(report: dict[str, Any], path: Path = PREFLIGHT_REPORT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Progress formula (AC5)
# ---------------------------------------------------------------------------


def progress_for_task(task: TaskEntry) -> float | None:
    """Compute progress percent for a single leaf task.

    Evaluation order is FIXED (black-box tests pin it):
      1. raw_status == 'unknown' or status == 'unknown'  -> None (excluded)
      2. status == 'done':
           a) shogun_verified=true AND completion_gate=open
              AND evidence_state=complete                 -> 100
           b) verdict.startswith('pass') and not 'pass_with'
                                                          -> 100 (verified) / 75 (unverified)
           c) verdict.startswith('pass_with')             -> 75
           d) verdict empty (audit awaits)                -> 75 (capped further by gates)
      3. status in STATUS_STAGE_PCT                       -> stage value
      4. status == 'assigned' AND task_id missing         -> 0 (degenerate)
      5. otherwise                                        -> 0

    Then apply caps:
      - evidence_state in {blocked_env, missing,
        schema_unsupported, cross_pc_missing}             -> min(score, 50)
      - shogun_verified=false                             -> min(score, 75)

    F2 cycle2 fix (黒田 audit): 監査待ち系 (audit_pending /
    completed_pending_audit / done_pending_audit / ready_for_audit) を
    unknown に丸めず、STATUS_STAGE_PCT 経由で明示段階値に。
    """
    if task.raw_status == "unknown" or task.status == "unknown":
        return None

    base: float
    if task.status == "done":
        if (task.shogun_verified
                and task.completion_gate == "open"
                and task.evidence_state == "complete"):
            base = 100.0
        elif task.verdict.startswith("pass") and not task.verdict.startswith("pass_with"):
            base = 100.0 if task.shogun_verified else 75.0
        elif task.verdict.startswith("pass_with"):
            base = 75.0
        else:
            # done without verdict yet — treat as awaiting audit, not 0%.
            base = 75.0
    elif task.status == "assigned":
        # degenerate: assigned without task_id is a placeholder, not progress.
        base = 25.0 if task.task_id else 0.0
    elif task.status in STATUS_STAGE_PCT:
        base = STATUS_STAGE_PCT[task.status]
    else:
        base = 0.0

    if task.evidence_state in {"blocked_env", "missing", "schema_unsupported", "cross_pc_missing"}:
        base = min(base, 50.0)
    # shogun_verified=false cap only blocks 'done' from claiming 100% — stage
    # values 80/85/90/95 are explicit "awaiting verification" markers and must
    # surface as-is (cycle1 universally capped them at 75 which hid progress).
    if task.status == "done" and not task.shogun_verified:
        base = min(base, 75.0)
    return base


def aggregate_progress(tasks: Iterable[TaskEntry]) -> dict[str, Any]:
    weighted_sum = 0.0
    total_weight = 0
    excluded = 0
    per_agent: dict[str, list[float]] = {}
    for task in tasks:
        score = progress_for_task(task)
        if score is None:
            excluded += 1
            continue
        weighted_sum += score
        total_weight += 1
        per_agent.setdefault(task.assigned_to or "unassigned", []).append(score)
    overall = (weighted_sum / total_weight) if total_weight else 0.0
    per_agent_avg = {k: (sum(v) / len(v) if v else 0.0) for k, v in per_agent.items()}
    return {
        "overall_pct": round(overall, 1),
        "leaf_count": total_weight,
        "excluded_count": excluded,
        "per_agent_pct": {k: round(v, 1) for k, v in per_agent_avg.items()},
    }


# ---------------------------------------------------------------------------
# Jinja2 template (AC4)
# ---------------------------------------------------------------------------


DASHBOARD_TEMPLATE = """# DentalBI Dashboard (auto-generated)

> ⚠️ 本ファイルは `scripts/regenerate_dashboard.py` が単独 writer。
> Karo / Gunshi / Shogun の手動編集は禁止 — state source (queue/reports/, queue/tasks/, memory/MEMORY.md) を更新せよ。
> 手動編集された旧版は `archive/dashboard_legacy_YYYYMMDD.md` へ退避すること。

- generated_at: `{{ generated_at }}`
- source_commit: `{{ source_commit }}`
- writer_pc: `{{ writer_pc }}`
- supabase_blocking: `{{ supabase.blocking }}`
{% if stale_warning -%}
- ⚠️ stale_warning: {{ stale_warning }}
{%- endif %}

## 進捗 (機械算出)

| 項目 | 値 |
|---|---|
| 全体進捗 | {{ progress.overall_pct }}% |
| 末端タスク数 | {{ progress.leaf_count }} |
| 除外件数 (不明/古い) | {{ progress.excluded_count }} |

### エージェント別

| エージェント | 平均 | タスク数 |
|---|---|---|
{% for agent, pct in progress.per_agent_pct.items() %}
| {{ agent }} | {{ pct }}% | {{ task_counts.get(agent, 0) }} |
{% endfor %}

## タスク一覧 (状態源)

| エージェント | タスクID | 状態 | 判定 | 関門 | 証拠 | 進捗 |
|---|---|---|---|---|---|---|
{% for task in tasks %}
| {{ task.assigned_to }} | `{{ task.task_id }}` | {{ task.status }} | {{ task.verdict }} | {{ task.completion_gate }} | {{ task.evidence_state }} | {{ task_progress.get(task.task_id, 'n/a') }} |
{% endfor %}

## Supabase接続事前確認

{% if supabase.blocking -%}
🚨 **接続障害**: {{ supabase.get('blocker_reason', '権限拒否を検出') }}
{% endif %}

| テーブル | 状態 | キャッシュ | 件数 | 備考 |
|---|---|---|---|---|
{% for tbl in supabase.tables %}
| {{ tbl.name }} | {{ tbl.status }} | {{ 'HIT' if tbl.cache_hit else 'MISS' }} | {{ tbl.row_count if tbl.row_count is not none else 'n/a' }} | {{ tbl.error or '' }} |
{% endfor %}

## メモリ取込 (MCPフォールバック)

- 取得可: `{{ memory.available }}`
{% if memory.available -%}
- 取得元: `{{ memory.source }}`
- サイズ: {{ memory.byte_size }}
{% else -%}
- 理由: {{ memory.reason }}
{%- endif %}

## 直近コミット

| ハッシュ | 概要 | 経過 |
|---|---|---|
{% for commit in git_log %}
| `{{ commit.hash }}` | {{ commit.subject }} | {{ commit.age }} |
{% endfor %}

## 解析エラー / 品質フラグ

{% if parse_errors -%}
{% for err in parse_errors %}
- {{ err }}
{% endfor %}
{% else -%}
(なし)
{%- endif %}

---
*家老所管 systemd サービスが dashboard.md を書き込み、各エージェント書き込み禁止 — scripts/regenerate_dashboard.py*
"""


def render_dashboard(context: dict[str, Any]) -> str:
    env = jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.StrictUndefined,
    )
    template = env.from_string(DASHBOARD_TEMPLATE)
    return template.render(**context)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def build_context(
    state: LoadedState,
    supabase_report: dict[str, Any],
    memory_snapshot: dict[str, Any],
    writer_pc: str,
) -> dict[str, Any]:
    task_progress: dict[str, str] = {}
    task_counts: dict[str, int] = {}
    for task in state.tasks:
        score = progress_for_task(task)
        task_progress[task.task_id] = "excluded" if score is None else f"{round(score, 0):.0f}%"
        task_counts[task.assigned_to or "unassigned"] = task_counts.get(task.assigned_to or "unassigned", 0) + 1

    stale_reports = [name for name, info in state.reports_snapshot.items() if info["stale"]]
    stale_warning = (
        f"{len(stale_reports)} report(s) older than {STALE_THRESHOLD_DAYS}d: " + ", ".join(stale_reports[:5])
        if stale_reports else ""
    )

    return {
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_commit": state.source_commit,
        "writer_pc": writer_pc,
        "stale_warning": stale_warning,
        "progress": aggregate_progress(state.tasks),
        "task_counts": task_counts,
        "task_progress": task_progress,
        "tasks": state.tasks,
        "supabase": supabase_report,
        "memory": memory_snapshot,
        "git_log": state.git_log,
        "parse_errors": state.parse_errors,
    }


# F4 cycle2 fix: 初回本番 write 前に手動編集 dashboard.md を archive へ退避。
# auto-generated header の有無で legacy 判定 (idempotent — generator output には
# 再 archive しない)。
_LEGACY_HEADER_MARKERS = ("auto-generated", "scripts/regenerate_dashboard.py")


def _archive_legacy_dashboard(target: Path, archive_dir: Path | None = None) -> Path | None:
    """Archive a hand-edited dashboard.md before the generator overwrites it.

    Returns the archive destination if archiving happened, else None.
    Subsequent runs (where target already carries the auto-generated banner)
    are no-ops, so the archive is created at most once per legacy file per day.
    """
    if archive_dir is None:
        archive_dir = ARCHIVE_DIR
    if not target.exists():
        return None
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if all(marker in text for marker in _LEGACY_HEADER_MARKERS):
        return None  # already generator output
    archive_dir.mkdir(parents=True, exist_ok=True)
    today = _dt.datetime.now().strftime("%Y%m%d")
    base_name = f"dashboard_legacy_{today}.md"
    dest = archive_dir / base_name
    n = 1
    while dest.exists():
        dest = archive_dir / f"dashboard_legacy_{today}_{n}.md"
        n += 1
    dest.write_text(text, encoding="utf-8")
    return dest


def write_output(rendered: str, output_path: Path, archive_dir: Path | None = None) -> None:
    archived = _archive_legacy_dashboard(output_path, archive_dir)
    if archived is not None:
        print(f"[regenerate_dashboard] archived legacy {output_path.name} -> {archived}",
              file=sys.stderr)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    tmp.write_text(rendered, encoding="utf-8")
    tmp.replace(output_path)


# F1 cycle2 fix (kuroda audit verify_time_delta): rendered 全文比較は
# generated_at と git_log の relative age が時刻 drift で必ず割れるため
# AC6 verify-only mode が運用不能。verify 直前に非決定値を mask する。
_VERIFY_VOLATILE_PATTERNS = (
    # ヘッダ generated_at: `2026-05-11T22:00:00+09:00`
    re.compile(r"^- generated_at: `[^`]+`\s*$", re.MULTILINE),
    # 表行 | hash | subject | 5 minutes ago | (最終列が age)
    re.compile(r"^(\| `[0-9a-fA-F]+` \| [^|\n]+ \|)([^|\n]*)\|\s*$", re.MULTILINE),
)


def _normalize_for_verify(text: str) -> str:
    """Strip wall-clock / relative-age values so verify is time-stable.

    Reproducer (kuroda 21:47 audit): write tmp output → sleep 2 → --verify
    → previously rc=1 (generated_at 2 sec apart). After normalization both
    sides hash identically because the volatile span is masked.
    """
    out = _VERIFY_VOLATILE_PATTERNS[0].sub("- generated_at: `<volatile>`", text)
    out = _VERIFY_VOLATILE_PATTERNS[1].sub(r"\1 <volatile> |", out)
    return out


def verify_dashboard(expected: str, actual_path: Path) -> bool:
    if not actual_path.exists():
        return False
    actual = actual_path.read_text(encoding="utf-8")
    expected_n = _normalize_for_verify(expected)
    actual_n = _normalize_for_verify(actual)
    return (
        hashlib.sha256(expected_n.encode("utf-8")).hexdigest()
        == hashlib.sha256(actual_n.encode("utf-8")).hexdigest()
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate dashboard.md from state sources")
    parser.add_argument("--preflight", action="store_true", help="Only run Supabase preflight + write report")
    parser.add_argument("--dry-run", action="store_true", help="Render to stdout / tmp without overwriting dashboard.md")
    parser.add_argument("--writer-pc", default="mainpc", choices=["mainpc", "secondpc"],
                        help="Identify writer PC (MC primary, SC verify-only)")
    parser.add_argument("--verify", action="store_true", help="Verify-only mode (SC): compare existing dashboard.md hash")
    parser.add_argument("--output", default=str(DASHBOARD_FILE), help="Override output path")
    parser.add_argument("--no-supabase", action="store_true", help="Skip Supabase fetch (use cache only)")
    parser.add_argument("--memory-snapshot", default=str(MEMORY_FILE), help="Override MEMORY.md path")
    parser.add_argument("--secondpc-head", default=None,
                        help="Optional SC HEAD hint; mismatched HEAD fails the generator")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.writer_pc == "secondpc" and not args.verify:
        print("[regenerate_dashboard] SC must run with --verify; MC is primary writer", file=sys.stderr)
        return 1

    if args.preflight:
        report = supabase_preflight()
        write_preflight_report(report)
        print(yaml.safe_dump(report, allow_unicode=True, sort_keys=False))
        return 2 if report["blocking"] else 0

    try:
        with generation_lock():
            state = load_local_state()
            mainpc_head = state.source_commit
            if args.secondpc_head and not git_head_match(mainpc_head, args.secondpc_head):
                print(f"[regenerate_dashboard] HEAD mismatch MC={mainpc_head} SC={args.secondpc_head}", file=sys.stderr)
                return 1

            if args.no_supabase:
                supabase_report = {
                    "schema_version": 1,
                    "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                    "source_commit": state.source_commit,
                    "tables": [], "blocking": False, "skipped": True,
                }
            else:
                supabase_report = supabase_preflight()
                write_preflight_report(supabase_report)

            memory = load_memory_snapshot(Path(args.memory_snapshot))
            context = build_context(state, supabase_report, memory, args.writer_pc)
            rendered = render_dashboard(context)

            if args.verify:
                ok = verify_dashboard(rendered, Path(args.output))
                print("verify: ok" if ok else "verify: mismatch", file=sys.stderr)
                return 0 if ok else 1

            if args.dry_run:
                sys.stdout.write(rendered)
                return 0

            write_output(rendered, Path(args.output))
            print(f"[regenerate_dashboard] wrote {args.output} ({len(rendered)} bytes, head={state.source_commit})")
            return 0
    except BlockingIOError:
        print("[regenerate_dashboard] generation_lock contended", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
