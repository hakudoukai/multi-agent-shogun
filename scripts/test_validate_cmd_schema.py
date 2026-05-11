"""Tests for validate_cmd_schema.py"""

import pytest
import yaml
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from validate_cmd_schema import validate_file, validate_cmd, _load_simultaneous_reviews


def write_yaml(data: dict, path: Path) -> None:
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def make_valid_cmd(**overrides) -> dict:
    cmd = {
        "id": "cmd_test_001",
        "status": "pending",
        "pc_priority": "mc_first",
        "implementation_pc": "mc_only",
        "execution_strategy": "parallel",
    }
    cmd.update(overrides)
    return cmd


def make_valid_task(**overrides) -> dict:
    task = {
        "task_id": "task_001",
        "dependencies": [],
        "sla": {
            "first_action_within_minutes": 10,
            "final_deadline_iso": "2026-05-11T12:00:00+09:00",
        },
        "start_trigger": "immediate",
    }
    task.update(overrides)
    return task


# ─── V2.1-1: pc_priority ─────────────────────────────────────────────────────

class TestPcPriority:
    def test_missing_pc_priority(self, tmp_path):
        cmd = make_valid_cmd()
        del cmd["pc_priority"]
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v["field"] == "pc_priority" for v in violations)

    def test_invalid_pc_priority_value(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(pc_priority="bogus")]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v["field"] == "pc_priority" for v in violations)

    def test_parallel_without_rationale(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(pc_priority="parallel")]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v["field"] == "pc_priority_rationale" for v in violations)

    def test_parallel_with_rationale_no_pc_violation(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(
            pc_priority="parallel",
            pc_priority_rationale="MC/SC独立実装のため",
        )]}, f)
        violations, _ = validate_file(f, None)
        pc_v = [v for v in violations if v["field"] in ("pc_priority", "pc_priority_rationale")]
        assert pc_v == []

    def test_sc_first_valid(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(pc_priority="sc_first")]}, f)
        violations, code = validate_file(f, None)
        pc_v = [v for v in violations if v["field"] in ("pc_priority", "pc_priority_rationale")]
        assert pc_v == []


# ─── V2.1-1: implementation_pc ───────────────────────────────────────────────

class TestImplementationPc:
    def test_missing_implementation_pc(self, tmp_path):
        cmd = make_valid_cmd()
        del cmd["implementation_pc"]
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v["field"] == "implementation_pc" for v in violations)

    def test_both_without_rationale(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(implementation_pc="both")]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v["field"] == "implementation_pc_rationale" for v in violations)

    def test_both_with_rationale_still_needs_review(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(
            id="cmd_both_001",
            implementation_pc="both",
            implementation_pc_rationale="理由あり",
        )]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        v2_1_3 = [v for v in violations if v.get("rule") == "V2.1-3"]
        assert len(v2_1_3) > 0

    def test_sc_only_no_rationale_needed(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(implementation_pc="sc_only")]}, f)
        violations, _ = validate_file(f, None)
        ipc_v = [v for v in violations if v["field"] in ("implementation_pc", "implementation_pc_rationale")]
        assert ipc_v == []


# ─── V2.1-1: execution_strategy ──────────────────────────────────────────────

class TestExecutionStrategy:
    def test_missing_execution_strategy(self, tmp_path):
        cmd = make_valid_cmd()
        del cmd["execution_strategy"]
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v["field"] == "execution_strategy" for v in violations)

    def test_invalid_execution_strategy(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(execution_strategy="unknown_type")]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v["field"] == "execution_strategy" for v in violations)

    def test_sequential_strategy_valid(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(execution_strategy="sequential")]}, f)
        violations, _ = validate_file(f, None)
        es_v = [v for v in violations if v["field"] == "execution_strategy"]
        assert es_v == []

    def test_staged_strategy_valid(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(execution_strategy="staged")]}, f)
        violations, _ = validate_file(f, None)
        es_v = [v for v in violations if v["field"] == "execution_strategy"]
        assert es_v == []


# ─── Grandfathered ────────────────────────────────────────────────────────────

class TestGrandfathered:
    @pytest.mark.parametrize("status", ["done", "archive", "archived", "cancelled", "canceled"])
    def test_grandfathered_status_skipped(self, tmp_path, status):
        cmd = {"id": "cmd_old_001", "status": status}
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)
        violations, code = validate_file(f, None)
        assert code == 0
        assert violations == []

    def test_active_cmd_not_skipped(self, tmp_path):
        cmd = {"id": "cmd_new_001", "status": "pending"}
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert len(violations) > 0


# ─── V2.1-3: simultaneous implementation review ───────────────────────────────

