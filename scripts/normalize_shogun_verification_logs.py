#!/usr/bin/env python3
"""
normalize_shogun_verification_logs.py — cmd_013 Stream B canonical index 生成

入力:
  queue/reports/shogun_verification_mainpc_log.yaml   (MC writer)
  queue/reports/shogun_verification_secondpc_log.yaml (SC writer)

出力:
  queue/reports/shogun_verification_canonical_index.yaml

各 entry フィールド:
  event_id       — sha1(source_pc + auditor_who + target + verified_at)[:12]
  source_pc      — mainpc | secondpc
  target_id      — 審査対象 audit_id / target
  shogun_verified — bool
  checks_passed   — "N/M" string
  verified_at     — ISO 8601
  payload_hash    — sha256(canonical_payload)[:16]
  redaction_note  — 適用 pattern 一覧 (redact 跡)

規律:
  - 重複 event_id は warn + skip (= writer single-PC ownership 違反検知)
  - 片方 PC log 欠如は warn + partial output (exit 0、--strict 時 exit 1)
  - 全 string 値に redact pattern (= AWS key / OpenAI key / absolute /home or /mnt/c path) 適用
"""

import argparse
import hashlib
import re
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORT_DIR = PROJECT_ROOT / "queue" / "reports"

DEFAULT_INPUTS = [
    ("mainpc", REPORT_DIR / "shogun_verification_mainpc_log.yaml"),
    ("secondpc", REPORT_DIR / "shogun_verification_secondpc_log.yaml"),
]
OUTPUT_FILE = REPORT_DIR / "shogun_verification_canonical_index.yaml"

