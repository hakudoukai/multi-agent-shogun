#!/usr/bin/env python3
"""
hakudokai_dashboard_sync.py — 博道会 dashboard.md 自動更新 (Phase B-2 task 2)

Supabase pc_handshake から最新 status を取得し、~/.openclaw/dashboard.md を再生成する。
クロちゃん 1次集約 + 山ちゃん 2次集約 の手動更新を補完するため、定期実行で
最新の稼働状況・進行中 cmd・要対応事項を反映する。

cron 設定例 (setup-departure.md task 2 参照):
  */5 * * * * cd /path/to/hakudokai-shogun && \\
    HAKUDOKAI_ROLE=kuro python3 scripts/hakudokai_dashboard_sync.py

Usage:
  hakudokai_dashboard_sync.py [--out PATH] [--dry-run] [--lookback-min N]

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[dashboard_sync] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

# Phase R1 PII detector を再利用 (Codex audit B-2-3 #2 修正)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from hakudokai_pii_detector import scan_for_pii  # type: ignore
except ImportError:
    scan_for_pii = None  # type: ignore


VALID_ROLES = ("fukuincho", "yama", "kuro", "sakura", "kouchan")
CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _redact_if_pii(text: str) -> str:
    """direct INSERT 系で混入した PII を表示前に redact (Codex audit B-2-3 #2)。

    PII detector は matched_excerpt に元文字列を含めない設計 (PIIMatch.matched_excerpt
    は `<REDACTED, len=N>` placeholder)。よって正確な find-replace は不可能のため、
    検出時は text 全体を marker 文字列で置換する保守的方針を採る。
    """
    if not text or scan_for_pii is None:
        return text
    try:
        matches = list(scan_for_pii(text))
    except Exception:
        return text
    if not matches:
        return text
    cats = sorted({getattr(m, "category", "?") for m in matches})
    return f"[REDACTED: PII detected ({len(matches)} match in {cats})]"


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[dashboard_sync] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _fetch_in_progress(sb, lookback_min: int) -> list[dict]:
    """進行中 = unack で heartbeat 以外 (Codex audit B-2-3 #1 strict 修正、Loop 3)。

    DB 側で heartbeat topic を除外することで limit 内に cmd/task/report が確保される。
    heartbeat sender は topic を `heartbeat <role>` 固定で送るため、
    `not.like.heartbeat %` でフィルタ可能。
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=lookback_min)).strftime("%Y-%m-%dT%H:%M:%SZ")
    res = (
        sb.table("pc_handshake")
        .select("id,from_pc,to_pc,priority,topic,context_data,created_at")
        .eq("clinic_id", CLINIC_ID)
        .is_("acknowledged_at", "null")
        .gte("created_at", cutoff)
        .not_.like("topic", "heartbeat %")
        .order("created_at", desc=True)
        .limit(20)
        .execute()
    )
    items = res.data or []
    # 二重防御: 万一 topic に heartbeat 文字列が含まれない heartbeat record があっても context_data 側で除外
    filtered = [
        h for h in items
        if (h.get("context_data") or {}).get("shogun_kind") != "heartbeat"
    ]
    return filtered


def _fetch_recent_completed(sb, lookback_min: int) -> list[dict]:
    """完了 = ack 済 (acknowledged_at IS NOT NULL) で lookback 内、heartbeat 除外。"""
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=lookback_min)).strftime("%Y-%m-%dT%H:%M:%SZ")
    res = (
        sb.table("pc_handshake")
        .select("id,from_pc,to_pc,topic,acknowledged_at,context_data")
        .eq("clinic_id", CLINIC_ID)
        .not_.is_("acknowledged_at", "null")
        .gte("acknowledged_at", cutoff)
        .not_.like("topic", "heartbeat %")
        .order("acknowledged_at", desc=True)
        .limit(20)
        .execute()
    )
    items = res.data or []
    return [
        h for h in items
        if (h.get("context_data") or {}).get("shogun_kind") != "heartbeat"
    ]


