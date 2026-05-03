#!/usr/bin/env python3
"""
hakudokai_skill_candidate.py — Skill Discovery 足軽提案 wrapper (Phase B-3 task 3)

足軽 (さくら / こうちゃん) が skill_candidate を副医院長宛に提案する際の標準 wrapper。
- pc_handshake INSERT (shogun_kind=skill_candidate, to=fukuincho, requires_response=true)
- dev_lessons 自動 INSERT (severity 自動分類)
- PII guard 適用 (Phase R1 二重防御継承)
- criteria 4 項目自己 check + severity 降格判定

Usage:
  hakudokai_skill_candidate.py \\
    --name "skill-name-kebab" \\
    --description "1-3 文の要約" \\
    --reason "criteria 4 項目を満たす根拠 verbatim" \\
    --criteria reusable=1,repeat=1,specialized=1,cross_ashigaru=1 \\
    --evidence-handshake-ids id1,id2 \\
    --evidence-dev-lesson-ids id1 \\
    [--from sakura] [--dry-run] [--skip-pii-check]

設計: docs/skill-discovery.md §1-§3 schema 準拠

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
        "[skill_candidate] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

# Phase R1 PII detector を再利用
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from hakudokai_pii_detector import scan_for_pii  # type: ignore
except ImportError:
    scan_for_pii = None  # type: ignore


VALID_PROPOSER_ROLES = ("sakura", "kouchan")
CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _resolve_proposer_role(args) -> str:
    role = args.from_role or os.environ.get("HAKUDOKAI_ROLE")
    if not role:
        role_file = os.path.expanduser("~/.openclaw/role.json")
        if os.path.isfile(role_file):
            try:
                with open(role_file, encoding="utf-8") as fh:
                    role = json.load(fh).get("role")
            except Exception:
                pass
    if not role:
        raise SystemExit("[skill_candidate] proposer role unresolved (use --from or HAKUDOKAI_ROLE)")
    role = role.lower()
    if role not in VALID_PROPOSER_ROLES:
        raise SystemExit(
            f"[skill_candidate] proposer must be in {VALID_PROPOSER_ROLES}, got '{role}'"
        )
    return role


def _resolve_from_pc(role: str) -> str:
    yama_pc = os.environ.get("HAKUDOKAI_YAMA_PC", "fukuincho")
    table = {
        "fukuincho": "fukuincho",
        "yama": yama_pc,
        "kuro": "second_pc",
        "sakura": "second_pc",
        "kouchan": "main_pc",
    }
    return table.get(role, role)


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[skill_candidate] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _parse_criteria(spec: str) -> dict:
    """e.g. 'reusable=1,repeat=1,specialized=0,cross_ashigaru=1' →
    {reusable_across_projects:..., pattern_repeated_2_plus:..., requires_specialized_knowledge:..., useful_to_other_ashigaru:...}
    """
    aliases = {
        "reusable": "reusable_across_projects",
        "repeat": "pattern_repeated_2_plus",
        "specialized": "requires_specialized_knowledge",
        "cross_ashigaru": "useful_to_other_ashigaru",
    }
    result = {v: False for v in aliases.values()}
    if not spec:
        return result
    for kv in spec.split(","):
        kv = kv.strip()
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        k = k.strip().lower()
        v = v.strip().lower()
        full = aliases.get(k, k)
        if full not in result:
            sys.stderr.write(f"[skill_candidate] WARN unknown criterion '{k}', ignored\n")
            continue
        result[full] = v in ("1", "true", "yes", "on")
    return result


def _classify_severity(criteria: dict) -> str | None:
    true_count = sum(1 for v in criteria.values() if v)
    if true_count >= 4:
        return "medium"
    if true_count == 3:
        return "low"
    return None  # 2/4 以下: dev_lessons INSERT skip


def _scan_pii(scan_targets: list[tuple[str, str]], skip: bool) -> None:
    if skip or scan_for_pii is None:
        return
    matches = []
    for label, txt in scan_targets:
        for m in scan_for_pii(txt or ""):
            matches.append((label, getattr(m, "category", "?")))
    if matches:
        sys.stderr.write(
            f"[skill_candidate] PII detected, abort INSERT (matches={len(matches)} "
            f"first={matches[0]})\n"
        )
        raise SystemExit(5)


def _build_handshake_payload(args, proposer_role: str, from_pc: str,
                             criteria: dict) -> dict:
    """Codex audit B-3-3 #3 修正: docs/skill-discovery.md §1 仕様 (4 項目すべて true で
    found=true、いずれか false なら found=false で graduation 不要、保留扱い) と一致。
    """
    now = datetime.now(timezone.utc)
    found = all(criteria.values())
    skill = {
        "found": found,
        "name": args.name,
        "description": args.description,
        "criteria": criteria,
        "reason": args.reason,
        "evidence_handshake_ids": [s for s in (args.evidence_handshake_ids or "").split(",") if s.strip()],
        "evidence_dev_lesson_ids": [s for s in (args.evidence_dev_lesson_ids or "").split(",") if s.strip()],
        "proposer_role": proposer_role,
        "proposed_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    idem = f"skill-candidate-{proposer_role}-{args.name}-{int(now.timestamp() // 3600)}"
    return {
        "from_pc": from_pc,
        "to_pc": "fukuincho",
        "priority": "normal",
        "topic": f"[skill_candidate] {args.name}",
        "content": (
            f"skill_candidate 提案: {args.name}\n"
            f"description: {args.description}\n"
            f"criteria: {criteria}\n"
            f"reason: {args.reason}"
        ),
        "message_type": "question",
        "requires_response": True,
        "clinic_id": CLINIC_ID,
        "context_data": {
            "shogun_kind": "skill_candidate",
            "skill_candidate": skill,
            "idempotency_key": idem,
        },
    }


def _build_dev_lesson_row(args, proposer_role: str, severity: str) -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "session_date": today,
        "thread_title": args.name,
        "lesson_type": "skill_candidate",
        "title": f"skill_candidate 提案: {args.name}",
        "wrong_approach": "(skill_candidate なので未該当)",
        "root_cause": args.reason,
        "correct_fix": args.description,
        "prevention": (
            "skill graduation 後 instruction-forge で skill 化、"
            "足軽 onboarding で参照必須"
        ),
        "philosophy_ref": "FKI-OSS-FIRST-01 / FKI-PRIOR-WISDOM-01",
        "severity": severity,
        "tags": ["skill_candidate", proposer_role, args.name],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai skill_candidate proposer")
    parser.add_argument("--name", required=True, help="skill 仮名 (kebab-case)")
    parser.add_argument("--description", required=True, help="1-3 文の要約")
    parser.add_argument("--reason", required=True, help="criteria 根拠 verbatim")
    parser.add_argument(
        "--criteria",
        default="reusable=0,repeat=0,specialized=0,cross_ashigaru=0",
        help="criteria 4 項目: reusable=1,repeat=1,specialized=1,cross_ashigaru=1",
    )
    parser.add_argument("--evidence-handshake-ids", default="",
                        help="comma-separated handshake ids")
    parser.add_argument("--evidence-dev-lesson-ids", default="",
                        help="comma-separated dev_lessons ids")
    parser.add_argument("--from", dest="from_role", default=None,
                        help="proposer role (default: env / role.json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="payload 計算のみ、INSERT skip")
    parser.add_argument("--skip-pii-check", action="store_true",
                        help="(emergency only) PII detector を bypass")
    args = parser.parse_args(argv)

    proposer_role = _resolve_proposer_role(args)
    from_pc = _resolve_from_pc(proposer_role)
    criteria = _parse_criteria(args.criteria)
    severity = _classify_severity(criteria)

    payload = _build_handshake_payload(args, proposer_role, from_pc, criteria)
    _scan_pii(
        [
            ("name", args.name),
            ("description", args.description),
            ("reason", args.reason),
            ("content", payload["content"]),
        ],
        args.skip_pii_check,
    )

    if args.dry_run:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2, default=str)
        sys.stdout.write("\n")
        sys.stderr.write(
            f"[skill_candidate] (dry-run) severity={severity} criteria_true="
            f"{sum(1 for v in criteria.values() if v)}/4\n"
        )
        return 0

    sb = _supabase_client()
    # Codex audit B-3-3 #4 修正: idempotency_key UNIQUE conflict (23505) を吸収
    handshake_id = None
    try:
        res = sb.table("pc_handshake").insert(payload).execute()
        handshake_id = res.data[0]["id"] if res.data else None
        sys.stderr.write(f"[skill_candidate] handshake INSERT ok id={handshake_id}\n")
    except Exception as exc:
        msg = str(exc)
        if "duplicate key" in msg or "23505" in msg or "idempotency" in msg.lower():
            sys.stderr.write(
                f"[skill_candidate] idempotency conflict (1h bucket 内重複)、INSERT skip\n"
            )
            return 0
        sys.stderr.write(f"[skill_candidate] handshake INSERT failed: {exc}\n")
        return 4

    # dev_lessons 自動 INSERT (severity が None なら skip)
    if severity:
        try:
            row = _build_dev_lesson_row(args, proposer_role, severity)
            res2 = sb.table("dev_lessons").insert(row).execute()
            dl_id = res2.data[0]["id"] if res2.data else None
            sys.stderr.write(
                f"[skill_candidate] dev_lessons INSERT ok severity={severity} id={dl_id}\n"
            )
        except Exception as exc:
            sys.stderr.write(f"[skill_candidate] dev_lessons INSERT failed: {exc}\n")
    else:
        sys.stderr.write(
            f"[skill_candidate] criteria 不足 (true=<3/4)、dev_lessons INSERT skip\n"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
