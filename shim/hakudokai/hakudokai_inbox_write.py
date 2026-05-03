#!/usr/bin/env python3
"""
hakudokai_inbox_write.py — Supabase pc_handshake INSERT wrapper.

shogun (yohey-w/multi-agent-shogun v4.6.0、MIT) の scripts/inbox_write.sh の
Supabase 化版。両 PC (main_pc / second_pc) 間で pc_handshake をメッセージ
キューとして使用し、role 間で task_assignment / report / skill_candidate /
dashboard_snapshot 等を授受する。

Usage:
    hakudokai_inbox_write.py <to_role> <content> [--type TYPE] [--from FROM]
                              [--priority PRI] [--cmd-id ID] [--idempotency-key KEY]
                              [--shogun-kind KIND]

Roles (-> pc_handshake.to_pc 対応):
    fukuincho  -> fukuincho      (副院長 main_pc Claude.ai)
    kuro       -> second_pc      (クロちゃん second_pc Claude.ai)
    yama       -> fukuincho      (山ちゃん system prompt 経由、暫定 fukuincho 同居)
    sakura     -> second_pc      (さくら second_pc Claude Code)
    kouchan    -> main_pc        (こうちゃん main_pc Claude Code)
    broadcast  -> broadcast

Types (pc_handshake.message_type 内で互換):
    task_assignment / report / status_update / question / answer
    request_permission / grant_permission / urgent_stop

Required env:
    SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY)

Reference: shogun upstream commit 20af6b53, scripts/inbox_write.sh
License: MIT (this file is博道会 minimal patch、shogun 原作者クレジット保持)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from typing import Any

try:
    from supabase import create_client  # supabase-py v2
except ImportError:
    sys.stderr.write(
        "[hakudokai_inbox_write] supabase-py not installed. "
        "Run: pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

# Phase R1: PII detector (アプリ層 二重防御 #1) を同 dir から import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from hakudokai_pii_detector import (  # noqa: E402
        PIIDetected, scan_for_pii, explain_matches,
    )
except ImportError as _pii_imp_err:
    sys.stderr.write(
        f"[hakudokai_inbox_write] FATAL: hakudokai_pii_detector.py missing: {_pii_imp_err}\n"
    )
    sys.exit(3)


def _build_role_to_pc() -> dict:
    """Phase B-1: yama 独立化対応 (PHASE_B_ROADMAP §1 task 4)。

    Phase A 同居運用: yama → fukuincho (default)。
    Phase B 独立スレ運用: HAKUDOKAI_YAMA_PC env で別 PC 識別子に切替可能。
    後方互換のため未設定時は Phase A 挙動。
    """
    yama_pc = os.environ.get("HAKUDOKAI_YAMA_PC", "fukuincho")
    return {
        "fukuincho": "fukuincho",
        "yama": yama_pc,           # Phase A: fukuincho 同居 / Phase B: env で独立 PC へ
        "kuro": "second_pc",
        "sakura": "second_pc",
        "kouchan": "main_pc",
        "broadcast": "broadcast",
    }


ROLE_TO_PC = _build_role_to_pc()

VALID_KINDS = {
    "cmd_assignment",
    "task_assignment",
    "report",
    "skill_candidate",
    "dashboard_snapshot",
    "ack",
    "escalation",
}

VALID_PRIORITIES = {"low", "normal", "high", "urgent"}


def _resolve_to_pc(role: str) -> str:
    role = role.lower()
    if role not in ROLE_TO_PC:
        raise SystemExit(
            f"[hakudokai_inbox_write] unknown role '{role}'. "
            f"valid: {sorted(ROLE_TO_PC)}"
        )
    return ROLE_TO_PC[role]


def _resolve_from_pc(from_role: str | None) -> str:
    if from_role:
        return _resolve_to_pc(from_role)
    role_file = os.path.expanduser("~/.openclaw/role.json")
    if os.path.isfile(role_file):
        with open(role_file, encoding="utf-8") as fh:
            cfg = json.load(fh)
        role = cfg.get("role")
        if role:
            return _resolve_to_pc(role)
    raise SystemExit(
        "[hakudokai_inbox_write] cannot resolve from_pc. "
        "Pass --from <role> or create ~/.openclaw/role.json with {\"role\": \"...\"}."
    )


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[hakudokai_inbox_write] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _build_payload(args: argparse.Namespace) -> dict[str, Any]:
    to_pc = _resolve_to_pc(args.to_role)
    from_pc = _resolve_from_pc(args.from_role)
    # Codex audit fix #2: 自送防止は role 粒度で判定 (PC 粒度では yama=fukuincho 同居設計が破綻するため)
    from_role_norm = (args.from_role or os.environ.get("HAKUDOKAI_ROLE", "")).lower().strip()
    to_role_norm = args.to_role.lower().strip()
    if from_role_norm and from_role_norm == to_role_norm and to_role_norm != "broadcast":
        raise SystemExit(
            f"[hakudokai_inbox_write] self-send rejected at role level: "
            f"from_role={from_role_norm} to_role={to_role_norm}"
        )

    if args.shogun_kind and args.shogun_kind not in VALID_KINDS:
        raise SystemExit(
            f"[hakudokai_inbox_write] invalid shogun_kind '{args.shogun_kind}'. "
            f"valid: {sorted(VALID_KINDS)}"
        )
    priority = args.priority or "normal"
    if priority not in VALID_PRIORITIES:
        raise SystemExit(
            f"[hakudokai_inbox_write] invalid priority '{priority}'. "
            f"valid: {sorted(VALID_PRIORITIES)}"
        )

    context: dict[str, Any] = {
        "shogun_kind": args.shogun_kind or "task_assignment",
        "idempotency_key": args.idempotency_key or str(uuid.uuid4()),
        "from_role": args.from_role or os.environ.get("HAKUDOKAI_ROLE", ""),
        "to_role": args.to_role,
    }
    if args.cmd_id:
        context["cmd_id"] = args.cmd_id

    extra_obj: dict[str, Any] | None = None
    if args.extra_json:
        extra_obj = json.loads(args.extra_json)
        context["extra"] = extra_obj

    requires_response = args.requires_response
    if requires_response is None:
        requires_response = (args.type == "question")

    # Phase R2: clinic_id 自動付与 (multi-tenant 対応、env > role.json > default)
    clinic_id = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")
    return {
        "from_pc": from_pc,
        "to_pc": to_pc,
        "message_type": args.type,
        "priority": priority,
        "topic": args.topic or args.content[:160],
        "content": args.content,
        "context_data": context,
        "requires_response": requires_response,
        "clinic_id": clinic_id,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai inbox write (Supabase pc_handshake).")
    parser.add_argument("to_role", help="target role: fukuincho / kuro / yama / sakura / kouchan / broadcast")
    parser.add_argument("content", help="message body (text)")
    parser.add_argument("--type", default="status_update",
                        help="message_type: task_assignment / report / status_update / question / "
                             "answer / request_permission / grant_permission / urgent_stop")
    parser.add_argument("--from", dest="from_role",
                        help="sender role (default: ~/.openclaw/role.json or HAKUDOKAI_ROLE)")
    parser.add_argument("--priority", choices=sorted(VALID_PRIORITIES), default=None)
    parser.add_argument("--topic", help="explicit topic (default: content first 160 chars)")
    parser.add_argument("--cmd-id", help="optional cmd id for chain tracking")
    parser.add_argument("--idempotency-key", help="dedup key (default: random uuid4)")
    parser.add_argument("--shogun-kind", choices=sorted(VALID_KINDS),
                        help="logical kind (default: task_assignment)")
    parser.add_argument("--extra-json", help="extra json merged into context_data.extra")
    parser.add_argument("--requires-response", type=lambda v: v.lower() in ("1", "true", "yes"),
                        default=None, help="override requires_response (default: True for question)")
    parser.add_argument("--dry-run", action="store_true", help="print payload only, no INSERT")
    parser.add_argument("--skip-pii-check", action="store_true",
                        help="(emergency only) bypass PII detection. Phase R1 root-cause guard。"
                             "通常使用禁止、緊急時の rescue 用途のみ。")
    args = parser.parse_args(argv)

    payload = _build_payload(args)

    if args.dry_run:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2, default=str)
        sys.stdout.write("\n")
        return 0

    sb = _supabase_client()

    # Phase R1 (FKI-ROOT-CAUSE-FIRST-01): PII 検出 (アプリ層 二重防御 #1)
    # content + context_data 全 string field を scan、検出時は INSERT 拒否 + dev_lessons INSERT
    if not args.skip_pii_check:
        scan_targets: list[tuple[str, str]] = [
            ("content", payload.get("content", "")),
            ("topic", payload.get("topic", "")),
            ("context_data_json", json.dumps(payload.get("context_data", {}), ensure_ascii=False)),
        ]
        all_matches = []
        for label, txt in scan_targets:
            for m in scan_for_pii(txt):
                all_matches.append((label, m))
        if all_matches:
            summary = {
                "total": len(all_matches),
                "by_field": {},
                "by_category": {},
            }
            for label, m in all_matches:
                summary["by_field"].setdefault(label, 0)
                summary["by_field"][label] += 1
                summary["by_category"].setdefault(m.category, 0)
                summary["by_category"][m.category] += 1
            sys.stderr.write(
                f"[hakudokai_inbox_write] PII detected, INSERT aborted. "
                f"summary={json.dumps(summary, ensure_ascii=False)}\n"
            )
            # dev_lessons へ自動 INSERT (severity=high、再発防止 feedback loop)
            try:
                sb.table("dev_lessons").insert({
                    "session_date": __import__("datetime").datetime.utcnow().date().isoformat(),
                    "thread_title": "hakudokai_inbox_write PII guard activated",
                    "lesson_type": "security_guard",
                    "title": "PII detected in pc_handshake INSERT attempt — aborted by Phase R1 layer",
                    "wrong_approach": (
                        f"caller from_role={payload.get('context_data', {}).get('from_role')} "
                        f"attempted to INSERT pc_handshake with PII in fields {sorted(summary['by_field'])}"
                    ),
                    "root_cause": "PII (患者個人情報) を pc_handshake.context_data / content 経由で送信する設計上の脆弱性。Phase R1 で技術的予防策を導入。",
                    "correct_fix": "PII を含むメッセージは送信しない。患者情報は SQLite ローカル経由で取扱い、pc_handshake は ops/clinical_meta のみ。",
                    "prevention": "Phase R1 PII detector + RLS trigger 二重防御。検出時は INSERT 拒否で運用継続。",
                    "philosophy_ref": "DD-061 v2.4 §16 + FKI-ROOT-CAUSE-FIRST-01 (2026-04-30)",
                    "severity": "high",
                    "tags": ["pii-guard", "phase-r1", "security", "auto-detected"],
                }).execute()
            except Exception as audit_exc:
                sys.stderr.write(f"[hakudokai_inbox_write] dev_lessons INSERT failed (non-fatal): {audit_exc}\n")
            return 5  # exit code 5 = PII detected

    # Codex audit fix #1: idempotency_key DB UNIQUE partial index (apply済) で重複INSERTは
    # 23505 unique_violation を返す。caller には dedup OK を示す exit 0 + dedup フラグ付き
    # の応答を返し、重複再実行で副作用が出ないようにする。
    try:
        res = sb.table("pc_handshake").insert(payload).execute()
    except Exception as exc:
        msg = str(exc)
        if "duplicate key" in msg or "unique" in msg.lower() or "23505" in msg:
            # 既存 row を取得して結果として返す (idempotent)
            idem = payload["context_data"].get("idempotency_key")
            existing = sb.table("pc_handshake").select(
                "id,to_pc,topic"
            ).eq("context_data->>idempotency_key", idem).limit(1).execute()
            if existing.data:
                row = existing.data[0]
                sys.stdout.write(json.dumps(
                    {"id": row.get("id"), "to_pc": row.get("to_pc"),
                     "topic": (row.get("topic") or "")[:80],
                     "shogun_kind": payload["context_data"].get("shogun_kind"),
                     "dedup": True},
                    ensure_ascii=False))
                sys.stdout.write("\n")
                return 0
        sys.stderr.write(f"[hakudokai_inbox_write] INSERT error: {exc}\n")
        return 1

    inserted = res.data[0] if res.data else None
    if inserted is None:
        sys.stderr.write(f"[hakudokai_inbox_write] INSERT failed: {res}\n")
        return 1
    sys.stdout.write(json.dumps(
        {"id": inserted.get("id"), "to_pc": inserted.get("to_pc"),
         "topic": inserted.get("topic")[:80] if inserted.get("topic") else None,
         "shogun_kind": payload["context_data"].get("shogun_kind"),
         "dedup": False},
        ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
