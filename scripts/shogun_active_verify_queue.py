#!/usr/bin/env python3
"""shogun_active_verify_queue.py — cycle 1 dry-run candidate scanner.

信長殿陛下御差配 (= 2026-05-12 13:57) 「規範決めただけ動いてない、解決を」
を機械化する仕組み task の cycle 1 縮小版。

scope (= 黒田 14:19 事前監査 pass_with_conditions / open_for_assignment):
  - local YAML scan のみ (= project tree 内 file)
  - 黒田/直政 audit pass entry × 信長 verify log 未追記 candidate を log 出力
  - dry-run のみ (= --execute flag 未実装、shogun inbox 自動投函禁)
  - systemctl/Supabase MCP 一切触らず

scan:
  1. queue/inbox/{karo,gunshi,ashigaru1-7,shogun}.yaml → unread (read: false) 件数
  2. queue/reports/{kuroda_mainpc,naomasa_secondpc,honda,ieyasu,sanada,takenaka}_report.yaml
     → verdict が "pass" prefix の audit entry を抽出
  3. queue/reports/shogun_verification_mainpc_log.yaml
     → verified 済 target/audit_id を set 化
  4. (2) - (3) = candidate

output: queue/reports/active_verify_queue_candidate_log.yaml

exit codes:
  0 = success (= candidates may be empty)
  1 = lock held / unreadable input / yaml parse error

privacy:
  - 絶対 path leak 禁 (= REPO_ROOT 相対の repo-relative path のみ記録)
  - YAML key 名は EXEMPT_FIELDS に整合 (= validate_report_privacy.py が誤検知しない設計)
"""

from __future__ import annotations

import argparse
import fcntl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
INBOX_DIR = REPO_ROOT / "queue" / "inbox"
REPORTS_DIR = REPO_ROOT / "queue" / "reports"
VERIFICATION_LOG = REPORTS_DIR / "shogun_verification_mainpc_log.yaml"
CANDIDATE_LOG = REPORTS_DIR / "active_verify_queue_candidate_log.yaml"
LOCK_PATH = REPO_ROOT / "queue" / "reports" / ".active_verify_queue.lock"

INBOX_AGENTS = [
    "karo", "gunshi",
    "ashigaru1", "ashigaru2", "ashigaru3", "ashigaru4",
    "ashigaru5", "ashigaru6", "ashigaru7",
    "shogun",
]

AUDITOR_REPORTS = [
    ("kuroda", "kuroda_mainpc_report.yaml"),
    ("naomasa", "naomasa_secondpc_report.yaml"),
    ("honda", "honda_report.yaml"),
    ("ieyasu", "ieyasu_report.yaml"),
    ("sanada", "sanada_report.yaml"),
    ("takenaka", "takenaka_report.yaml"),
]

PASS_VERDICT_PREFIX = "pass"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"yaml_parse_error file={path.relative_to(REPO_ROOT)} err={exc}") from exc


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return path.name


# ---------------------------------------------------------------------------
# Scanners
# ---------------------------------------------------------------------------

