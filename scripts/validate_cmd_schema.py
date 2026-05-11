#!/usr/bin/env python3
"""
validate_cmd_schema.py — V2.1 command schema validator.

Validates YAML command files (e.g. queue/shogun_to_karo.yaml) for:
  V2.1-1: pc_priority + implementation_pc + execution_strategy required fields
  V2.1-3: implementation_pc=both requires simultaneous_implementation_review (pass, gunshi)
  V2.1-6: task-level dependencies / sla / start_trigger required fields

Grandfathered: commands with status in {done, archive, archived, cancelled} are skipped.

Exit codes:
  0 = valid (no violations)
  1 = template_violation found
  2 = parse_error
"""

import argparse
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SIMULTANEOUS_REVIEWS_FILE = PROJECT_ROOT / "queue" / "reports" / "simultaneous_implementation_reviews.yaml"

VALID_PC_PRIORITY = {"sc_first", "mc_first", "parallel"}
VALID_IMPLEMENTATION_PC = {"mc_only", "sc_only", "both"}
VALID_EXECUTION_STRATEGY = {"parallel", "sequential", "staged"}
VALID_START_TRIGGER = {"immediate", "dependencies_done", "lord_approval", "gate_open"}
GRANDFATHERED_STATUSES = {"done", "archive", "archived", "cancelled", "canceled"}


def _is_grandfathered(cmd: dict) -> bool:
    return str(cmd.get("status", "")).lower() in GRANDFATHERED_STATUSES


def _load_simultaneous_reviews() -> dict:
    """Load simultaneous_implementation_reviews.yaml. Returns dict keyed by cmd_id."""
    if not SIMULTANEOUS_REVIEWS_FILE.exists():
        return {}
    try:
        data = yaml.safe_load(SIMULTANEOUS_REVIEWS_FILE.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}
    reviews = {}
    for entry in (data.get("reviews") or []):
        if isinstance(entry, dict) and "cmd_id" in entry:
            reviews[entry["cmd_id"]] = entry
    return reviews


def _validate_iso_datetime_with_tz(
    value: str, cmd_id: str, field: str, task_id: str | None, violations: list
) -> None:
    """Validate that value is an ISO 8601 datetime string with timezone offset."""
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M%z",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                break
            return
        except ValueError:
            continue
    violations.append(_v(
        cmd_id, "V2.1-6", field,
        f"{field} must be an ISO 8601 datetime with timezone (e.g. 2026-05-11T12:00:00+09:00), got {value!r}",
        task_id=task_id
    ))


def _v(cmd_id: str, rule: str, field: str, message: str, task_id: str | None = None) -> dict:
    entry: dict = {
        "cmd_id": cmd_id,
        "rule": rule,
        "field": field,
        "message": message,
        "dispatch_gate": "blocked",
    }
    if task_id is not None:
        entry["task_id"] = task_id
    return entry


def _validate_v2_1_1(cmd: dict, cmd_id: str, violations: list) -> None:
    """V2.1-1: pc_priority + implementation_pc + execution_strategy."""
    pc_priority = cmd.get("pc_priority")
    if not pc_priority:
        violations.append(_v(cmd_id, "V2.1-1", "pc_priority", "pc_priority field is required"))
    elif str(pc_priority).lower() not in VALID_PC_PRIORITY:
        violations.append(_v(
            cmd_id, "V2.1-1", "pc_priority",
            f"pc_priority must be one of {VALID_PC_PRIORITY}, got '{pc_priority}'"
        ))
    elif str(pc_priority).lower() == "parallel" and not cmd.get("pc_priority_rationale"):
        violations.append(_v(
            cmd_id, "V2.1-1", "pc_priority_rationale",
            "pc_priority_rationale is required when pc_priority=parallel"
        ))

    impl_pc = cmd.get("implementation_pc")
    if not impl_pc:
        violations.append(_v(cmd_id, "V2.1-1", "implementation_pc", "implementation_pc field is required"))
    elif str(impl_pc).lower() not in VALID_IMPLEMENTATION_PC:
        violations.append(_v(
            cmd_id, "V2.1-1", "implementation_pc",
            f"implementation_pc must be one of {VALID_IMPLEMENTATION_PC}, got '{impl_pc}'"
        ))
    elif str(impl_pc).lower() == "both" and not cmd.get("implementation_pc_rationale"):
        violations.append(_v(
            cmd_id, "V2.1-1", "implementation_pc_rationale",
            "implementation_pc_rationale is required when implementation_pc=both"
        ))

    exec_strategy = cmd.get("execution_strategy")
    if not exec_strategy:
        violations.append(_v(cmd_id, "V2.1-6", "execution_strategy", "execution_strategy field is required"))
    elif str(exec_strategy).lower() not in VALID_EXECUTION_STRATEGY:
        violations.append(_v(
            cmd_id, "V2.1-6", "execution_strategy",
            f"execution_strategy must be one of {VALID_EXECUTION_STRATEGY}, got '{exec_strategy}'"
        ))


