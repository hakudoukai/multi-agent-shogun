#!/usr/bin/env python3
r"""
validate_report_privacy.py — cmd_013 Stream B privacy gate

YAML/JSON ファイル群を scan し、以下の機密候補を検出する:
  - AWS access key:        AKIA[A-Z0-9]{16}
  - OpenAI key:            sk-[A-Za-z0-9]{20,}
  - Anthropic key:         sk-ant-[A-Za-z0-9_\-]{20,}
  - GitHub token:          ghp_[A-Za-z0-9]{36,} / gh[pousr]_[A-Za-z0-9]{20,}
  - xAI key:               xai-[A-Za-z0-9_\-]{20,}
  - GitLab PAT:            glpat-[A-Za-z0-9_\-]{20,}
  - Bearer token:          Bearer [A-Za-z0-9_\-\.]{20,}
  - absolute Linux path:   /home/[^/\s'"]+
  - absolute WSL path:     /mnt/c/[^\s'"]+

Warn only (no fail without --strict):
  - .env fragment:         ^[A-Z_]+=...     (heuristic)
  - patient/clinic id:     5〜10 桁の独立 digit

EXEMPT_FIELDS (scan_file のみ): 既知メタデータフィールドは value スキャン対象外。

返却:
  0 = clean
  1 = violations found (= high severity 一件以上 / --strict 時は warn 含む)

cmd_014 統合: SC base の豊富な検出パターン + MC の multi-file / JSON / absolute-path gate。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

HIGH_PATTERNS = [
    ("aws_key",        re.compile(r"AKIA[A-Z0-9]{16}")),
    ("anthropic_key",  re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("openai_key",     re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github_token",   re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("xai_key",        re.compile(r"\bxai-[A-Za-z0-9_\-]{20,}\b")),
    ("gitlab_pat",     re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b")),
    ("bearer_token",   re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{20,}")),
    ("absolute_home",  re.compile(r"/home/[^/\s'\"]+")),
    ("absolute_wsl_c", re.compile(r"/mnt/c/[^\s'\"]+")),
]

WARN_PATTERNS = [
    ("env_assignment",    re.compile(r"^[A-Z][A-Z0-9_]+=.+", re.MULTILINE)),
    ("digit_id_candidate", re.compile(r"(?<![\d])\d{5,10}(?![\d])")),
]

# Fields whose values are exempt from HIGH/WARN scanning in scan_file().
# These are known metadata fields that legitimately contain IDs, hashes, etc.
EXEMPT_FIELDS = frozenset({
    "verdict", "evidence_state", "completion_gate",
    "task_id", "audit_id", "timestamp",
    "commit_hash", "transfer_id", "assigned_at", "audited_at",
    "report_file", "source_hash", "target_hash",
})

# YAML simple key-value line pattern
_YAML_KV_RE = re.compile(r"^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)")


# ---------------------------------------------------------------------------
# Core scan functions
# ---------------------------------------------------------------------------

def scan_text(text: str) -> tuple[list[dict], list[dict]]:
    """Return (high_violations, warnings) — each item dict with name + sample.

    Field-unaware: scans the full text string. Used by scan_file() for
    non-YAML lines and directly by callers that have extracted value text.
    """
    high: list[dict] = []
    warn: list[dict] = []
    for name, pat in HIGH_PATTERNS:
        for m in pat.finditer(text):
            sample = m.group(0)
            if len(sample) > 80:
                sample = sample[:77] + "..."
            high.append({"pattern": name, "match_sample": sample})
    for name, pat in WARN_PATTERNS:
        for m in pat.finditer(text):
            sample = m.group(0)
            if len(sample) > 80:
                sample = sample[:77] + "..."
            warn.append({"pattern": name, "match_sample": sample})
    return high, warn


def scan_file(path: Path) -> dict:
    """Scan a single file. Return result dict (MC-compatible format).

    Field-aware: EXEMPT_FIELDS lines are skipped for HIGH/WARN checks.
    Non-keyed lines and non-exempt keyed lines are fully scanned.
    """
    if not path.exists():
        return {"file": str(path), "status": "missing", "high": [], "warn": []}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"file": str(path), "status": "read_error", "error": str(exc), "high": [], "warn": []}

    high: list[dict] = []
    warn: list[dict] = []

    for line in text.splitlines():
        kv = _YAML_KV_RE.match(line)
        if kv:
            field_name = kv.group(2).lower()
            if field_name in EXEMPT_FIELDS:
                continue
            scan_target = kv.group(3)
        else:
            scan_target = line

        if not scan_target:
            continue

        h, w = scan_text(scan_target)
        high.extend(h)
        warn.extend(w)

    return {
        "file": str(path),
        "status": "clean" if not high and not warn else "violations",
        "high": high,
        "warn": warn,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="YAML/JSON files to scan")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures too")
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="output format"
    )
    args = parser.parse_args()

    results = [scan_file(Path(p)) for p in args.files]

    any_high = any(r["high"] for r in results)
    any_warn = any(r["warn"] for r in results)

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if r["status"] == "missing":
                print(f"MISSING: {r['file']}")
                continue
            if r["status"] == "read_error":
                print(f"READ_ERROR: {r['file']}: {r.get('error')}")
                continue
            if not r["high"] and not r["warn"]:
                print(f"CLEAN: {r['file']}")
                continue
            print(f"VIOLATIONS: {r['file']}")
            for v in r["high"]:
                print(f"  HIGH  [{v['pattern']}] {v['match_sample']}")
            for v in r["warn"]:
                print(f"  WARN  [{v['pattern']}] {v['match_sample']}")

    if any_high:
        return 1
    if args.strict and any_warn:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
