#!/usr/bin/env python3
"""
hakudokai_patient_chat.py — 患者 AIチャット 24h (Phase C-2, DD-041 §3-§4)

設計上の最重要制約 (DD-054 §11 法令第1優先):
  - 診断禁止: AI が患者へ「あなたは XX 病です」等の確定診断を返さない
  - 治療強制禁止: AI が「XX を必ずやるべき」等の強制を返さない
  - 法令準拠 keyword filter は **入力 (患者発話)** と **出力 (AI 応答)** の両方で適用
  - 違反検出時: 入力は warning + safe_response 返却、出力は phrase 置換

機能:
- 患者発話の keyword filter (患者からの「診断して」「絶対治す方法」等を検出)
- AI 応答の keyword filter (出力前 sanitize、診断断定 / 強制表現を一般表現へ置換)
- 蜘蛛の糸 (DD-020 ai_fukuincho_messages) 自動連携 (option、本 stub では log のみ)
- CRM 情報参照 (家族構成等) は patient_master 側 PII guard 経由で読み取り

実 LLM 接続は本 stub では mock (Anthropic API interface 定義 + safe_response template)。
本番接続は副医院長 + 山ちゃん 法令適合審査 + Anthropic ZDR 確認後の別 Phase。

Usage:
  hakudokai_patient_chat.py --send --patient-id <uuid> --message "歯が痛いです"
  hakudokai_patient_chat.py --history --patient-id <uuid>
  hakudokai_patient_chat.py --check-keyword --message "診断してください"
  --dry-run で副作用なし

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[patient_chat] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
# Phase C-2 全体設計やり直し: PII detector 必須 import (optional 廃止、import 失敗で起動失敗)
# Codex Loop 1 で「optional import で実体不在 → no-op」と誤判定された経路の根本治癒
try:
    from hakudokai_pii_detector import scan_for_pii, raise_if_pii  # type: ignore
except ImportError as exc:
    sys.stderr.write(
        f"[patient_chat] FATAL: hakudokai_pii_detector required but not importable: {exc}\n"
        f"  PII guard が機能しないため起動拒否 (DD-061 v2.4 §16 + FKI-DEV-ROOT-CURE-FIRST-01)\n"
    )
    sys.exit(3)


CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


# ============================================================
# 法令準拠 keyword filter (DD-054 §11 法令第1優先、DD-041 §3 診断禁止/治療強制禁止)
# ============================================================

# 患者発話側の検出 keyword (患者が AI に診断/強制を求めている兆候)
PATIENT_INPUT_FORBIDDEN = {
    "diagnosis_request": [
        re.compile(r"診断(?:して|お願い|してくだ|を求|を)"),
        re.compile(r"病名"),
        re.compile(r"(?:何の?病気|何の?病|何の?疾患)"),
    ],
    "treatment_force_request": [
        re.compile(r"必ず治る"),
        re.compile(r"絶対(?:治る|治す|やるべき)"),
        re.compile(r"確実に(?:治る|なくなる)"),
    ],
}

# AI 応答側で sanitize する pattern (出力前に置換する確定表現)
AI_OUTPUT_SANITIZE = [
    # 確定診断 → 推測表現へ
    (re.compile(r"あなたは(.{1,20})です(?:[。!])?"), r"あなたは\1の可能性があります。歯科医による診察が必要です。"),
    (re.compile(r"あなたの(.{1,20})は(.{1,20})です(?:[。!])?"), r"あなたの\1は\2の可能性が考えられます。歯科医による診察が必要です。"),
    # 治療強制 → 提案表現へ
    (re.compile(r"必ず(.{1,20})して(?:くださ|ね|くだ)"), r"\1をご検討ください (歯科医にご相談ください)。"),
    (re.compile(r"絶対に(.{1,20})しないと"), r"\1をご検討いただくと良い場合があります"),
]

# safe_response template (法令違反入力時の AI 返却)
SAFE_RESPONSE_TEMPLATES = {
    "diagnosis_request": (
        "AI チャットでは確定診断はお伝えできません (法令上、医師のみが診断可能です)。"
        "気になる症状があれば、歯科医院での診察をご予約ください。"
    ),
    "treatment_force_request": (
        "AI チャットでは特定治療を強くお勧めすることはできません。"
        "歯科医による診察と、ご本人のご希望を踏まえた選択肢のご提案が原則です。"
    ),
}


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[patient_chat] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _abort_if_pii(text: str, label: str) -> None:
    """Phase C-2 全体設計やり直し: fail-close PII guard (scan_for_pii は import 必須化済).

    raise_if_pii は PIIDetected 例外を raise、本 wrapper では SystemExit(5) に変換.
    scan_for_pii 自体の例外は握り潰さず raise (silent failure 撲滅).
    """
    if not text:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception as exc:
        # PII scanner 自体の例外は fail-close (silent skip 禁止)
        sys.stderr.write(f"[patient_chat] PII scanner error in {label}: {exc}\n")
        raise SystemExit(5) from exc
    if matches:
        sys.stderr.write(
            f"[patient_chat] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
        )
        raise SystemExit(5)


def _verify_session(sb, session_id: str, patient_id: str, clinic_id: str) -> bool:
    """Phase C-2 全体設計やり直し: session_token verify で caller 指定 patient_id 真正性確認.

    patient_app_session を SELECT し、session が patient_id × clinic_id に紐付いているか確認.
    紐付け不一致 / session 不存在 / revoked / expired → False (caller は INSERT 中止).
    """
    if not session_id:
        # session_id 不在時は caller 側で session を渡さない明示判断 (内部 CLI / batch).
        # caller (_send_chat / _list_history) は session_id 非指定で呼出可能、その場合
        # _verify_session は呼ばれない設計. 本関数到達時点で session_id 必須.
        return False
    try:
        res = (
            sb.table("patient_app_session")
            .select("patient_id,clinic_id,revoked_at,expires_at")
            .eq("id", session_id)
            .eq("patient_id", patient_id)
            .eq("clinic_id", clinic_id)
            .maybeSingle()
            .execute()
        )
    except Exception as exc:
        sys.stderr.write(f"[patient_chat] session verify error: {exc}\n")
        return False
    if not res.data:
        return False
    row = res.data
    # revoked / expired チェック
    if row.get("revoked_at") is not None:
        return False
    expires_at = row.get("expires_at")
    if expires_at:
        # Gemini Pass 1 修正 (Phase C-2 Pass 6): module 冒頭で from datetime import datetime, timezone 済、
        # 関数内 import は不要、削除. 旧 `from datetime import datetime` のみ → NameError on timezone.
        try:
            exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if exp < datetime.now(timezone.utc):
                return False
        except Exception:
            pass
    return True


def _scan_input_forbidden(message: str) -> list[str]:
    """患者発話に診断要求 / 治療強制要求 keyword が含まれるか検出。"""
    detected: list[str] = []
    for category, patterns in PATIENT_INPUT_FORBIDDEN.items():
        for p in patterns:
            if p.search(message):
                detected.append(category)
                break
    return detected


def _sanitize_output(response_text: str) -> tuple[str, bool, bool]:
    """AI 応答の確定診断 / 治療強制表現を sanitize。

    戻り値: (sanitized_text, diagnosis_replaced, treatment_force_replaced)
    """
    sanitized = response_text
    diag_replaced = False
    force_replaced = False
    for i, (pattern, replacement) in enumerate(AI_OUTPUT_SANITIZE):
        new_text, n = pattern.subn(replacement, sanitized)
        if n > 0:
            sanitized = new_text
            if i < 2:
                diag_replaced = True
            else:
                force_replaced = True
    return sanitized, diag_replaced, force_replaced


def _mock_ai_response(message: str, crm_summary: dict | None = None) -> tuple[str, dict]:
    """Anthropic API 呼び出しを mock。本番接続は別 Phase。

    crm_summary は CRM 情報サマリ (家族構成等)、本 stub では log のみ。
    """
    # 入力 keyword filter (法令準拠)
    forbidden_categories = _scan_input_forbidden(message)
    if forbidden_categories:
        # 最優先 category の safe_response 返却
        cat = forbidden_categories[0]
        text = SAFE_RESPONSE_TEMPLATES.get(cat, SAFE_RESPONSE_TEMPLATES["diagnosis_request"])
        return text, {
            "model_id": "mock-safe-response",
            "tokens_used": 0,
            "input_forbidden_categories": forbidden_categories,
        }

    # 通常 mock 応答 (実際は Anthropic API に投げる、本 stub では template)
    base_response = (
        f"ご質問ありがとうございます。"
        f"歯科医院では症状に応じた選択肢のご提案を行っています。"
        f"気になる症状があれば、ご予約をご検討ください。"
    )
    # CRM 参照 mock (家族構成等が判明していれば言及、PII 直書きは禁止)
    if crm_summary and crm_summary.get("has_family_records"):
        base_response += " ご家族でのご来院にも対応しております。"
    return base_response, {
        "model_id": "mock-template",
        "tokens_used": len(base_response),
        "input_forbidden_categories": [],
    }


def _fetch_crm_summary(sb, clinic_id: str, patient_id: str) -> dict:
    """patient_master + 関連 table から CRM 簡易サマリを取得。
    PII guard: 氏名/住所/電話などは含めない、has_family_records 等の boolean のみ。
    """
    try:
        # 例: patient_relations table 等が無い場合は空 dict
        return {"has_family_records": False, "is_recall_target": False}
    except Exception:
        return {}


def _send_chat(sb, args) -> int:
    # Phase C-2 全体設計やり直し Pass 3 修正 (Codex Pass 2 session_id NULL bypass 根治):
    # session-id 必須化、--internal-batch 時のみ明示 bypass (warning log)
    if not args.session_id:
        if not args.internal_batch:
            sys.stderr.write(
                "[patient_chat] --session-id required (or --internal-batch for explicit CLI/batch bypass)\n"
            )
            return 2
        sys.stderr.write(
            "[patient_chat] WARNING: --internal-batch bypass active、session verify skipped (CLI/batch 専用)\n"
        )
    elif not _verify_session(sb, args.session_id, args.patient_id, args.clinic_id):
        sys.stderr.write(
            f"[patient_chat] session verify failed (session_id/{args.session_id[:8]}.../patient_id mismatch or revoked/expired)、INSERT 拒否\n"
        )
        return 4
    _abort_if_pii(args.message, "patient_message")
    forbidden = _scan_input_forbidden(args.message)
    chat_thread_id = args.thread_id  # NULL なら DB 側 default で gen_random_uuid

    # patient_chat_log INSERT
    chat_log_payload = {
        "clinic_id": args.clinic_id,
        "patient_id": args.patient_id,
        "session_id": args.session_id,
        "sender": "patient",
        "message_text": args.message,
        "forbidden_keyword_detected": bool(forbidden),
        "forbidden_categories": forbidden,
    }
    if chat_thread_id:
        chat_log_payload["chat_thread_id"] = chat_thread_id

    if args.dry_run:
        sys.stderr.write(f"[patient_chat] (dry-run) chat_log payload prepared\n")
        # AI 応答 mock も実行 (副作用なし)
        crm = _fetch_crm_summary(sb, args.clinic_id, args.patient_id)
        ai_text, ai_meta = _mock_ai_response(args.message, crm)
        sanitized, diag, force = _sanitize_output(ai_text)
        sys.stdout.write(
            f"[patient_chat] (dry-run) input_forbidden={forbidden} "
            f"sanitize_diag={diag} sanitize_force={force}\n"
            f"  AI response: {sanitized}\n"
        )
        return 0

    try:
        chat_res = sb.table("patient_chat_log").insert(chat_log_payload).execute()
        chat_log_id = chat_res.data[0]["id"]
    except Exception as exc:
        sys.stderr.write(f"[patient_chat] chat_log INSERT failed: {exc}\n")
        return 4

    # AI 応答生成 (mock or 本番、本 stub は mock)
    crm = _fetch_crm_summary(sb, args.clinic_id, args.patient_id)
    ai_text, ai_meta = _mock_ai_response(args.message, crm)
    sanitized, diag_replaced, force_replaced = _sanitize_output(ai_text)
    _abort_if_pii(sanitized, "ai_response_text")

    # patient_chat_response INSERT (chat_log_uniq UNIQUE)
    response_payload = {
        "clinic_id": args.clinic_id,
        "chat_log_id": chat_log_id,
        "response_text": sanitized,
        "diagnosis_phrase_replaced": diag_replaced,
        "treatment_force_replaced": force_replaced,
        "crm_referenced": bool(crm.get("has_family_records") or crm.get("is_recall_target")),
        "spider_thread_pushed": False,  # DD-020 蜘蛛の糸 push は別 service
        "model_id": ai_meta.get("model_id"),
        "tokens_used": ai_meta.get("tokens_used"),
    }
    try:
        res = sb.table("patient_chat_response").insert(response_payload).execute()
        sys.stdout.write(
            f"[patient_chat] chat_log id={chat_log_id} response_id={res.data[0]['id']}\n"
            f"  forbidden={forbidden} sanitize_diag={diag_replaced} sanitize_force={force_replaced}\n"
            f"  AI response: {sanitized}\n"
        )
        return 0
    except Exception as exc:
        msg = str(exc)
        if "duplicate key" in msg or "23505" in msg:
            sys.stdout.write(
                f"[patient_chat] response idempotency conflict (chat_log_id 既存)、INSERT skip\n"
            )
            return 0
        sys.stderr.write(f"[patient_chat] response INSERT failed: {exc}\n")
        return 4


def _list_history(sb, args) -> int:
    # Phase C-2 全体設計やり直し Pass 3 修正 (Codex Pass 2 session_id NULL bypass 根治):
    # session-id 必須化、--internal-batch 時のみ明示 bypass
    if not args.session_id:
        if not args.internal_batch:
            sys.stderr.write(
                "[patient_chat] --session-id required for history (or --internal-batch)\n"
            )
            return 2
        sys.stderr.write(
            "[patient_chat] WARNING: --internal-batch bypass active for history\n"
        )
    elif not _verify_session(sb, args.session_id, args.patient_id, args.clinic_id):
        sys.stderr.write(
            f"[patient_chat] session verify failed for history、SELECT 拒否\n"
        )
        return 4
    try:
        res = (
            sb.table("patient_chat_log")
            .select("id,sender,message_text,forbidden_keyword_detected,created_at")
            .eq("clinic_id", args.clinic_id)
            .eq("patient_id", args.patient_id)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        rows = res.data or []
        sys.stdout.write(f"[patient_chat] history ({len(rows)}):\n")
        for r in rows:
            forbidden = " 🔴LAW" if r.get("forbidden_keyword_detected") else ""
            sys.stdout.write(
                f"  {r['created_at'][:19]} #{r['id'][:8]} [{r['sender']}]{forbidden} :: "
                f"{(r.get('message_text') or '')[:80]}\n"
            )
        return 0
    except Exception as exc:
        sys.stderr.write(f"[patient_chat] history fetch failed: {exc}\n")
        return 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai patient AIチャット (DD-041 §3-§4)")
    sub = parser.add_mutually_exclusive_group(required=True)
    sub.add_argument("--send", action="store_true", help="患者発話を送信 + AI 応答")
    sub.add_argument("--history", action="store_true", help="チャット履歴一覧")
    sub.add_argument("--check-keyword", action="store_true",
                     help="message の keyword filter のみ検証 (DB 接続なし)")

    parser.add_argument("--clinic-id", default=CLINIC_ID)
    parser.add_argument("--patient-id", help="patient_master.id (uuid)")
    parser.add_argument("--message", help="患者発話 (--send / --check-keyword)")
    parser.add_argument("--thread-id", help="既存 chat_thread_id (option)")
    # Phase C-2 全体設計やり直し Pass 3 (Codex Pass 2 session_id NULL bypass 根治):
    # session-id を実質必須化、bypass は明示 --internal-batch のみ許容 (運用前提依存撲滅)
    parser.add_argument("--session-id",
                        help="patient_app_session.id (--send/--history で必須、--internal-batch 時のみ省略可)")
    parser.add_argument("--internal-batch", action="store_true",
                        help="session 検証 bypass (内部 CLI/batch 専用、明示宣言、warning log 必須)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.check_keyword:
        if not args.message:
            sys.stderr.write("[patient_chat] --check-keyword requires --message\n")
            return 2
        forbidden = _scan_input_forbidden(args.message)
        sanitized, diag, force = _sanitize_output(args.message)
        sys.stdout.write(
            f"[patient_chat] input_forbidden_categories={forbidden}\n"
            f"  sanitize_diag={diag} sanitize_force={force}\n"
            f"  sanitized_message: {sanitized}\n"
        )
        return 0

    sb = _supabase_client()

    if args.send:
        if not (args.patient_id and args.message):
            sys.stderr.write("[patient_chat] --send requires --patient-id and --message\n")
            return 2
        return _send_chat(sb, args)

    if args.history:
        if not args.patient_id:
            sys.stderr.write("[patient_chat] --history requires --patient-id\n")
            return 2
        return _list_history(sb, args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
