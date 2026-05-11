#!/usr/bin/env python3
"""
normalize_audit_reports.py — Canonical audit report normalizer.

Reads MC/SC auditor report files (multi-schema) and emits a unified
queue/reports/audit_report_index.yaml with canonical schema.

Hard rules:
  - `partial` verdict is never terminal. It is always mapped to `fail`.
  - The cause determines evidence_state: blocked_env | missing | schema_unsupported | cross_pc_missing
  - completion_gate is `blocked` whenever evidence_state != complete or verdict == fail
  - `partial` in any entry triggers a stderr warning.
  - Legacy schema sections trigger a stderr warning.
"""

import argparse
import sys
import re
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORT_DIR = PROJECT_ROOT / "queue" / "reports"

DEFAULT_REPORT_FILES = [
    REPORT_DIR / "kuroda_mainpc_report.yaml",
    REPORT_DIR / "takenaka_report.yaml",
    REPORT_DIR / "naomasa_secondpc_report.yaml",
    REPORT_DIR / "acha_secondpc_report.yaml",
]

OUTPUT_FILE = REPORT_DIR / "audit_report_index.yaml"

# Environment-related keywords for partial → blocked_env detection
_ENV_KEYWORDS = re.compile(
    r"pytest.*FAIL|FAIL.*pytest|WSL|venv.*エラー|環境|environment|"
    r"テスト実行不能|tests did not start|skip_count.*unknown",
    re.IGNORECASE,
)


def _detect_partial_reason(entry: dict) -> str:
    """
    Return evidence_state for a `partial` verdict.

    Looks at `verification`, `recommendations`, `findings`, and
    `perspective_verdicts` to classify the reason.
    """
    verification = entry.get("verification", {})
    if isinstance(verification, dict):
        combined = " ".join(str(v) for v in verification.values())
        if _ENV_KEYWORDS.search(combined):
            return "blocked_env"

    recommendations = entry.get("recommendations", [])
    findings = entry.get("findings", [])
    text = " ".join(str(r) for r in recommendations) + " " + " ".join(str(f) for f in findings)
    if _ENV_KEYWORDS.search(text):
        return "blocked_env"

    # Test perspective explicitly failed
    pvs = entry.get("perspective_verdicts", {})
    for key, val in pvs.items():
        if "test" in key.lower() or "6_" in key:
            if str(val) in ("fail", "partial"):
                return "missing"

    # Missing evidence indicators
    if any(kw in text for kw in ("未取得", "missing", "不足", "証跡", "未確認", "残存")):
        return "missing"

    return "missing"


def _normalize_verdict(source_verdict: str, entry: dict) -> tuple[str, str, str, str]:
    """
    Return (verdict, evidence_state, completion_gate, normalization_reason).
    """
    v = str(source_verdict).strip().lower()

    if v == "partial":
        evidence_state = _detect_partial_reason(entry)
        reason = f"partial→fail (Hard rule): evidence_state={evidence_state}"
        print(
            f"WARNING: partial verdict detected in audit_id={entry.get('audit_id', '?')} "
            f"→ mapped to fail / {evidence_state}",
            file=sys.stderr,
        )
        return "fail", evidence_state, "blocked", reason

    if v in ("pass", "passed"):
        return "pass", "complete", "open", "pass→canonical"

    if v in ("pass_with_concerns", "concerns"):
        return "pass_with_concerns", "complete", "open", "pass_with_concerns→canonical"

    if v in ("fail", "failed"):
        return "fail", "missing", "blocked", "fail→canonical"

    if v == "blocked_verification":
        return "fail", "blocked_env", "blocked", "blocked_verification→fail/blocked_env"

    # Unknown verdict
    print(
        f"WARNING: unknown verdict '{source_verdict}' in audit_id={entry.get('audit_id', '?')} "
        f"→ mapped to fail / schema_unsupported",
        file=sys.stderr,
    )
    return "fail", "schema_unsupported", "blocked", f"unknown verdict '{source_verdict}'→fail"


