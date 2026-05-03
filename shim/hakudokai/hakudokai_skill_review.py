#!/usr/bin/env python3
"""
hakudokai_skill_review.py — 山ちゃん graduation 評価機構 (Phase B-3 task 2+5)

副医院長宛に届いた skill_candidate を山ちゃんが strict 評価し、graduation 推奨 / 保留 /
不要を判定。pattern_repeated_2_plus は過去 dev_lessons / handshake から自動検出する。

設計: docs/skill-discovery.md §2 graduation flow + §5 自動チェック準拠

Usage:
  hakudokai_skill_review.py --list                                # pending skill_candidate 一覧
  hakudokai_skill_review.py --review HANDSHAKE_ID                 # 1 件の skill_candidate を評価 (placeholder + pattern check)
  hakudokai_skill_review.py --review HANDSHAKE_ID --decision graduate
  hakudokai_skill_review.py --review HANDSHAKE_ID --decision hold
  hakudokai_skill_review.py --review HANDSHAKE_ID --decision reject

decision:
  graduate: ✅ graduation 推奨 → 副医院長承認要請 INSERT
  hold:     🟡 1 度保留 → クロちゃんへ「次回同パターン発生時に再評価」通知
  reject:   🔴 graduation 不要 → 山ちゃん review コメント INSERT のみ

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[skill_review] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)


CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[skill_review] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _list_pending(sb) -> list[dict]:
    """unack の skill_candidate を topic prefix で抽出。"""
    res = (
        sb.table("pc_handshake")
        .select("id,from_pc,topic,context_data,created_at")
        .eq("clinic_id", CLINIC_ID)
        .is_("acknowledged_at", "null")
        .like("topic", "[skill_candidate] %")
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    items = res.data or []
    return [
        h for h in items
        if (h.get("context_data") or {}).get("shogun_kind") == "skill_candidate"
    ]


def _fetch_handshake(sb, hid: str) -> dict | None:
    """Codex audit B-3-3 #1 修正: clinic_id filter を必須化、Phase R2 RLS 整合。"""
    res = (
        sb.table("pc_handshake")
        .select("id,from_pc,to_pc,topic,content,context_data,created_at,clinic_id")
        .eq("id", hid)
        .eq("clinic_id", CLINIC_ID)
        .execute()
    )
    return res.data[0] if res.data else None