def _validate_v2_1_3(cmd: dict, cmd_id: str, violations: list, reviews: dict) -> None:
    """V2.1-3: implementation_pc=both requires a passing Gunshi review."""
    if str(cmd.get("implementation_pc", "")).lower() != "both":
        return

    review = reviews.get(cmd_id)
    if not review:
        violations.append(_v(
            cmd_id, "V2.1-3", "simultaneous_implementation_review",
            "implementation_pc=both requires a pass review in simultaneous_implementation_reviews.yaml"
        ))
        return

    if str(review.get("reviewed_by", "")).lower() != "gunshi":
        violations.append(_v(
            cmd_id, "V2.1-3", "simultaneous_implementation_review.reviewed_by",
            "simultaneous_implementation_review must be reviewed_by=gunshi"
        ))

    if str(review.get("verdict", "")).lower() != "pass":
        violations.append(_v(
            cmd_id, "V2.1-3", "simultaneous_implementation_review.verdict",
            f"simultaneous_implementation_review.verdict must be pass, got '{review.get('verdict')}'"
        ))

    ownership = review.get("ownership_split") or {}
    if not isinstance(ownership, dict) or not ownership.get("mc") or not ownership.get("sc"):
        violations.append(_v(
            cmd_id, "V2.1-3", "simultaneous_implementation_review.ownership_split",
            "simultaneous_implementation_review.ownership_split must have mc and sc entries"
        ))


def _validate_task_v2_1_6(task: dict, cmd_id: str, task_idx: int, violations: list) -> None:
    """V2.1-6: task-level dependencies / sla / start_trigger."""
    task_id = task.get("task_id", f"task[{task_idx}]")

    if "dependencies" not in task:
        violations.append(_v(
            cmd_id, "V2.1-6", "dependencies",
            "task.dependencies array is required", task_id=task_id
        ))

    sla = task.get("sla") or {}
    first_action = sla.get("first_action_within_minutes") if isinstance(sla, dict) else None
    if first_action is None:
        violations.append(_v(
            cmd_id, "V2.1-6", "sla.first_action_within_minutes",
            "task.sla.first_action_within_minutes is required", task_id=task_id
        ))
    elif not isinstance(first_action, int) or isinstance(first_action, bool) or first_action <= 0:
        violations.append(_v(
            cmd_id, "V2.1-6", "sla.first_action_within_minutes",
            f"task.sla.first_action_within_minutes must be a positive integer, got {first_action!r}",
            task_id=task_id
        ))

    final_deadline = sla.get("final_deadline_iso") if isinstance(sla, dict) else None
    if not final_deadline:
        violations.append(_v(
            cmd_id, "V2.1-6", "sla.final_deadline_iso",
            "task.sla.final_deadline_iso is required", task_id=task_id
        ))
    else:
        _validate_iso_datetime_with_tz(str(final_deadline), cmd_id, "sla.final_deadline_iso", task_id, violations)

    start_trigger = task.get("start_trigger")
    if not start_trigger:
        violations.append(_v(
            cmd_id, "V2.1-6", "start_trigger",
            "task.start_trigger is required", task_id=task_id
        ))
    elif str(start_trigger).lower() not in VALID_START_TRIGGER:
        violations.append(_v(
            cmd_id, "V2.1-6", "start_trigger",
            f"task.start_trigger must be one of {VALID_START_TRIGGER}, got '{start_trigger}'",
            task_id=task_id
        ))
    elif str(start_trigger).lower() == "dependencies_done":
        deps = task.get("dependencies") or []
        if isinstance(deps, list) and len(deps) == 0:
            violations.append(_v(
                cmd_id, "V2.1-6", "dependencies",
                "start_trigger=dependencies_done requires non-empty dependencies array",
                task_id=task_id
            ))


