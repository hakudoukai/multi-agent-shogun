#!/usr/bin/env python3
"""
normalize_audit_reports.py — P0-1 Canonical Report Normalizer

Reads audit report YAMLs and outputs a normalized audit_report_index.yaml
using the 3-axis model: verdict / evidence_state / completion_gate.

Rules:
  - partial verdict → verdict=fail, evidence_state=blocked_env (explicit mapping, never silent pass_with_concerns)
  - fail verdict → verdict=fail, evidence_state=missing
  - pass → verdict=pass, evidence_state=complete, completion_gate=open
  - pass_with_concerns → verdict=pass_with_concerns, evidence_state=complete, completion_gate=open
  - Any entry with existing evidence_state/completion_gate fields: preserve them
  - shogun_verified: always false (requires shogun direct verification)
"""

import sys
import os
from datetime import datetime, timezone, timedelta

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

JST = timezone(timedelta(hours=9))

VERDICT_MAPPING = {
    "pass": {
        "verdict": "pass",
        "evidence_state": "complete",
        "completion_gate": "open",
    },
    "pass_with_concerns": {
        "verdict": "pass_with_concerns",
        "evidence_state": "complete",
        "completion_gate": "open",
    },
    "partial": {
        "verdict": "fail",
        "evidence_state": "blocked_env",
        "completion_gate": "blocked",
    },
    "fail": {
        "verdict": "fail",
        "evidence_state": "missing",
        "completion_gate": "blocked",
    },
}

KNOWN_SECTIONS = [
    "reports",
    "new_project_audits",
    "phase_b_reaudits",
    "cycle2_fix_reaudits",
    "self_reflections",
]

INPUT_FILES = [
    "queue/reports/naomasa_secondpc_report.yaml",
    "queue/reports/kuroda_mainpc_report.yaml",
    "queue/reports/takenaka_mainpc_report.yaml",
    "queue/reports/acha_secondpc_report.yaml",
]

OUTPUT_FILE = "queue/reports/audit_report_index.yaml"


def get_target_id(entry):
    for key in ("target_id", "target_audit_id", "target_doc"):
        if key in entry:
            return entry[key]
    return None


def normalize_entry(entry, source_file, source_section):
    audit_id = entry.get("audit_id", "unknown")
    original_verdict = entry.get("verdict", "unknown")
    target_id = get_target_id(entry)

    mapping = VERDICT_MAPPING.get(original_verdict, {
        "verdict": "fail",
        "evidence_state": "missing",
        "completion_gate": "blocked",
    })

    verdict = mapping["verdict"]
    evidence_state = entry.get("evidence_state", mapping["evidence_state"])
    completion_gate = entry.get("completion_gate", mapping["completion_gate"])

    normalized = (original_verdict == "partial")

    result = {
        "audit_id": audit_id,
        "source_file": source_file,
        "source_section": source_section,
        "target_id": target_id,
        "verdict": verdict,
        "evidence_state": evidence_state,
        "completion_gate": completion_gate,
        "shogun_verified": False,
    }

    if normalized:
        result["original_verdict"] = original_verdict
        result["normalized"] = True

    return result


def process_file(file_path):
    if not os.path.exists(file_path):
        print(f"  SKIP: {file_path} — file not found (MC 連携予定)", file=sys.stderr)
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"  WARN: {file_path} — YAML parse error: {e}", file=sys.stderr)
        return []

    if not data:
        print(f"  WARN: {file_path} — empty or non-parseable YAML", file=sys.stderr)
        return []

    entries = []

    for section_key in KNOWN_SECTIONS:
        if section_key not in data:
            continue
        section_data = data[section_key]
        if not isinstance(section_data, list):
            continue
        for entry in section_data:
            if not isinstance(entry, dict):
                continue
            normalized = normalize_entry(entry, file_path, section_key)
            entries.append(normalized)

    # legacy named blocks: any top-level list key not in KNOWN_SECTIONS
    for key, value in data.items():
        if key in KNOWN_SECTIONS:
            continue
        if not isinstance(value, list):
            continue
        if not value:
            continue
        if not isinstance(value[0], dict):
            continue
        if "audit_id" not in value[0]:
            continue
        for entry in value:
            if not isinstance(entry, dict):
                continue
            normalized = normalize_entry(entry, file_path, key)
            entries.append(normalized)

    return entries


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    print(f"Working directory: {os.getcwd()}")

    all_entries = []
    processed_files = []
    skipped_files = []

    for file_path in INPUT_FILES:
        print(f"Processing: {file_path}")
        entries = process_file(file_path)
        if entries:
            all_entries.extend(entries)
            processed_files.append(file_path)
            print(f"  -> {len(entries)} entries extracted")
        else:
            skipped_files.append(file_path)

    partial_count = sum(1 for e in all_entries if e.get("normalized"))
    fail_count = sum(1 for e in all_entries if e["verdict"] == "fail")
    pass_count = sum(1 for e in all_entries if e["verdict"] == "pass")
    pwc_count = sum(1 for e in all_entries if e["verdict"] == "pass_with_concerns")

    now_jst = datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00")

    output = {
        "generated_at": now_jst,
        "generator": "scripts/normalize_audit_reports.py",
        "schema_version": "P0-1",
        "source_files": processed_files,
        "skipped_files": skipped_files,
        "summary": {
            "total": len(all_entries),
            "pass": pass_count,
            "pass_with_concerns": pwc_count,
            "fail": fail_count,
            "partial_auto_mapped_to_fail": partial_count,
        },
        "reports": all_entries,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"Total entries: {len(all_entries)}")
    print(f"  pass: {pass_count}")
    print(f"  pass_with_concerns: {pwc_count}")
    print(f"  fail: {fail_count} (includes {partial_count} auto-mapped from partial)")
    print(f"\nDone. exit 0")


if __name__ == "__main__":
    main()