REDACT_PATTERNS = [
    ("aws_key", re.compile(r"AKIA[A-Z0-9]{16}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("absolute_home", re.compile(r"/home/[^\s'\"]+")),
    ("absolute_wsl_c", re.compile(r"/mnt/c/[^\s'\"]+")),
]


def redact_string(s: str) -> tuple[str, list[str]]:
    """Apply redact patterns. Return (redacted_string, [matched_pattern_names])."""
    matched: list[str] = []
    out = s
    for name, pat in REDACT_PATTERNS:
        if pat.search(out):
            matched.append(name)
            out = pat.sub(f"<REDACTED:{name}>", out)
    return out, matched


def redact_value(v, matched: set):
    """Walk an arbitrary value; redact strings; collect matched pattern names."""
    if isinstance(v, str):
        red, m = redact_string(v)
        for x in m:
            matched.add(x)
        return red
    if isinstance(v, list):
        return [redact_value(x, matched) for x in v]
    if isinstance(v, dict):
        return {k: redact_value(val, matched) for k, val in v.items()}
    return v


def stable_event_id(source_pc: str, auditor_who: str, target: str, verified_at: str) -> str:
    raw = f"{source_pc}|{auditor_who}|{target}|{verified_at}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def payload_hash(entry: dict) -> str:
    """sha256 of canonical (sorted) yaml of payload-relevant fields."""
    payload = {
        "checks": entry.get("checks"),
        "flags": entry.get("flags"),
        "audit_entry_excerpt": entry.get("audit_entry_excerpt"),
    }
    canonical = yaml.safe_dump(payload, allow_unicode=True, sort_keys=True, default_flow_style=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def normalize_entry(raw: dict, source_pc: str) -> dict | None:
    """Convert a verification log entry to canonical form. Returns None if shape invalid."""
    if not isinstance(raw, dict):
        return None

    target = raw.get("target")
    auditor_who = raw.get("auditor_who")
    verified_at = raw.get("verified_at")
    if not (isinstance(target, str) and isinstance(verified_at, str)):
        return None
    if auditor_who is None:
        auditor_who = "unknown"

    event_id = stable_event_id(source_pc, str(auditor_who), target, verified_at)
    p_hash = payload_hash(raw)

    matched: set[str] = set()
    redacted_excerpt = redact_value(raw.get("audit_entry_excerpt") or {}, matched)
    redacted_flags = redact_value(raw.get("flags") or [], matched)

    canonical = {
        "event_id": event_id,
        "source_pc": source_pc,
        "target_id": target,
        "auditor_who": auditor_who,
        "shogun_verified": bool(raw.get("shogun_verified", False)),
        "checks_passed": raw.get("checks_passed", ""),
        "verified_at": verified_at,
        "payload_hash": p_hash,
        "audit_entry_excerpt": redacted_excerpt,
        "flags": redacted_flags,
    }
    if matched:
        canonical["redaction_note"] = sorted(matched)
    return canonical


def load_log(path: Path) -> tuple[list[dict] | None, str | None]:
    """Return (entries, error_kind). entries=None on parse error."""
    if not path.exists():
        return None, "missing"
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: parse_error in {path}: {exc}", file=sys.stderr)
        return None, "parse_error"
    if not isinstance(raw, dict):
        print(f"ERROR: top-level type unexpected in {path}", file=sys.stderr)
        return None, "parse_error"
    entries = raw.get("verifications") or []
    if not isinstance(entries, list):
        print(f"ERROR: 'verifications' is not a list in {path}", file=sys.stderr)
        return None, "parse_error"
    return entries, None


def normalize(inputs: list[tuple[str, Path]]) -> tuple[list[dict], list[str], bool]:
    """
    Returns (canonical_entries, missing_pcs, parse_error_seen).
    """
    seen_event_ids: set[str] = set()
    out: list[dict] = []
    missing: list[str] = []
    parse_error_seen = False

    for source_pc, path in inputs:
        entries, err = load_log(path)
        if err == "missing":
            print(f"WARNING: {source_pc} log missing: {path} (partial output)", file=sys.stderr)
            missing.append(source_pc)
            continue
        if err == "parse_error":
            parse_error_seen = True
            continue
        for raw in entries or []:
            canonical = normalize_entry(raw, source_pc)
            if canonical is None:
                print(f"WARNING: skipped malformed entry in {source_pc} log", file=sys.stderr)
                continue
            eid = canonical["event_id"]
            if eid in seen_event_ids:
                print(
                    f"WARNING: duplicate event_id {eid} in {source_pc} log "
                    f"(target={canonical['target_id']}) — skipped",
                    file=sys.stderr,
                )
                continue
            seen_event_ids.add(eid)
            out.append(canonical)
    return out, missing, parse_error_seen


def build_index(entries: list[dict], missing: list[str], parse_error_seen: bool) -> dict:
    return {
        "schema_version": "1",
        "generator": "scripts/normalize_shogun_verification_logs.py",
        "missing_pc_logs": missing,
        "parse_error_seen": parse_error_seen,
        "total_events": len(entries),
        "events": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="stdout only, do not write file")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any input log is missing")
    parser.add_argument("--mainpc-log", help="override mainpc log path")
    parser.add_argument("--secondpc-log", help="override secondpc log path")
    parser.add_argument("--output", help="override output path")
    args = parser.parse_args()

    inputs = list(DEFAULT_INPUTS)
    if args.mainpc_log:
        inputs[0] = ("mainpc", Path(args.mainpc_log))
    if args.secondpc_log:
        inputs[1] = ("secondpc", Path(args.secondpc_log))

    entries, missing, parse_error_seen = normalize(inputs)
    index = build_index(entries, missing, parse_error_seen)
    text = yaml.safe_dump(index, allow_unicode=True, sort_keys=False, default_flow_style=False)

    if parse_error_seen:
        # parse_error is a hard failure even without --strict
        if args.dry_run:
            print(text)
        return 2

    if args.dry_run:
        print(text)
    else:
        out_path = Path(args.output) if args.output else OUTPUT_FILE
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(
            f"Written {len(entries)} canonical events to {out_path} "
            f"(missing={missing or 'none'})",
            file=sys.stderr,
        )

    if args.strict and missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