def _normalize_entry(
    entry: dict,
    source_file: str,
    source_section: str,
    original_schema_type: str,
) -> dict:
    """Convert a raw report entry to canonical schema."""
    source_verdict = entry.get("verdict", "unknown")
    verdict, evidence_state, completion_gate, normalization_reason = _normalize_verdict(
        source_verdict, entry
    )

    related_files = entry.get("related_files", [])
    if not isinstance(related_files, list):
        related_files = [related_files] if related_files else []

    return {
        "audit_id": entry.get("audit_id", "unknown"),
        "source_file": source_file,
        "source_section": source_section,
        "original_schema_type": original_schema_type,
        "target_id": entry.get("target_id", entry.get("target_audit_id", "unknown")),
        "verdict": verdict,
        "source_verdict": source_verdict,
        "evidence_state": evidence_state,
        "completion_gate": completion_gate,
        "shogun_verified": False,
        "normalization_reason": normalization_reason,
        "audited_at": entry.get("audited_at", None),
        "related_files": related_files,
        "commit_hash": entry.get("commit_hash", None),
        "log_path": entry.get("log_path", None),
    }


def load_report_file(path: Path) -> list[dict]:
    """
    Load a report file and return a list of normalized canonical entries.

    Handles schema types:
      - reports (canonical list)
      - new_project_audits
      - phase_b_reaudits
      - legacy named blocks (warn)
    """
    if not path.exists():
        print(f"WARNING: report file not found, skipping: {path}", file=sys.stderr)
        return []

    try:
        source_file = str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        source_file = str(path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(
            f"WARNING: YAML parse error in {path}: {exc} — skipping file",
            file=sys.stderr,
        )
        return []

    if not isinstance(raw, dict):
        print(f"WARNING: unexpected top-level type in {path}, skipping", file=sys.stderr)
        return []

    results = []

    # Section: reports (canonical)
    if "reports" in raw and isinstance(raw["reports"], list):
        for entry in raw["reports"]:
            if isinstance(entry, dict):
                results.append(
                    _normalize_entry(entry, source_file, "reports", "reports")
                )

    # Section: new_project_audits
    if "new_project_audits" in raw and isinstance(raw["new_project_audits"], list):
        for entry in raw["new_project_audits"]:
            if isinstance(entry, dict):
                results.append(
                    _normalize_entry(entry, source_file, "new_project_audits", "new_project_audits")
                )

    # Section: phase_b_reaudits
    if "phase_b_reaudits" in raw and isinstance(raw["phase_b_reaudits"], list):
        for entry in raw["phase_b_reaudits"]:
            if isinstance(entry, dict):
                results.append(
                    _normalize_entry(entry, source_file, "phase_b_reaudits", "phase_b_reaudits")
                )

    # Legacy named blocks (any other dict-valued top-level key containing a list)
    known_sections = {"reports", "new_project_audits", "phase_b_reaudits"}
    for key, value in raw.items():
        if key in known_sections:
            continue
        if isinstance(value, list) and value and isinstance(value[0], dict) and "audit_id" in value[0]:
            print(
                f"WARNING: legacy schema section '{key}' in {source_file} — "
                "reading with legacy fallback",
                file=sys.stderr,
            )
            for entry in value:
                if isinstance(entry, dict):
                    results.append(
                        _normalize_entry(entry, source_file, key, "legacy")
                    )

    if not results:
        print(f"WARNING: no audit entries found in {path}", file=sys.stderr)

    return results


def normalize(report_files: list[Path]) -> list[dict]:
    """Process all report files and return combined canonical entries."""
    all_entries = []
    for path in report_files:
        all_entries.extend(load_report_file(path))
    return all_entries


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize multi-schema audit reports to canonical index."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print normalized output to stdout only, do not write to file.",
    )
    parser.add_argument(
        "--report",
        metavar="FILE",
        help="Process a single report file instead of all defaults.",
    )
    args = parser.parse_args()

    if args.report:
        report_files = [Path(args.report)]
    else:
        report_files = DEFAULT_REPORT_FILES

    entries = normalize(report_files)
    output = {"reports": entries}
    yaml_text = yaml.dump(output, allow_unicode=True, sort_keys=False, default_flow_style=False)

    if args.dry_run:
        print(yaml_text)
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(yaml_text, encoding="utf-8")
    print(f"Written {len(entries)} entries to {OUTPUT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
