#!/usr/bin/env python3
"""
normalize_shogun_verification_logs.py — Verification Index Normalizer

Reads shogun_verification_log YAMLs from both PCs and outputs
queue/reports/verification_index.yaml keyed by target_audit_id.

Supports mixed-root YAML structure (mapping + root-level sequence items).
"""

import sys
import os
import re
from datetime import datetime, timezone, timedelta

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

JST = timezone(timedelta(hours=9))

INPUT_FILES = {
    "secondpc": "queue/reports/shogun_verification_log_secondpc.yaml",
    "mainpc":   "queue/reports/shogun_verification_log.yaml",
}

OUTPUT_FILE = "queue/reports/verification_index.yaml"

# Pattern to detect root-level sequence items that break mapping-root YAML
ROOT_SEQ_PATTERN = re.compile(r'^- (?:entry_id|verify_id):', re.MULTILINE)


def load_yaml_lenient(file_path):
    """
    Load YAML file, falling back to split-parse for mixed mapping+sequence root.
    Returns (mapping_data, extra_list_items, error_info)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Try normal load first
    try:
        data = yaml.safe_load(content)
        if data is None:
            return {}, [], None
        if isinstance(data, dict):
            return data, [], None
        return {}, [], f"unexpected root type: {type(data).__name__}"
    except yaml.YAMLError:
        pass

    # Fallback: split at first root-level sequence item
    match = ROOT_SEQ_PATTERN.search(content)
    if match is None:
        return {}, [], "yaml_parse_error: no recognizable split point"

    mapping_part = content[: match.start()].rstrip()
    sequence_part = content[match.start():]

    mapping_data = {}
    if mapping_part:
        try:
            mapping_data = yaml.safe_load(mapping_part) or {}
        except yaml.YAMLError as e:
            return {}, [], f"yaml_parse_error (mapping): {str(e).split(chr(10))[0]}"

    extra_items = []
    if sequence_part:
        try:
            items = yaml.safe_load(sequence_part)
            if isinstance(items, list):
                extra_items = [i for i in items if isinstance(i, dict)]
        except yaml.YAMLError:
            pass

    return mapping_data, extra_items, None


def pc_suffix_from(file_path, mapping_data):
    """Determine PC suffix from metadata or filename."""
    metadata = mapping_data.get("metadata", {})
    if isinstance(metadata, dict):
        pc = metadata.get("pc", "")
        if pc in ("mainpc", "secondpc"):
            return pc
    basename = os.path.basename(file_path)
    if "secondpc" in basename:
        return "secondpc"
    return "mainpc"


def extract_from_verifications(verifications, source_file, pc):
    """Extract entries from the standard verifications list format."""
    entries = []
    for v in verifications:
        if not isinstance(v, dict):
            continue
        verify_id = v.get("verify_id", "unknown")
        target_audit_ids = v.get("target_audit_ids", [])
        if not isinstance(target_audit_ids, list):
            target_audit_ids = [target_audit_ids] if target_audit_ids else []
        for tid in target_audit_ids:
            if tid is None:
                continue
            entries.append({
                "target_audit_id": str(tid),
                "verify_id": verify_id,
                "target_task": v.get("target_task", ""),
                "pc_source": pc,
                "shogun_verified": bool(v.get("shogun_verified", False)),
                "audit_passed": bool(v.get("audit_passed", False)),
                "audited_done": bool(v.get("audited_done", False)),
                "verified_at": str(v.get("verified_at", "")),
                "source_file": source_file,
                "entry_type": "verifications",
            })
    return entries


def extract_from_top_level_entries(items, source_file, pc):
    """Extract entries from top-level entry_id/targets format (P0/P1/P2 style)."""
    entries = []
    for item in items:
        if not isinstance(item, dict):
            continue
        entry_id = item.get("entry_id") or item.get("verify_id", "unknown")
        targets = item.get("targets", [])
        if not isinstance(targets, list):
            continue
        verified_at = str(item.get("date") or item.get("verified_at", ""))
        for target in targets:
            if not isinstance(target, dict):
                continue
            tid = target.get("target_id", "")
            if not tid:
                continue
            shogun_verified = bool(target.get("shogun_verified", False))
            entries.append({
                "target_audit_id": str(tid),
                "verify_id": entry_id,
                "target_task": str(tid),
                "pc_source": pc,
                "shogun_verified": shogun_verified,
                "audit_passed": True,
                "audited_done": shogun_verified,
                "verified_at": verified_at,
                "source_file": source_file,
                "entry_type": "targets",
                "gunshi_verdict": str(target.get("gunshi_verdict", "")),
                "completion_gate": str(target.get("gunshi_completion_gate", "")),
                "commit": str(target.get("commit", "")),
            })
    return entries


def process_file(file_path, default_pc):
    if not os.path.exists(file_path):
        print(f"  SKIP: {file_path} — not found", file=sys.stderr)
        return []

    print(f"Processing: {file_path}")

    mapping_data, extra_items, error_info = load_yaml_lenient(file_path)

    if error_info and not mapping_data and not extra_items:
        print(f"  WARN: {file_path} — {error_info}", file=sys.stderr)
        base = os.path.splitext(os.path.basename(file_path))[0]
        return [{
            "target_audit_id": f"{base}_parse_error",
            "verify_id": "parse_error",
            "target_task": "",
            "pc_source": default_pc,
            "shogun_verified": False,
            "audit_passed": False,
            "audited_done": False,
            "verified_at": "",
            "source_file": file_path,
            "entry_type": "error",
            "evidence_state": "schema_unsupported",
            "parse_error": error_info,
        }]

    pc = pc_suffix_from(file_path, mapping_data)
    if error_info:
        print(f"  NOTE: {file_path} — split-parse used ({error_info[:60]}...)", file=sys.stderr)

    entries = []

    verifications = mapping_data.get("verifications", [])
    if isinstance(verifications, list):
        v_entries = extract_from_verifications(verifications, file_path, pc)
        entries.extend(v_entries)
        if v_entries:
            print(f"  -> {len(v_entries)} entries from verifications section")

    if extra_items:
        t_entries = extract_from_top_level_entries(extra_items, file_path, pc)
        entries.extend(t_entries)
        if t_entries:
            print(f"  -> {len(t_entries)} entries from top-level entry blocks")

    return entries


def deduplicate(all_entries):
    """Keep latest entry per target_audit_id (last occurrence wins)."""
    seen = {}
    for e in all_entries:
        tid = e["target_audit_id"]
        seen[tid] = e
    return list(seen.values())


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")

    all_entries = []
    processed_files = []
    skipped_files = []

    for pc_suffix, file_path in INPUT_FILES.items():
        entries = process_file(file_path, pc_suffix)
        if entries:
            all_entries.extend(entries)
            if os.path.exists(file_path):
                processed_files.append(file_path)
        else:
            if not os.path.exists(file_path):
                skipped_files.append(file_path)

    deduped = deduplicate(all_entries)

    by_pc = {}
    for e in deduped:
        pc = e.get("pc_source", "unknown")
        by_pc.setdefault(pc, []).append(e["target_audit_id"])

    shogun_verified_count = sum(1 for e in deduped if e.get("shogun_verified"))
    audited_done_count = sum(1 for e in deduped if e.get("audited_done"))
    error_count = sum(1 for e in deduped if e.get("entry_type") == "error")

    now_jst = datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00")

    output = {
        "generated_at": now_jst,
        "generator": "scripts/normalize_shogun_verification_logs.py",
        "schema_version": "v1.0",
        "source_files": processed_files,
        "skipped_files": skipped_files,
        "summary": {
            "total": len(deduped),
            "shogun_verified": shogun_verified_count,
            "audited_done": audited_done_count,
            "error_entries": error_count,
            "by_pc": {pc: len(ids) for pc, ids in by_pc.items()},
        },
        "verifications": deduped,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"Total entries: {len(deduped)}")
    print(f"  shogun_verified: {shogun_verified_count}")
    print(f"  audited_done: {audited_done_count}")
    print(f"  error_entries: {error_count}")
    for pc, ids in by_pc.items():
        print(f"  {pc}: {len(ids)} entries")
    print("\nDone. exit 0")


if __name__ == "__main__":
    main()