def scan_unread_inbox(inbox_dir: Path, agents: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for agent in agents:
        path = inbox_dir / f"{agent}.yaml"
        data = safe_load_yaml(path)
        if not isinstance(data, dict):
            counts[agent] = 0
            continue
        msgs = data.get("messages") or []
        unread = sum(1 for m in msgs if isinstance(m, dict) and m.get("read") is False)
        counts[agent] = unread
    return counts


def scan_audit_pass_entries(reports_dir: Path, auditors: list[tuple[str, str]]) -> list[dict]:
    out: list[dict] = []
    for auditor_name, filename in auditors:
        path = reports_dir / filename
        data = safe_load_yaml(path)
        if not isinstance(data, dict):
            continue
        reports = data.get("reports") or []
        if not isinstance(reports, list):
            continue
        for entry in reports:
            if not isinstance(entry, dict):
                continue
            verdict = entry.get("verdict")
            if not isinstance(verdict, str) or not verdict.startswith(PASS_VERDICT_PREFIX):
                continue
            audit_id = entry.get("audit_id") or ""
            target_id = entry.get("target_id") or ""
            commit_hash = entry.get("commit_hash") or ""
            audited_at = entry.get("audited_at") or ""
            out.append({
                "auditor": auditor_name,
                "audit_id": str(audit_id),
                "target_id": str(target_id),
                "verdict": verdict,
                "commit_hash": str(commit_hash),
                "audited_at": str(audited_at),
                "source_file": relpath(path),
            })
    return out


def scan_verified_ids(verification_log_path: Path) -> set[str]:
    data = safe_load_yaml(verification_log_path)
    verified: set[str] = set()
    if not isinstance(data, dict):
        return verified
    entries = data.get("verifications") or []
    if not isinstance(entries, list):
        return verified
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        target = entry.get("target")
        if isinstance(target, str) and target:
            verified.add(target)
        excerpt = entry.get("audit_entry_excerpt")
        if isinstance(excerpt, dict):
            aid = excerpt.get("audit_id")
            tid = excerpt.get("target_id")
            if isinstance(aid, str) and aid:
                verified.add(aid)
            if isinstance(tid, str) and tid:
                verified.add(tid)
    return verified


def compute_candidates(pass_entries: list[dict], verified_ids: set[str]) -> list[dict]:
    candidates: list[dict] = []
    for entry in pass_entries:
        identifiers = {entry["audit_id"], entry["target_id"]}
        identifiers.discard("")
        if identifiers.isdisjoint(verified_ids):
            candidates.append(entry)
    return candidates


# ---------------------------------------------------------------------------
# Lock + write
# ---------------------------------------------------------------------------

class LockHeld(RuntimeError):
    pass


def acquire_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fp = lock_path.open("w")
    try:
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        fp.close()
        raise LockHeld(f"lock held: {relpath(lock_path)}") from exc
    return fp


def write_candidate_log(output_path: Path, payload: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
    output_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Orchestration (testable)
# ---------------------------------------------------------------------------

def run_scan(
    repo_root: Path | None = None,
    inbox_dir: Path | None = None,
    reports_dir: Path | None = None,
    verification_log: Path | None = None,
    candidate_log: Path | None = None,
    inbox_agents: list[str] | None = None,
    auditor_reports: list[tuple[str, str]] | None = None,
) -> dict:
    repo_root = repo_root or REPO_ROOT
    inbox_dir = inbox_dir or (repo_root / "queue" / "inbox")
    reports_dir = reports_dir or (repo_root / "queue" / "reports")
    verification_log = verification_log or (reports_dir / "shogun_verification_mainpc_log.yaml")
    candidate_log = candidate_log or (reports_dir / "active_verify_queue_candidate_log.yaml")
    inbox_agents = inbox_agents or INBOX_AGENTS
    auditor_reports = auditor_reports or AUDITOR_REPORTS

    unread_counts = scan_unread_inbox(inbox_dir, inbox_agents)
    pass_entries = scan_audit_pass_entries(reports_dir, auditor_reports)
    verified_ids = scan_verified_ids(verification_log)
    candidates = compute_candidates(pass_entries, verified_ids)

    payload = {
        "generated_at": now_iso(),
        "mode": "dry_run",
        "cycle": 1,
        "scope_note": "local scan only; --execute and shogun inbox auto-post are out of cycle 1 scope",
        "unread_inbox_counts": unread_counts,
        "audit_pass_total": len(pass_entries),
        "already_verified_total": len(verified_ids),
        "candidates_total": len(candidates),
        "candidates": candidates,
    }
    write_candidate_log(candidate_log, payload)
    return payload


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quiet", action="store_true",
        help="suppress stdout summary (log file still written)",
    )
    args = parser.parse_args(argv)

    try:
        lock_fp = acquire_lock(LOCK_PATH)
    except LockHeld as exc:
        print(f"SKIP: {exc}", file=sys.stderr)
        return 1

    try:
        payload = run_scan()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        try:
            fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)
        finally:
            lock_fp.close()

    if not args.quiet:
        print(
            f"[{payload['generated_at']}] "
            f"audit_pass={payload['audit_pass_total']} "
            f"verified={payload['already_verified_total']} "
            f"candidates={payload['candidates_total']} "
            f"log={relpath(CANDIDATE_LOG)}"
        )
    return 0


if __name__ == "__main__":
    # Small jitter to avoid systemd timer thundering on shared inotify
    time.sleep(0)
    sys.exit(main())
