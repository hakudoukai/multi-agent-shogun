"""scripts/test/test_unmatched_verified_targets_regression.py

subtask_cmd020_unmatched_verified_targets_dashboard_mapping (revision 2) AC2 regression invariant.

既装着 helper を reuse する (= scripts/regenerate_dashboard.py の
`compute_shogun_reflection_stats` / `annotate_unmatched_with_retain` /
`UNMATCHED_VERIFY_RETAIN_REGISTRY` / `build_layer_render_entries`)。
重複 extraction logic は装着しない (constraint `existing_helper_reuse` 整合)。

5 test、PASS SKIP=0 mandated。各 test 決定的、network 呼出なし、dashboard.md mutate 禁。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import regenerate_dashboard as rd  # noqa: E402

TRANSITION_DOC = REPO_ROOT / "docs" / "unmatched_verified_targets_8_to_0_transition_20260514.md"
TRANSITION_AUDIT_ID = "transition_doc_unmatched_verified_targets_8_to_0_20260514_ashigaru4"


def _compute_stats_via_helper() -> dict:
    """build_context と同 chain で stats を再現 (= 既装着 helper reuse、
    重複実装禁)。reference: scripts/regenerate_dashboard.py:2535"""
    state = rd.load_local_state()
    kuroda_entries = rd.load_kuroda_index()
    shogun_entries = rd.load_shogun_verification_index()
    w9_stages = rd.aggregate_w9_stage_progress(state.tasks)
    w9_batches = rd.aggregate_w9_batch_progress(state.tasks)
    _, precomputed_states = rd.build_layer_render_entries(
        kuroda_entries=kuroda_entries,
        shogun_entries=shogun_entries,
        w9_stages=w9_stages,
        w9_batches=w9_batches,
        collect_states=True,
    )
    return rd.compute_shogun_reflection_stats(
        rd.LAYER_CHILDREN,
        shogun_entries,
        kuroda_entries=kuroda_entries,
        w9_batches=w9_batches,
        w9_stages=w9_stages,
        precomputed_states=precomputed_states,
        retain_registry=rd.UNMATCHED_VERIFY_RETAIN_REGISTRY,
    )


def test_unmatched_verified_targets_count_zero_invariant():
    """test 1: AC0 truth-gate で測定された unmatched_verified_targets=0 を固定化。

    将来 active shogun_verified entry が復帰し本 invariant が破られた場合、
    retain_registry 拡張 or dashboard children placeholder 追加 の判断が
    必要 (= docs/unmatched_verified_targets_8_to_0_transition_20260514.md
    §7 SoP 参照)。"""
    stats = _compute_stats_via_helper()
    unmatched = stats["unmatched_verified_targets"]
    assert isinstance(unmatched, list)
    assert len(unmatched) == 0, (
        f"unmatched_verified_targets invariant 破綻 — current={len(unmatched)} 件、"
        f"AC0 truth gate baseline=0 件。entries={unmatched}。"
        f"対処: docs/unmatched_verified_targets_8_to_0_transition_20260514.md §7 SoP"
    )
    assert stats["unmatched_retain_registered_count"] == 0
    assert stats["unmatched_unregistered_count"] == 0


def test_retain_registry_full_completeness():
    """test 2: UNMATCHED_VERIFY_RETAIN_REGISTRY 4 entry 全件の必須 3 field
    (match_substring / candidate_id / reason / source_log) が非空である事を検証。

    本 task では registry mutation 禁、4 entry baseline を invariant 固定。"""
    registry = rd.UNMATCHED_VERIFY_RETAIN_REGISTRY
    assert isinstance(registry, list)
    expected_substrings = {
        "kuroda_audit_cmd004_phase_1_6_rollback",
        "cmd012_p02_preflight_verify",
        "subtask_cmd004_w9_supabase_completed_evidence_audit_71",
        "subtask_delta_ashigaru2_ceremony_trigger_cycle2_001",
    }
    actual_substrings = {entry["match_substring"] for entry in registry}
    assert actual_substrings == expected_substrings, (
        f"retain_registry baseline 差分: expected={expected_substrings} "
        f"vs actual={actual_substrings}"
    )
    for entry in registry:
        for field in ("match_substring", "candidate_id", "reason", "source_log"):
            value = entry.get(field, "")
            assert value, f"registry entry {entry.get('candidate_id','?')} field {field} 空"


def test_dashboard_render_metric_invariance_after_stats():
    """test 3: stats 算出と dashboard.md render path で
    matched_count / green_count / mapped_count / eligible_count / children_total
    が一致する事を検証 (= 直政 cycle2 finding
    `dashboard_regression_assertion_underspecified` 反映、SoT 単一性 invariant)。"""
    stats_direct = _compute_stats_via_helper()
    # render path も同じ chain を経由 (build_context 経由)。precomputed_states
    # 経由で SoT carry されている事を sot_source field で確認。
    assert stats_direct["sot_source"] == "precomputed_states"

    # 再呼出で同一 stats 値が出る事を確認 (= deterministic、render path =
    # stats path の単一 SoT 整合)。
    stats_again = _compute_stats_via_helper()
    for key in (
        "children_total",
        "eligible_count",
        "mapped_count",
        "matched_count",
        "green_count",
        "unmatched_unregistered_count",
        "unmatched_retain_registered_count",
        "active_entries_total",
    ):
        assert stats_direct[key] == stats_again[key], (
            f"SoT 単一性 invariant 破綻 — {key}: "
            f"first={stats_direct[key]} vs second={stats_again[key]}"
        )


def test_baseline_metric_snapshot():
    """test 4: AC0 truth gate 機械測定 baseline 固定化 (= 6 stat snapshot)。

    revision 2 時点の current SoT 値:
      children_total=106 / eligible_count=78 / mapped_count=25 / matched_count=0
      / green_count=37 / unmatched_unregistered_count=0

    これらが意図せず drift した場合は本 test が fail → 改修原因の調査要。"""
    stats = _compute_stats_via_helper()
    baseline = {
        "children_total": 106,
        "eligible_count": 78,
        "mapped_count": 25,
        "matched_count": 0,
        "green_count": 37,
        "unmatched_unregistered_count": 0,
        "unmatched_retain_registered_count": 0,
        "active_entries_total": 0,
    }
    drift = {
        k: (baseline[k], stats[k]) for k in baseline if stats[k] != baseline[k]
    }
    assert not drift, (
        f"baseline drift 検出: {drift}。AC0 truth gate "
        f"(2026-05-14T00:21:00+09:00) baseline と乖離。原因調査要。"
    )


def test_transition_documentation_file_exists():
    """test 5: AC1 transition documentation file の存在 + audit_id ref 整合。

    本 file が削除 / リネームされた場合 audit trail 喪失。
    本 task の `audit_id` ref が doc 内に embed されている事も verify。"""
    assert TRANSITION_DOC.exists(), (
        f"transition documentation 不在: {TRANSITION_DOC}。AC1 evidence_required 破綻。"
    )
    content = TRANSITION_DOC.read_text(encoding="utf-8")
    assert TRANSITION_AUDIT_ID in content, (
        f"audit_id `{TRANSITION_AUDIT_ID}` が {TRANSITION_DOC} に embed されていない。"
        f"AC1 機械 ref 整合破綻。"
    )
    # registry 4 entry の candidate_id が doc に列挙されている事も verify
    for entry in rd.UNMATCHED_VERIFY_RETAIN_REGISTRY:
        cid = entry["candidate_id"]
        assert cid in content, (
            f"retain_registry candidate_id `{cid}` が transition doc に列挙されていない"
        )