class TestSimultaneousReview:
    def test_both_with_valid_review_no_v2_1_3_violation(self, tmp_path):
        cmd = make_valid_cmd(
            id="cmd_both_reviewed",
            implementation_pc="both",
            implementation_pc_rationale="理由あり",
        )
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)

        reviews_file = tmp_path / "reviews.yaml"
        write_yaml({
            "reviews": [{
                "cmd_id": "cmd_both_reviewed",
                "reviewed_by": "gunshi",
                "verdict": "pass",
                "reason": "独立実装可能",
                "duplicate_work_risk": "low",
                "ownership_split": {"mc": "frontend実装", "sc": "backend実装"},
            }]
        }, reviews_file)

        import validate_cmd_schema as mod
        orig = mod.SIMULTANEOUS_REVIEWS_FILE
        mod.SIMULTANEOUS_REVIEWS_FILE = reviews_file
        violations, _ = validate_file(f, None)
        mod.SIMULTANEOUS_REVIEWS_FILE = orig

        v2_1_3 = [v for v in violations if v.get("rule") == "V2.1-3"]
        assert v2_1_3 == []

    def test_both_review_verdict_fail_blocked(self, tmp_path):
        cmd = make_valid_cmd(
            id="cmd_both_fail",
            implementation_pc="both",
            implementation_pc_rationale="理由",
        )
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)

        reviews_file = tmp_path / "reviews.yaml"
        write_yaml({
            "reviews": [{
                "cmd_id": "cmd_both_fail",
                "reviewed_by": "gunshi",
                "verdict": "fail",
                "reason": "重複リスク高",
                "duplicate_work_risk": "high",
                "ownership_split": {"mc": "?", "sc": "?"},
            }]
        }, reviews_file)

        import validate_cmd_schema as mod
        orig = mod.SIMULTANEOUS_REVIEWS_FILE
        mod.SIMULTANEOUS_REVIEWS_FILE = reviews_file
        violations, code = validate_file(f, None)
        mod.SIMULTANEOUS_REVIEWS_FILE = orig

        assert code == 1
        v2_1_3 = [v for v in violations if v.get("rule") == "V2.1-3"]
        assert len(v2_1_3) > 0

    def test_both_missing_review_file_blocked(self, tmp_path):
        cmd = make_valid_cmd(
            id="cmd_no_review",
            implementation_pc="both",
            implementation_pc_rationale="理由",
        )
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)

        nonexistent = tmp_path / "no_such_reviews.yaml"
        import validate_cmd_schema as mod
        orig = mod.SIMULTANEOUS_REVIEWS_FILE
        mod.SIMULTANEOUS_REVIEWS_FILE = nonexistent
        violations, code = validate_file(f, None)
        mod.SIMULTANEOUS_REVIEWS_FILE = orig

        assert code == 1
        v2_1_3 = [v for v in violations if v.get("rule") == "V2.1-3"]
        assert len(v2_1_3) > 0

    def test_both_review_missing_ownership_split(self, tmp_path):
        cmd = make_valid_cmd(
            id="cmd_both_no_split",
            implementation_pc="both",
            implementation_pc_rationale="理由",
        )
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd]}, f)

        reviews_file = tmp_path / "reviews.yaml"
        write_yaml({
            "reviews": [{
                "cmd_id": "cmd_both_no_split",
                "reviewed_by": "gunshi",
                "verdict": "pass",
                "reason": "OK",
                "duplicate_work_risk": "low",
                # ownership_split omitted
            }]
        }, reviews_file)

        import validate_cmd_schema as mod
        orig = mod.SIMULTANEOUS_REVIEWS_FILE
        mod.SIMULTANEOUS_REVIEWS_FILE = reviews_file
        violations, code = validate_file(f, None)
        mod.SIMULTANEOUS_REVIEWS_FILE = orig

        assert code == 1
        split_v = [v for v in violations if "ownership_split" in v.get("field", "")]
        assert len(split_v) > 0


# ─── V2.1-6: task-level fields ────────────────────────────────────────────────

