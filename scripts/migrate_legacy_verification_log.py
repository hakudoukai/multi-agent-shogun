#!/usr/bin/env python3
"""
migrate_legacy_verification_log.py — cmd_014 AC3: legacy shogun_verification_log.yaml migration

legacy format (shogun_verification_log.yaml) → new schema (shogun_verification_mainpc_log.yaml)

Actions:
  1. Read legacy entries from shogun_verification_log.yaml
  2. Compute event_id for each entry (same algorithm as normalize_shogun_verification_logs.py)
  3. Dedupe against existing mainpc_log entries
  4. Append new entries to shogun_verification_mainpc_log.yaml
  5. Archive legacy entries to shogun_verification_log_archive.yaml
"""

import argparse
import hashlib
import sys
import warnings
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
REPORT_DIR = PROJECT_ROOT / "queue" / "reports"

LEGACY_LOG = REPORT_DIR / "shogun_verification_log.yaml"
MAINPC_LOG = REPORT_DIR / "shogun_verification_mainpc_log.yaml"
ARCHIVE_LOG = REPORT_DIR / "shogun_verification_log_archive.yaml"

SOURCE_PC = "mainpc"


def stable_event_id(source_pc: str, auditor_who: str, target: str, verified_at: str) -> str:
    raw = f"{source_pc}|{auditor_who}|{target}|{verified_at}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def payload_hash(entry: dict) -> str:
    payload = {
        "checks": entry.get("checks"),
        "flags": entry.get("flags"),
        "audit_entry_excerpt": entry.get("audit_entry_excerpt"),
    }
    canonical = yaml.safe_dump(
        payload, allow_unicode=True, sort_keys=True, default_flow_style=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def load_yaml_verifications(path: Path) -> list[dict]:
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return raw.get("verifications", []) or []


def compute_existing_event_ids(mainpc_entries: list[dict]) -> set[str]:
    seen: set[str] = set()
    for entry in mainpc_entries:
        target = entry.get("target") or entry.get("target_id")
        auditor = entry.get("auditor_who") or "unknown"
        verified_at = entry.get("verified_at")
        if not (isinstance(target, str) and isinstance(verified_at, str)):
            continue
        eid = stable_event_id(SOURCE_PC, str(auditor), target, str(verified_at))
        seen.add(eid)
    return seen


def migrate_entry(legacy: dict) -> tuple[dict | None, str | None]:
    """
    Convert a legacy entry to a mainpc_log entry.
    Returns (entry, skip_reason) — entry=None means skip.
    """
    target = legacy.get("target")
    target_audit_ids = legacy.get("target_audit_ids")

    if target_audit_ids is not None:
        if isinstance(target_audit_ids, list) and len(target_audit_ids) > 0:
            actual_target = str(target_audit_ids[0])
            skipped = target_audit_ids[1:]
            if skipped:
                print(
                    f"  WARN: target_audit_ids has {len(skipped)} extra items"
                    f" beyond first — skipped: {skipped}",
                    file=sys.stderr,
                )
            target = actual_target
        else:
            return None, f"invalid target_audit_ids: {target_audit_ids!r}"

    if not isinstance(target, str) or not target:
        return None, f"missing or invalid target: {target!r}"

    auditor_who = legacy.get("auditor_who") or "unknown"
    verified_at = legacy.get("verified_at")
    if not isinstance(verified_at, str):
        verified_at = str(verified_at) if verified_at is not None else None
    if not verified_at:
        return None, f"missing verified_at in entry target={target!r}"

    eid = stable_event_id(SOURCE_PC, str(auditor_who), target, verified_at)
    p_hash = payload_hash(legacy)

    migrated = dict(legacy)
    migrated["target"] = target
    migrated["source_pc"] = SOURCE_PC
    migrated["event_id"] = eid
    migrated["payload_hash"] = p_hash
    migrated["migration_note"] = "legacy_migrated"
    return migrated, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    parser.add_argument("--legacy-log", default=str(LEGACY_LOG), help="Override legacy log path")
    parser.add_argument("--mainpc-log", default=str(MAINPC_LOG), help="Override mainpc log path")
    parser.add_argument("--archive-log", default=str(ARCHIVE_LOG), help="Override archive path")
    args = parser.parse_args()

    legacy_path = Path(args.legacy_log)
    mainpc_path = Path(args.mainpc_log)
    archive_path = Path(args.archive_log)

    # 1. Load legacy entries
    legacy_entries = load_yaml_verifications(legacy_path)
    if not legacy_entries:
        print(f"ERROR: no entries found in {legacy_path}", file=sys.stderr)
        return 1
    print(f"Loaded {len(legacy_entries)} legacy entries from {legacy_path}", file=sys.stderr)

    # 2. Load existing mainpc_log entries
    existing_entries = load_yaml_verifications(mainpc_path)
    print(f"Existing mainpc_log entries: {len(existing_entries)}", file=sys.stderr)

    # 3. Compute existing event_ids for dedup
    existing_eids = compute_existing_event_ids(existing_entries)
    print(f"Existing event_ids: {len(existing_eids)}", file=sys.stderr)

    # 4. Migrate legacy entries
    new_entries: list[dict] = []
    skipped_dedup = 0
    skipped_invalid = 0

    for entry in legacy_entries:
        migrated, skip_reason = migrate_entry(entry)
        if migrated is None:
            print(f"  WARN: skipping invalid entry — {skip_reason}", file=sys.stderr)
            skipped_invalid += 1
            continue

        eid = migrated["event_id"]
        if eid in existing_eids:
            target = migrated.get("target", "?")
            print(f"  DEDUP: event_id={eid} target={target} already exists — skipped", file=sys.stderr)
            skipped_dedup += 1
            continue

        existing_eids.add(eid)
        new_entries.append(migrated)

    print(
        f"\nMigration summary:",
        file=sys.stderr,
    )
    print(f"  Total legacy:       {len(legacy_entries)}", file=sys.stderr)
    print(f"  Dedup skipped:      {skipped_dedup}", file=sys.stderr)
    print(f"  Invalid skipped:    {skipped_invalid}", file=sys.stderr)
    print(f"  New entries to add: {len(new_entries)}", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] Would append entries to mainpc_log and create archive.", file=sys.stderr)
        return 0

    # 5. Append to mainpc_log
    all_entries = existing_entries + new_entries
    mainpc_data = {"verifications": all_entries}
    mainpc_path.write_text(
        yaml.safe_dump(mainpc_data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(
        f"\nWritten {len(all_entries)} entries to {mainpc_path} "
        f"(was {len(existing_entries)}, added {len(new_entries)})",
        file=sys.stderr,
    )

    # 6. Archive legacy entries
    archive_data = {
        "archive_source": str(legacy_path),
        "archived_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "verifications": legacy_entries,
    }
    archive_path.write_text(
        yaml.safe_dump(archive_data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"Archived {len(legacy_entries)} legacy entries to {archive_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
