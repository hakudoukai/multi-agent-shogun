#!/usr/bin/env python3
"""
validate_cross_pc_directive.py — V2.1-2 MC→SC directive gate validator.

Required fields: source_pc, source_agent, target_pc, target_agent, directive_type, via_agent
Gate rule: source_pc=main_pc AND target_pc=second_pc → via_agent must be second_pc.shogun

Blocked attempts are appended to queue/reports/directive_gate_log.yaml.

Exit codes:
  0 = valid
  1 = gate_violation
  2 = parse_error
"""

import argparse
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
GATE_LOG_FILE = PROJECT_ROOT / "queue" / "reports" / "directive_gate_log.yaml"

REQUIRED_FIELDS = [
    "source_pc",
    "source_agent",
    "target_pc",
    "target_agent",
    "directive_type",
    "via_agent",
]


def _append_gate_log(entry: dict) -> None:
    """Append a blocked attempt record to directive_gate_log.yaml."""
    GATE_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if GATE_LOG_FILE.exists():
        try:
            data = yaml.safe_load(GATE_LOG_FILE.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            data = {}
    else:
        data = {}

    if not isinstance(data, dict):
        data = {}
    if not isinstance(data.get("blocked_directives"), list):
        data["blocked_directives"] = []

    data["blocked_directives"].append(entry)
    GATE_LOG_FILE.write_text(
        yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def validate_directive(directive: dict, source_file: str) -> list[dict]:
    """
    Validate a directive dict against V2.1-2 gate rules.

    Returns a list of gate_violation dicts (empty list = valid).
    """
    violations = []

    for field in REQUIRED_FIELDS:
        if field not in directive or not directive[field]:
            violations.append({
                "rule": "V2.1-2",
                "field": field,
                "message": f"Required field '{field}' is missing or empty",
                "source_file": source_file,
            })

    if violations:
        return violations

    source_pc = str(directive["source_pc"]).lower()
    target_pc = str(directive["target_pc"]).lower()
    via_agent = str(directive["via_agent"]).lower()

    if source_pc == "main_pc" and target_pc == "second_pc":
        if via_agent != "second_pc.shogun":
            violations.append({
                "rule": "V2.1-2",
                "field": "via_agent",
                "message": (
                    f"MC→SC directive must route via second_pc.shogun "
                    f"(got via_agent='{directive['via_agent']}'). "
                    "Allowed path: MC Shogun → MC Karo → Ieyasu/SecondPC Shogun → SC Karo → SC agents"
                ),
                "source_pc": directive["source_pc"],
                "source_agent": directive["source_agent"],
                "target_pc": directive["target_pc"],
                "target_agent": directive["target_agent"],
                "directive_type": directive["directive_type"],
                "source_file": source_file,
            })

    return violations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate MC→SC directive routing gate (V2.1-2)."
    )
    parser.add_argument("directive_yaml", help="Path to directive YAML file")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any violation (same as default)")
    args = parser.parse_args()

    directive_file = Path(args.directive_yaml)

    if not directive_file.exists():
        print(f"ERROR: {directive_file} not found", file=sys.stderr)
        sys.exit(2)

    try:
        data = yaml.safe_load(directive_file.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: parse error in {directive_file}: {exc}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(data, dict):
        print(f"ERROR: unexpected top-level type in {directive_file}", file=sys.stderr)
        sys.exit(2)

    source_file = str(directive_file)
    violations = validate_directive(data, source_file)

    if violations:
        for v in violations:
            print(f"[GATE_VIOLATION][{v.get('rule', 'V2.1-2')}] field={v.get('field')} | {v.get('message')}")

        log_entry = {
            "blocked_at": datetime.now(timezone.utc).isoformat(),
            "source_file": source_file,
            "directive_type": data.get("directive_type", "unknown"),
            "source_pc": data.get("source_pc", "unknown"),
            "source_agent": data.get("source_agent", "unknown"),
            "target_pc": data.get("target_pc", "unknown"),
            "target_agent": data.get("target_agent", "unknown"),
            "via_agent": data.get("via_agent", "unknown"),
            "violations": violations,
        }
        _append_gate_log(log_entry)
        print(f"\n{len(violations)} gate violation(s) → blocked, recorded in {GATE_LOG_FILE}")
        sys.exit(1)

    print("OK: directive routing is valid")
    sys.exit(0)


if __name__ == "__main__":
    main()