def _check_tracked_files_gate(cmd: dict, cmd_id: str, violations: list) -> None:
    """V2.1-3 gate: if implementation_pc is set, warn if declared scripts/ files are already tracked.

    Prevents duplicate-commit errors when the same script is ordered to both PCs.
    Checks target_files field (list of file paths) against git ls-files output.
    """
    impl_pc = str(cmd.get("implementation_pc", "")).lower()
    if impl_pc not in {"both", "mc_only", "sc_only"}:
        return

    target_files = cmd.get("target_files") or []
    if isinstance(target_files, str):
        target_files = [target_files]
    if not isinstance(target_files, list):
        return

    scripts_files = [str(f) for f in target_files if str(f).startswith("scripts/")]
    if not scripts_files:
        return

    for filepath in scripts_files:
        try:
            result = subprocess.run(
                ["git", "ls-files", "--", filepath],
                capture_output=True, text=True, timeout=5,
            )
            if result.stdout.strip():
                msg = (
                    f"implementation_pc={impl_pc} declares '{filepath}' but it is already "
                    "git-tracked — potential duplicate commit across PCs"
                )
                print(f"WARNING: [V2.1-3-gate] {msg}", file=sys.stderr)
                violations.append(_v(cmd_id, "V2.1-3-gate", "target_files", msg))
        except Exception:
            pass


def validate_cmd(cmd: dict, cmd_id: str, reviews: dict, violations: list) -> None:
    """Run all V2.1 checks on a single command."""
    if _is_grandfathered(cmd):
        return
    _validate_v2_1_1(cmd, cmd_id, violations)
    _validate_v2_1_3(cmd, cmd_id, violations, reviews)
    _check_tracked_files_gate(cmd, cmd_id, violations)
    for idx, task in enumerate(cmd.get("tasks") or []):
        if isinstance(task, dict):
            _validate_task_v2_1_6(task, cmd_id, idx, violations)


def validate_file(yaml_file: Path, target_cmd_id: str | None) -> tuple[list, int]:
    """
    Validate all (or one) command(s) in a YAML file.

    Returns (violations, exit_code) where exit_code is 0=valid, 1=violations, 2=parse_error.
    """
    if not yaml_file.exists():
        print(f"ERROR: {yaml_file} not found", file=sys.stderr)
        return [], 2

    try:
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: parse error in {yaml_file}: {exc}", file=sys.stderr)
        return [], 2

    if not isinstance(data, dict):
        print(f"ERROR: unexpected top-level type in {yaml_file}", file=sys.stderr)
        return [], 2

    commands = data.get("commands") or []
    if not isinstance(commands, list):
        print(f"ERROR: 'commands' is not a list in {yaml_file}", file=sys.stderr)
        return [], 2

    reviews = _load_simultaneous_reviews()
    violations: list = []

    for cmd in commands:
        if not isinstance(cmd, dict):
            continue
        cmd_id = str(cmd.get("id", "unknown"))
        if target_cmd_id and cmd_id != target_cmd_id:
            continue
        validate_cmd(cmd, cmd_id, reviews, violations)

    return violations, (1 if violations else 0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate V2.1 command schema (pc_priority, implementation_pc, execution_strategy, SLA)."
    )
    parser.add_argument("yaml_file", help="Path to YAML file (e.g. queue/shogun_to_karo.yaml)")
    parser.add_argument("--cmd", metavar="CMD_ID", help="Validate only this cmd_id")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any violation")
    args = parser.parse_args()

    violations, exit_code = validate_file(Path(args.yaml_file), args.cmd)

    if violations:
        for v in violations:
            parts = [f"[VIOLATION][{v.get('rule', '?')}]"]
            if "task_id" in v:
                parts.append(f"cmd={v['cmd_id']} task={v['task_id']}")
            else:
                parts.append(f"cmd={v['cmd_id']}")
            parts.append(f"field={v['field']}")
            parts.append(v["message"])
            parts.append(f"dispatch_gate={v['dispatch_gate']}")
            print(" | ".join(parts))
        print(f"\n{len(violations)} violation(s) found → dispatch_gate: blocked")
        sys.exit(exit_code)
    else:
        print("OK: no violations found")
        sys.exit(0)


if __name__ == "__main__":
    main()