def _fetch_skill_candidates(sb, lookback_min: int) -> list[dict]:
    """Phase B-3 task 4: 🚀 skill候補 (In Review) section 用データ取得。

    skill_candidate handshake で unack のものを上位表示。
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=lookback_min)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        res = (
            sb.table("pc_handshake")
            .select("id,from_pc,topic,context_data,created_at")
            .eq("clinic_id", CLINIC_ID)
            .is_("acknowledged_at", "null")
            .gte("created_at", cutoff)
            .like("topic", "[skill_candidate] %")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        items = res.data or []
        return [
            h for h in items
            if (h.get("context_data") or {}).get("shogun_kind") == "skill_candidate"
        ]
    except Exception as exc:
        sys.stderr.write(f"[dashboard_sync] skill_candidate fetch failed: {exc}\n")
        return []


def _fetch_graduated_skills(sb) -> list[dict]:
    """Phase B-3 task 4: 📚 graduated skills section 用データ取得。

    project_documents の doc_type=instruction で title LIKE 'skill:%' を抽出。
    instruction-forge 命名規約 (skill: <name>) 準拠。
    """
    try:
        res = (
            sb.table("project_documents")
            .select("id,title,version,is_current,created_at")
            .eq("doc_type", "instruction")
            .eq("is_current", True)
            .like("title", "skill:%")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return res.data or []
    except Exception as exc:
        sys.stderr.write(f"[dashboard_sync] graduated_skills fetch failed: {exc}\n")
        return []


def _fetch_disable_flags() -> dict[str, bool]:
    home = os.path.expanduser("~")
    flags = {
        "global": os.path.isfile(os.path.join(home, ".openclaw", "global_disable")),
    }
    for role in VALID_ROLES:
        flags[role] = os.path.isfile(
            os.path.join(home, ".openclaw", f"disable_auto_continue_{role}")
        )
    return flags


def _fetch_idle_status(sb) -> dict[str, str]:
    """直近 heartbeat / unack handshake を見て各 role の稼働を判定。

    heartbeat shogun_kind が pc_handshake にあれば直近 5min を idle 判定の根拠に使う。
    無ければ簡易判定 (unack の有無)。
    """
    status: dict[str, str] = {role: "unknown" for role in VALID_ROLES}
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        res = (
            sb.table("pc_handshake")
            .select("from_pc,context_data,created_at")
            .eq("clinic_id", CLINIC_ID)
            .gte("created_at", cutoff)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        for row in res.data or []:
            ctx = row.get("context_data") or {}
            if ctx.get("shogun_kind") == "heartbeat":
                role = ctx.get("role") or row.get("from_pc")
                if role in status:
                    status[role] = "alive"
    except Exception as exc:
        sys.stderr.write(f"[dashboard_sync] heartbeat fetch failed: {exc}\n")
    return status


def _render(in_progress: list[dict], completed: list[dict],
            disable_flags: dict[str, bool], idle: dict[str, str],
            skill_candidates: list[dict], graduated_skills: list[dict]) -> str:
    now = datetime.now(timezone.utc).astimezone()
    lines = []
    lines.append("# 博道会 4AI 自動連動 Dashboard (auto-sync)")
    lines.append("")
    lines.append(f"> 自動生成: hakudokai_dashboard_sync.py / {now.strftime('%Y-%m-%d %H:%M:%S %z')}")
    lines.append("> 手動編集禁止 (次回 sync で上書き)。手動更新は dashboard_template.md 参照。")
    lines.append("> Reference: shogun upstream (yohey-w v4.6.0, MIT) dashboard.md")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 進行中
    lines.append("## 🔄 進行中 (In Progress, unack)")
    lines.append("")
    if not in_progress:
        lines.append("- (空) — 現在進行中の cmd なし")
    else:
        for h in in_progress[:10]:
            ctx = h.get("context_data") or {}
            kind = ctx.get("shogun_kind", "-")
            topic = _redact_if_pii((h.get("topic") or ""))[:80]
            lines.append(
                f"- `#{h['id'][:8]}` [{h.get('priority','-')}] "
                f"{h.get('from_pc','-')}->{h.get('to_pc','-')} kind={kind} :: "
                f"{topic}"
            )
    lines.append("")

    # 完了
    lines.append("## ✅ 完了 (Completed, ack 済) — 直近")
    lines.append("")
    if not completed:
        lines.append("- (空)")
    else:
        for h in completed[:10]:
            topic = _redact_if_pii((h.get("topic") or ""))[:80]
            lines.append(
                f"- `#{h['id'][:8]}` {h.get('from_pc','-')}->{h.get('to_pc','-')} :: "
                f"{topic}"
            )
    lines.append("")

    # Phase B-3 task 4: skill_candidate (In Review)
    # Codex audit B-3-3 #2 修正: skill_candidate.name にも _redact_if_pii 適用
    lines.append("## 🚀 skill候補 (skill_candidate, In Review)")
    lines.append("")
    if not skill_candidates:
        lines.append("- (空) — 現在 review 待ち skill_candidate なし")
    else:
        for h in skill_candidates[:10]:
            ctx = h.get("context_data") or {}
            skill = ctx.get("skill_candidate", {})
            criteria = skill.get("criteria", {})
            criteria_true = sum(1 for v in criteria.values() if v)
            name = _redact_if_pii(skill.get("name", "?"))[:80]
            lines.append(
                f"- `#{h['id'][:8]}` proposer={h.get('from_pc','-')} :: {name} "
                f"(criteria={criteria_true}/4)"
            )
    lines.append("")

    # Phase B-3 task 4: graduated skills
    # Codex audit B-3-3 #2 修正: title にも _redact_if_pii 適用
    lines.append("## 📚 graduated skills (instruction 化済)")
    lines.append("")
    if not graduated_skills:
        lines.append("- (空) — 現在 graduated skill なし")
    else:
        for s in graduated_skills[:10]:
            title = _redact_if_pii(s.get("title") or "")[:80]
            v = s.get("version", "-")
            ts = (s.get("created_at") or "")[:10]
            lines.append(f"- {title} (version={v}, graduated_at={ts})")
    lines.append("")

    # 稼働状況
    lines.append("## 📊 稼働状況")
    lines.append("")
    for role in VALID_ROLES:
        s = idle.get(role, "unknown")
        sign = "🟢" if s == "alive" else "⚪"
        lines.append(f"- {sign} {role}: {s}")
    lines.append("")

    # disable flags
    lines.append("## 🛡 緊急停止 状態")
    lines.append("")
    g = disable_flags.get("global", False)
    lines.append(f"- ~/.openclaw/global_disable: {'✅' if g else '❌'}")
    for role in VALID_ROLES:
        lines.append(
            f"- ~/.openclaw/disable_auto_continue_{role}: "
            f"{'✅' if disable_flags.get(role, False) else '❌'}"
        )
    lines.append("")
    if g or any(disable_flags.get(r, False) for r in VALID_ROLES):
        lines.append("(いずれか ✅ = 該当 role 停止)")
    else:
        lines.append("(全 ❌ = 全自動連動 有効)")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## License / Attribution")
    lines.append("")
    lines.append("shogun upstream (yohey-w/multi-agent-shogun v4.6.0, MIT) dashboard.md ベース、博道会語彙化 + 自動 sync。")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai dashboard.md auto-sync")
    parser.add_argument(
        "--out",
        default=os.path.expanduser("~/.openclaw/dashboard.md"),
        help="output path (default: ~/.openclaw/dashboard.md)",
    )
    parser.add_argument(
        "--lookback-min", type=int, default=240,
        help="completed lookback window in minutes (default: 240=4h)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print to stdout, no write")
    args = parser.parse_args(argv)

    sb = _supabase_client()
    in_progress = _fetch_in_progress(sb, args.lookback_min)
    completed = _fetch_recent_completed(sb, args.lookback_min)
    disable_flags = _fetch_disable_flags()
    idle = _fetch_idle_status(sb)
    skill_candidates = _fetch_skill_candidates(sb, args.lookback_min)
    graduated_skills = _fetch_graduated_skills(sb)

    rendered = _render(
        in_progress, completed, disable_flags, idle,
        skill_candidates, graduated_skills,
    )
    if args.dry_run:
        sys.stdout.write(rendered)
        return 0

    out_path = args.out
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        fh.write(rendered)
    os.replace(tmp_path, out_path)
    sys.stderr.write(
        f"[dashboard_sync] wrote {out_path} "
        f"(in_progress={len(in_progress)} completed={len(completed)})\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
