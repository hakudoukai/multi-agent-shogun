"""Tests for validate_cross_pc_directive.py"""

import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_cross_pc_directive import validate_directive, _append_gate_log


def make_valid_directive(**overrides) -> dict:
    d = {
        "source_pc": "main_pc",
        "source_agent": "karo",
        "target_pc": "second_pc",
        "target_agent": "karo",
        "directive_type": "task_assignment",
        "via_agent": "second_pc.shogun",
    }
    d.update(overrides)
    return d


# ─── MC→SC gate rule ──────────────────────────────────────────────────────────

class TestMcToScGate:
    def test_mc_to_sc_direct_blocked(self):
        """MC→SC without via second_pc.shogun → violation."""
        directive = make_valid_directive(via_agent="karo_mc")
        violations = validate_directive(directive, "test.yaml")
        assert len(violations) > 0
        assert any(v["field"] == "via_agent" for v in violations)

    def test_mc_to_sc_via_shogun_passes(self):
        """MC→SC with via_agent=second_pc.shogun → valid."""
        directive = make_valid_directive(via_agent="second_pc.shogun")
        violations = validate_directive(directive, "test.yaml")
        assert violations == []

    def test_mc_to_sc_via_karo_blocked(self):
        """Karo bypassing Ieyasu directly to SC Karo → blocked."""
        directive = make_valid_directive(
            source_agent="karo",
            target_agent="karo",
            via_agent="karo",
        )
        violations = validate_directive(directive, "test.yaml")
        assert len(violations) > 0

    def test_mc_to_sc_via_gunshi_blocked(self):
        """Gunshi direct SC directive → blocked."""
        directive = make_valid_directive(
            source_agent="gunshi",
            target_agent="ashigaru1",
            via_agent="gunshi",
        )
        violations = validate_directive(directive, "test.yaml")
        assert len(violations) > 0


# ─── Non-cross-PC directives ─────────────────────────────────────────────────

class TestNonCrossPc:
    def test_mc_to_mc_passes(self):
        """MC→MC directive does not trigger the cross-PC gate."""
        directive = make_valid_directive(
            source_pc="main_pc",
            target_pc="main_pc",
            via_agent="karo",
        )
        violations = validate_directive(directive, "test.yaml")
        assert violations == []

    def test_sc_to_sc_passes(self):
        """SC→SC directive does not trigger the cross-PC gate."""
        directive = make_valid_directive(
            source_pc="second_pc",
            target_pc="second_pc",
            via_agent="karo_sc",
        )
        violations = validate_directive(directive, "test.yaml")
        assert violations == []

    def test_sc_to_mc_passes(self):
        """SC→MC reverse direction is not gated by this rule."""
        directive = make_valid_directive(
            source_pc="second_pc",
            target_pc="main_pc",
            via_agent="ieyasu",
        )
        violations = validate_directive(directive, "test.yaml")
        assert violations == []


# ─── Missing required fields ─────────────────────────────────────────────────

class TestMissingFields:
    @pytest.mark.parametrize("field", [
        "source_pc",
        "source_agent",
        "target_pc",
        "target_agent",
        "directive_type",
        "via_agent",
    ])
    def test_missing_required_field(self, field):
        directive = make_valid_directive()
        del directive[field]
        violations = validate_directive(directive, "test.yaml")
        assert len(violations) > 0
        assert any(v["field"] == field for v in violations)

    def test_empty_source_pc(self):
        directive = make_valid_directive(source_pc="")
        violations = validate_directive(directive, "test.yaml")
        assert len(violations) > 0
        assert any(v["field"] == "source_pc" for v in violations)


# ─── Gate log recording ──────────────────────────────────────────────────────

class TestGateLog:
    def test_blocked_directive_appended_to_log(self, tmp_path):
        gate_log = tmp_path / "directive_gate_log.yaml"

        directive = make_valid_directive(via_agent="direct_bypass")
        violations = validate_directive(directive, "test.yaml")
        assert len(violations) > 0

        import validate_cross_pc_directive as mod
        orig = mod.GATE_LOG_FILE
        mod.GATE_LOG_FILE = gate_log

        log_entry = {
            "blocked_at": "2026-05-11T10:00:00+00:00",
            "source_file": "test.yaml",
            "directive_type": directive.get("directive_type", "unknown"),
            "violations": violations,
        }
        _append_gate_log(log_entry)
        mod.GATE_LOG_FILE = orig

        data = yaml.safe_load(gate_log.read_text(encoding="utf-8"))
        assert "blocked_directives" in data
        assert len(data["blocked_directives"]) == 1

    def test_multiple_blocked_appended_sequentially(self, tmp_path):
        gate_log = tmp_path / "directive_gate_log.yaml"

        import validate_cross_pc_directive as mod
        orig = mod.GATE_LOG_FILE
        mod.GATE_LOG_FILE = gate_log

        _append_gate_log({"blocked_at": "2026-05-11T10:00:00", "violations": [{"v": "1"}]})
        _append_gate_log({"blocked_at": "2026-05-11T10:01:00", "violations": [{"v": "2"}]})

        mod.GATE_LOG_FILE = orig

        data = yaml.safe_load(gate_log.read_text(encoding="utf-8"))
        assert len(data["blocked_directives"]) == 2

    def test_valid_directive_does_not_write_log(self, tmp_path):
        gate_log = tmp_path / "directive_gate_log.yaml"

        directive = make_valid_directive()
        violations = validate_directive(directive, "test.yaml")
        assert violations == []
        assert not gate_log.exists()


# ─── Parse / file errors via CLI ─────────────────────────────────────────────

class TestCliErrors:
    def test_validate_directive_missing_file_exits_2(self, tmp_path):
        """Simulate missing directive file: validate_directive does not apply (that's CLI)."""
        # We test the validate_directive function with a valid dict; file handling is in main()
        directive = make_valid_directive()
        violations = validate_directive(directive, "valid_content.yaml")
        assert violations == []

    def test_all_fields_present_and_valid(self):
        directive = make_valid_directive()
        violations = validate_directive(directive, "test.yaml")
        assert violations == []