def _pattern_repeated_check(sb, skill_name: str) -> dict:
    """過去 dev_lessons + handshake で skill_name の出現を検索。
    2 回以上ヒット → pattern_repeated_2_plus 自動証明。

    Codex audit B-3-3 #1 修正: pc_handshake は clinic_id filter で boundary 厳守。
    dev_lessons は現状 clinic_id 列を持たない (Phase B-4 task 2 で全 4AI tables へ
    clinic_id 列追加予定、PHASE_B_ROADMAP §4)。本実装は Phase A の dev_lessons 共有運用
    を前提とし、Phase B-4 完了後に本関数も clinic_id filter 追加する。
    """
    result = {
        "dev_lessons_hits": 0,
        "handshake_hits": 0,
        "pattern_repeated_2_plus": False,
        "evidence": [],
    }
    # dev_lessons tags @> {skill_name}
    # NOTE: dev_lessons は clinic_id 列なし (Phase B-4 で追加予定)、現状 Phase A 共有運用
    try:
        res = (
            sb.table("dev_lessons")
            .select("id,title,tags,severity,created_at")
            .contains("tags", [skill_name])
            .limit(20)
            .execute()
        )
        rows = res.data or []
        result["dev_lessons_hits"] = len(rows)
        for r in rows:
            result["evidence"].append({
                "source": "dev_lessons",
                "id": r.get("id"),
                "title": r.get("title"),
            })
    except Exception as exc:
        sys.stderr.write(f"[skill_review] dev_lessons search failed: {exc}\n")

    # pc_handshake topic LIKE skill_name
    try:
        res2 = (
            sb.table("pc_handshake")
            .select("id,topic,created_at,context_data")
            .eq("clinic_id", CLINIC_ID)
            .like("topic", f"%{skill_name}%")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        rows = res2.data or []
        # skill_candidate handshake 自体は除外
        non_proposal = [
            r for r in rows
            if (r.get("context_data") or {}).get("shogun_kind") != "skill_candidate"
        ]
        result["handshake_hits"] = len(non_proposal)
        for r in non_proposal:
            result["evidence"].append({
                "source": "pc_handshake",
                "id": r.get("id"),
                "topic": (r.get("topic") or "")[:80],
            })
    except Exception as exc:
        sys.stderr.write(f"[skill_review] pc_handshake search failed: {exc}\n")

    if result["dev_lessons_hits"] + result["handshake_hits"] >= 2:
        result["pattern_repeated_2_plus"] = True
    return result


def _send_review_result(sb, original: dict, decision: str, pattern_check: dict) -> tuple[str, str | None]:
    """山ちゃん→副医院長に review 結果を INSERT。

    戻り値: ("ok", id) / ("conflict", None) / ("error", None)
    Codex audit B-3-3 Loop 2 #4 修正: conflict と非 conflict 失敗を呼び出し側で区別可能に。
    """
    skill = (original.get("context_data") or {}).get("skill_candidate") or {}
    skill_name = skill.get("name", "?")
    yama_pc = os.environ.get("HAKUDOKAI_YAMA_PC", "fukuincho")
    if decision == "graduate":
        topic = f"[skill_review ✅ graduate] {skill_name}"
        priority = "normal"
        requires_response = True
        msg_type = "answer"
    elif decision == "hold":
        topic = f"[skill_review 🟡 hold] {skill_name}"
        priority = "low"
        requires_response = False
        msg_type = "answer"
    elif decision == "reject":
        topic = f"[skill_review 🔴 reject] {skill_name}"
        priority = "low"
        requires_response = False
        msg_type = "answer"
    else:
        raise SystemExit(f"[skill_review] invalid decision '{decision}'")

    now = datetime.now(timezone.utc)
    idem = f"skill-review-{decision}-{skill_name}-{int(now.timestamp() // 3600)}"
    payload = {
        "from_pc": yama_pc,
        "to_pc": "fukuincho",
        "priority": priority,
        "topic": topic,
        "content": (
            f"skill_review 結果: {decision}\n"
            f"target skill: {skill_name}\n"
            f"original handshake: {original.get('id')}\n"
            f"pattern_repeated_2_plus (auto): {pattern_check['pattern_repeated_2_plus']}\n"
            f"dev_lessons hits: {pattern_check['dev_lessons_hits']}\n"
            f"handshake hits: {pattern_check['handshake_hits']}\n"
        ),
        "message_type": msg_type,
        "requires_response": requires_response,
        "clinic_id": CLINIC_ID,
        "context_data": {
            "shogun_kind": "skill_candidate",
            "review_decision": decision,
            "review_by_role": "yama",
            "original_handshake_id": original.get("id"),
            "skill_name": skill_name,
            "pattern_check": pattern_check,
            "idempotency_key": idem,
        },
    }
    # Codex audit B-3-3 #4 修正 (Loop 3 strict): conflict と他失敗を区別する
    # 戻り値: (status, id_or_none) — status は "ok" / "conflict" / "error"
    try:
        res = sb.table("pc_handshake").insert(payload).execute()
        return ("ok", res.data[0]["id"] if res.data else None)
    except Exception as exc:
        msg = str(exc)
        if "duplicate key" in msg or "23505" in msg or "idempotency" in msg.lower():
            sys.stderr.write(
                f"[skill_review] idempotency conflict (1h bucket 内重複)、INSERT skip\n"
            )
            return ("conflict", None)
        sys.stderr.write(f"[skill_review] INSERT failed: {exc}\n")
        return ("error", None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai skill_candidate review (山ちゃん graduation 評価)")
    parser.add_argument("--list", action="store_true",
                        help="pending skill_candidate を一覧表示")
    parser.add_argument("--review", help="評価対象の handshake id")
    parser.add_argument(
        "--decision", choices=("graduate", "hold", "reject"),
        help="評価結果。指定しない場合 placeholder 評価のみ (副医院長 INSERT 無し)",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="評価出力のみ、副医院長 INSERT skip")
    args = parser.parse_args(argv)

    sb = _supabase_client()

    if args.list:
        items = _list_pending(sb)
        sys.stdout.write(f"[skill_review] pending {len(items)} skill_candidate\n")
        for h in items:
            ctx = h.get("context_data") or {}
            skill = ctx.get("skill_candidate", {})
            criteria_true = sum(1 for v in (skill.get("criteria") or {}).values() if v)
            sys.stdout.write(
                f"  #{h['id'][:8]} {h.get('from_pc','-')} :: {skill.get('name','?')} "
                f"(criteria={criteria_true}/4)\n"
            )
        return 0

    if not args.review:
        parser.print_help()
        return 1

    h = _fetch_handshake(sb, args.review)
    if not h:
        sys.stderr.write(f"[skill_review] handshake {args.review} not found\n")
        return 3

    skill = (h.get("context_data") or {}).get("skill_candidate") or {}
    skill_name = skill.get("name", "?")
    sys.stdout.write(
        f"[skill_review] target #{args.review[:8]} :: {skill_name}\n"
    )
    pattern_check = _pattern_repeated_check(sb, skill_name)
    sys.stdout.write(
        f"  pattern_repeated_2_plus (auto): {pattern_check['pattern_repeated_2_plus']} "
        f"(dev_lessons={pattern_check['dev_lessons_hits']}, handshake={pattern_check['handshake_hits']})\n"
    )
    for ev in pattern_check["evidence"][:5]:
        sys.stdout.write(f"    evidence: {ev}\n")

    if not args.decision:
        sys.stdout.write(
            "[skill_review] placeholder 評価のみ実行。--decision graduate/hold/reject で副医院長 INSERT。\n"
        )
        return 0

    if args.dry_run:
        sys.stdout.write(
            f"[skill_review] (dry-run) decision={args.decision}, INSERT skip\n"
        )
        return 0

    status, rid = _send_review_result(sb, h, args.decision, pattern_check)
    if status == "ok":
        sys.stdout.write(
            f"[skill_review] decision={args.decision} review handshake INSERT ok id={rid}\n"
        )
        return 0
    if status == "conflict":
        sys.stdout.write(
            f"[skill_review] decision={args.decision} idempotency conflict, INSERT skip (exit 0)\n"
        )
        return 0
    # status == "error"
    sys.stdout.write(
        f"[skill_review] decision={args.decision} INSERT FAILED (non-conflict error), exit 4\n"
    )
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