class TestTaskLevelFields:
    def test_fully_valid_task(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[make_valid_task()])]}, f)
        violations, code = validate_file(f, None)
        assert code == 0
        assert violations == []

    def test_missing_dependencies(self, tmp_path):
        task = make_valid_task()
        del task["dependencies"]
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "dependencies" for v in violations)

    def test_missing_sla_first_action(self, tmp_path):
        task = make_valid_task()
        task["sla"] = {"final_deadline_iso": "2026-05-11T12:00:00+09:00"}
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.first_action_within_minutes" for v in violations)

    def test_missing_sla_deadline(self, tmp_path):
        task = make_valid_task()
        task["sla"] = {"first_action_within_minutes": 10}
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.final_deadline_iso" for v in violations)

    def test_missing_start_trigger(self, tmp_path):
        task = make_valid_task()
        del task["start_trigger"]
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "start_trigger" for v in violations)

    def test_dependencies_done_with_empty_deps(self, tmp_path):
        task = make_valid_task(start_trigger="dependencies_done", dependencies=[])
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        msg_matches = [v for v in violations if "dependencies_done" in v.get("message", "")]
        assert len(msg_matches) > 0

    def test_dependencies_done_with_nonempty_deps_valid(self, tmp_path):
        task = make_valid_task(start_trigger="dependencies_done", dependencies=["task_prior"])
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, _ = validate_file(f, None)
        dep_trigger_v = [v for v in violations if "dependencies_done" in v.get("message", "")]
        assert dep_trigger_v == []

    def test_dag_dependency_parallel_allowed(self, tmp_path):
        """parallel + non-empty dependencies is valid (DAG allowed per spec)."""
        task1 = make_valid_task(task_id="task_1", start_trigger="immediate")
        task2 = make_valid_task(task_id="task_2", dependencies=["task_1"], start_trigger="dependencies_done")
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(execution_strategy="parallel", tasks=[task1, task2])]}, f)
        violations, _ = validate_file(f, None)
        # DAG deps in parallel should not trigger a violation
        dag_v = [v for v in violations if "parallel" in v.get("message", "").lower() and "depend" in v.get("message", "").lower()]
        assert dag_v == []

    def test_negative_first_action_rejected(self, tmp_path):
        task = make_valid_task()
        task["sla"]["first_action_within_minutes"] = -5
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.first_action_within_minutes" for v in violations)

    def test_zero_first_action_rejected(self, tmp_path):
        task = make_valid_task()
        task["sla"]["first_action_within_minutes"] = 0
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.first_action_within_minutes" for v in violations)

    def test_float_first_action_rejected(self, tmp_path):
        task = make_valid_task()
        task["sla"]["first_action_within_minutes"] = 10.5
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.first_action_within_minutes" for v in violations)

    def test_string_first_action_rejected(self, tmp_path):
        task = make_valid_task()
        task["sla"]["first_action_within_minutes"] = "ten"
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.first_action_within_minutes" for v in violations)

    def test_invalid_iso_deadline_rejected(self, tmp_path):
        task = make_valid_task()
        task["sla"]["final_deadline_iso"] = "not-a-date"
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.final_deadline_iso" for v in violations)

    def test_iso_without_timezone_rejected(self, tmp_path):
        task = make_valid_task()
        task["sla"]["final_deadline_iso"] = "2026-05-11T12:00:00"  # no tz
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        assert any(v.get("field") == "sla.final_deadline_iso" for v in violations)

    def test_iso_with_utc_offset_accepted(self, tmp_path):
        task = make_valid_task()
        task["sla"]["final_deadline_iso"] = "2026-05-11T12:00:00+09:00"
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, _ = validate_file(f, None)
        assert not any(v.get("field") == "sla.final_deadline_iso" for v in violations)

    def test_iso_utc_z_accepted(self, tmp_path):
        task = make_valid_task()
        task["sla"]["final_deadline_iso"] = "2026-05-11T03:00:00+00:00"
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task])]}, f)
        violations, _ = validate_file(f, None)
        assert not any(v.get("field") == "sla.final_deadline_iso" for v in violations)

    def test_multiple_tasks_all_checked(self, tmp_path):
        task_bad1 = make_valid_task(task_id="bad1")
        del task_bad1["dependencies"]
        task_bad2 = make_valid_task(task_id="bad2")
        del task_bad2["start_trigger"]
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[task_bad1, task_bad2])]}, f)
        violations, code = validate_file(f, None)
        assert code == 1
        task_ids_with_violations = {v.get("task_id") for v in violations}
        assert "bad1" in task_ids_with_violations
        assert "bad2" in task_ids_with_violations


# ─── --cmd filter ─────────────────────────────────────────────────────────────

class TestCmdFilter:
    def test_filter_to_valid_cmd_no_violations(self, tmp_path):
        cmd_good = make_valid_cmd(id="cmd_good")
        cmd_bad = {"id": "cmd_bad", "status": "pending"}
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd_good, cmd_bad]}, f)
        violations, code = validate_file(f, "cmd_good")
        assert code == 0

    def test_filter_to_bad_cmd_returns_violations(self, tmp_path):
        cmd_good = make_valid_cmd(id="cmd_good")
        cmd_bad = {"id": "cmd_bad", "status": "pending"}
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [cmd_good, cmd_bad]}, f)
        violations, code = validate_file(f, "cmd_bad")
        assert code == 1
        assert all(v["cmd_id"] == "cmd_bad" for v in violations)


# ─── parse / file errors ──────────────────────────────────────────────────────

class TestParseErrors:
    def test_parse_error_returns_code_2(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text("commands: [{ broken: [\n", encoding="utf-8")
        violations, code = validate_file(f, None)
        assert code == 2
        assert violations == []

    def test_missing_file_returns_code_2(self, tmp_path):
        f = tmp_path / "nonexistent.yaml"
        violations, code = validate_file(f, None)
        assert code == 2
        assert violations == []

    def test_empty_commands_list_valid(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": []}, f)
        violations, code = validate_file(f, None)
        assert code == 0


# ─── full valid command (no tasks) ────────────────────────────────────────────

class TestFullValidCommand:
    def test_fully_valid_command_no_tasks(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd()]}, f)
        violations, code = validate_file(f, None)
        assert code == 0
        assert violations == []

    def test_fully_valid_command_with_task(self, tmp_path):
        f = tmp_path / "cmd.yaml"
        write_yaml({"commands": [make_valid_cmd(tasks=[make_valid_task()])]}, f)
        violations, code = validate_file(f, None)
        assert code == 0
        assert violations == []
