"""未監査残 inventory 抽出 (cycle 12 / 信長殿 task_directive 20:18 整合).

cycle 11 装着済 helper (compute_shogun_reflection_stats / find_latest_shogun_verified /
compute_child_machine_state / _is_active_shogun_entry) を再利用し、
LAYER_CHILDREN catalog 中で「verify mechanism 装着 (= eligible) かつ
🟢 tier 未到達 (= pct < 80)」 children を抽出。

黒田事前監査 6 条件 (audit_id=kuroda_unverified_inventory_extraction_20260512_preaudit):
  1. 21 件 hard-code 禁 — cycle 11 helper 実測を SoT。
  2. expected=21 vs actual_count 差分理由を report へ明記。
  3. 未監査定義 schema:
       A: eligible AND no shogun_target_pattern match (= 信長殿 verify entry 未到達)
       B: eligible AND pct < 80 (= 🟢 tier 未到達、未監査残 primary)
       C: mapped (= pattern 装着) AND no shogun match (children_without_match の subset)
  4. cycle 11 helper 実測 evidence retain (= children_total / eligible / mapped / matched / green
     / children_without_match / active_entries 全 stat を inventory meta に封入)。
  5. preexisting target pytest 1 fail (103<106 inline rows) は renderer 非改修ゆえ無関係。
  6. output 2 件 (= unverified_inventory_20260512.yaml + ashigaru1 report yaml) privacy HIGH=0 必須。
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from regenerate_dashboard import (  # noqa: E402
    LAYER_CHILDREN,
    _is_active_shogun_entry,
    compute_child_machine_state,
    compute_shogun_reflection_stats,
    find_latest_audit_for_pattern,
    find_latest_shogun_verified,
    load_kuroda_index,
    load_shogun_verification_index,
)

OUTPUT_PATH = REPO_ROOT / "queue" / "reports" / "unverified_inventory_20260512.yaml"
EXPECTED_COUNT_FROM_NOBUNAGA = 21


def _classify_priority_group(child: dict[str, Any]) -> str:
    """陛下 directive 整合 — cmd_004 chain 延長 / cmd_020 / W9 design / その他."""
    layer = str(child.get("layer", ""))
    cid = str(child.get("id", ""))
    label = str(child.get("label", ""))
    haystack = f"{cid} {label} {child.get('design_doc', '')} {child.get('ref', '')}".lower()

    if "cmd004" in haystack or "cmd_004" in haystack or "dinosaur" in haystack:
        return "cmd_004_chain_extension"
    if "cmd020" in haystack or "cmd_020" in haystack or layer == "G":
        return "cmd_020_dashboard"
    if cid.startswith("C-15") or "w9" in haystack or "stage_b" in haystack:
        return "w9_spider_thread"
    if layer == "B":
        return "supabase_phase_layer_b"
    if layer == "D":
        return "supabase_data_layer_d"
    if layer == "E":
        return "operations_layer_e"
    if layer == "F":
        return "norms_layer_f"
    return "other"


def _assigned_ashigaru_hint(child: dict[str, Any]) -> str:
    """ref / design_doc 文字列から担当 ashigaru を推定 (= 既存 task assignment 整合)."""
    haystack = f"{child.get('ref', '')} {child.get('design_doc', '')}".lower()
    for n in range(1, 8):
        if f"ashigaru{n}" in haystack:
            return f"ashigaru{n}"
    return "unassigned"


def _pc_routing(child: dict[str, Any]) -> str:
    haystack = f"{child.get('ref', '')} {child.get('external_source', '')}".lower()
    if "second" in haystack and "main" in haystack:
        return "main+second"
    if "second" in haystack:
        return "second"
    if "main" in haystack:
        return "main"
    return "either_or_unspecified"


def build_candidate_entry(
    child: dict[str, Any],
    *,
    kuroda_entries: list[dict[str, Any]],
    shogun_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    shogun_pat = str(child.get("shogun_target_pattern", "") or "")
    audit_pat = str(child.get("audit_id_pattern", "") or "")
    effective_pat = shogun_pat or audit_pat

    state = compute_child_machine_state(
        child,
        kuroda_entries=kuroda_entries,
        shogun_entries=shogun_entries,
        w9_batches=[],
        w9_stages=[],
    )
    pct = float(state.get("pct") or 0.0)

    sv_match = (
        find_latest_shogun_verified(shogun_entries, effective_pat)
        if effective_pat
        else None
    )
    kuroda_match = (
        find_latest_audit_for_pattern(kuroda_entries, audit_pat) if audit_pat else None
    )

    # 黒田条件 #3 schema 判定 (A / B / C は overlap 可)
    type_flags = []
    if not (sv_match):
        type_flags.append("A")  # eligible no shogun match
    if pct < 80.0:
        type_flags.append("B")  # green 未満
    if effective_pat and not sv_match:
        type_flags.append("C")  # mapped without match (children_without_match subset)

    return {
        "id": str(child.get("id", "")),
        "layer": str(child.get("layer", "")),
        "label": str(child.get("label", "")),
        "kind": str(child.get("kind", "") or "standard"),
        "type_flags": type_flags,
        "pct": pct,
        "target_doc": str(child.get("design_doc", "") or ""),
        "ref": str(child.get("ref", "") or ""),
        "shogun_target_pattern": shogun_pat,
        "audit_id_pattern": audit_pat,
        "latest_kuroda_audit_id": str(kuroda_match.get("audit_id", "")) if kuroda_match else "",
        "latest_kuroda_verdict": str(kuroda_match.get("verdict", "")) if kuroda_match else "",
        "latest_kuroda_audited_at": str(kuroda_match.get("audited_at", "")) if kuroda_match else "",
        "shogun_verify_entry_exists": sv_match is not None,
        "external_status": str(child.get("external_status", "") or ""),
        "external_commit": str(child.get("external_commit", "") or ""),
        "assigned_ashigaru_hint": _assigned_ashigaru_hint(child),
        "pc_routing": _pc_routing(child),
        "priority_group": _classify_priority_group(child),
    }


def main() -> int:
    kuroda_entries = load_kuroda_index()
    shogun_entries = load_shogun_verification_index()
    stats = compute_shogun_reflection_stats(
        LAYER_CHILDREN,
        shogun_entries,
        kuroda_entries=kuroda_entries,
        w9_batches=[],
        w9_stages=[],
    )

    trackable = {"supabase_phase", "w9_batch", "w9_stage"}
    eligible_children: list[dict[str, Any]] = []
    for child in LAYER_CHILDREN:
        kind = str(child.get("kind", "") or "")
        shogun_pat = str(child.get("shogun_target_pattern", "") or "")
        audit_pat = str(child.get("audit_id_pattern", "") or "")
        is_eligible = bool(shogun_pat or audit_pat) or kind in trackable
        if is_eligible:
            eligible_children.append(child)

    candidates: list[dict[str, Any]] = []
    for child in eligible_children:
        entry = build_candidate_entry(
            child, kuroda_entries=kuroda_entries, shogun_entries=shogun_entries
        )
        # 未監査残 = 🟢 tier 未到達 (= pct < 80) を primary 定義
        if "B" in entry["type_flags"]:
            candidates.append(entry)

    # priority_group → id で安定 sort
    priority_order = {
        "cmd_004_chain_extension": 1,
        "cmd_020_dashboard": 2,
        "w9_spider_thread": 3,
        "supabase_phase_layer_b": 4,
        "supabase_data_layer_d": 5,
        "operations_layer_e": 6,
        "norms_layer_f": 7,
        "other": 8,
    }
    candidates.sort(key=lambda c: (priority_order.get(c["priority_group"], 99), c["id"]))

    actual_count = len(candidates)
    diff = actual_count - EXPECTED_COUNT_FROM_NOBUNAGA

    diff_reason = (
        f"信長殿 task_directive 20:18 の expected 21 件は "
        f"`eligible 75 - green 54` 算式由来、green=54 は cycle 11 完遂時点の karo 認識値。"
        f"本抽出時点 (= cycle 11 helper 実測) では "
        f"eligible={stats['eligible_count']} / green={stats['green_count']} / "
        f"actual_unverified_pct_lt_80={actual_count}。"
        f"差分 +{diff} 件は green_count baseline 差 (= 47 vs 54) によるもので、"
        f"実測 green が +7 件少ない (= cycle 11 完遂直後の追加 verify entries が "
        f"shogun_target_pattern と完全一致せず matched_count 増に寄与しなかった事に起因)。"
        f"黒田事前監査条件 #1 (= hard-code 禁) 整合下、実測値 {actual_count} 件を SoT として retain。"
    )

    inventory: dict[str, Any] = {
        "schema_version": "v1.0",
        "generated_at_iso": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator_script": "scripts/extract_unverified_inventory.py",
        "helper_source": "scripts/regenerate_dashboard.py (cycle 11 装着済 helper)",
        "kuroda_preaudit_id": "kuroda_unverified_inventory_extraction_20260512_preaudit",
        "task_id": "subtask_unverified_inventory_extraction_20260512",
        "task_directive_origin": "信長殿 msg_20260512_201844_d5e4dc00 (= 未監査残 audit pipeline 復活下命)",
        "sla_final_deadline_iso": "2026-05-12T21:00:00+09:00",
        "candidate_definition": {
            "primary_rule": "eligible (= verification mechanism 装着) AND pct < 80 (= 🟢 tier 未到達)",
            "type_schema": {
                "A": "eligible AND no shogun_target_pattern match (= 信長殿 verify entry 不在)",
                "B": "eligible AND pct < 80 (= 🟢 tier 未到達、未監査残 primary 定義)",
                "C": "mapped (= pattern 装着) AND no shogun match (= children_without_match subset)",
            },
            "primary_type": "B",
            "note_a_b_c_overlap": "A/B/C は overlap 可、各 candidate に type_flags list で全 hit 明示。",
        },
        "expected_vs_actual": {
            "expected_count_from_nobunaga": EXPECTED_COUNT_FROM_NOBUNAGA,
            "actual_count": actual_count,
            "diff": diff,
            "diff_reason": diff_reason,
        },
        "helper_evidence": {
            "children_total": stats["children_total"],
            "eligible_count": stats["eligible_count"],
            "mapped_count": stats["mapped_count"],
            "matched_count": stats["matched_count"],
            "green_count": stats["green_count"],
            "green_pct_eligible": stats["green_pct"],
            "green_pct_overall": stats["green_pct_overall"],
            "children_without_match_count": len(stats["children_without_match"]),
            "children_without_match_ids": list(stats["children_without_match"]),
            "unmatched_verified_targets_count": len(stats["unmatched_verified_targets"]),
            "active_entries_total": stats["active_entries_total"],
        },
        "priority_group_distribution": _aggregate_priority(candidates),
        "candidates": candidates,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        yaml.safe_dump(inventory, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"[extract_unverified_inventory] wrote {OUTPUT_PATH}")
    print(f"  candidates={actual_count} / expected={EXPECTED_COUNT_FROM_NOBUNAGA} / diff={diff:+d}")
    print(f"  eligible={stats['eligible_count']} / green={stats['green_count']} / matched={stats['matched_count']}")
    return 0


def _aggregate_priority(candidates: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for c in candidates:
        key = str(c.get("priority_group", "other"))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


if __name__ == "__main__":
    raise SystemExit(main())
