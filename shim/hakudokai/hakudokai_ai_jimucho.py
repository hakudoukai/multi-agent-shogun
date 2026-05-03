#!/usr/bin/env python3
"""
hakudokai_ai_jimucho.py — AI 事務長 (Phase C-1, DD-046)

導入院の経営業務全自動化レイヤー (第 9 の柱) のうち、本 sandbox 範囲は:
- 日計表→月次決算転記 (集計)
- 請求入金管理 (未収金追跡)
- KPI ダッシュボード生成 (副医院長報告自動)

設計: 月次 cron で実行、副医院長 (fukuincho) 宛 pc_handshake INSERT で報告。
PII guard 適用、患者識別子 (uuid) 以外は出さない。

Usage:
  hakudokai_ai_jimucho.py --monthly-summary --month 2026-04         # 月次集計
  hakudokai_ai_jimucho.py --monthly-summary --month 2026-04 --report-fukuincho
  hakudokai_ai_jimucho.py --uncollected-track                       # 未収金追跡
  hakudokai_ai_jimucho.py --kpi --month 2026-04                     # KPI 表示

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, date, timedelta, timezone

# audit-fix(phase-c1) Critical #4 (L1-E): JST timezone 統一
try:
    from zoneinfo import ZoneInfo  # type: ignore
    _JST = ZoneInfo("Asia/Tokyo")
except Exception:
    _JST = timezone(timedelta(hours=9))


def _now_jst() -> datetime:
    return datetime.now(_JST)

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[ai_jimucho] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from hakudokai_pii_detector import scan_for_pii  # type: ignore
except ImportError:
    scan_for_pii = None  # type: ignore


CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[ai_jimucho] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _abort_if_pii(text: str, label: str) -> None:
    if not text or scan_for_pii is None:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception:
        return
    if matches:
        sys.stderr.write(
            f"[ai_jimucho] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
        )
        raise SystemExit(5)


def _month_range(month_str: str) -> tuple[date, date]:
    """'2026-04' → (2026-04-01, 2026-05-01)"""
    y, m = month_str.split("-")
    start = date(int(y), int(m), 1)
    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end


def _aggregate_monthly(sb, clinic_id: str, start: date, end: date) -> dict:
    """月次集計: daily_report ヘッダ row を SUM。

    Codex audit C-1-6 #3 修正: report_date 昇順で取得、uncollected_total_eom は
    最後の row (= 月内最新報告日) の uncollected_total を採用、決定的に集計。
    """
    res = (
        sb.table("daily_report")
        .select("report_date,insurance_income,self_pay_total,misc_income_total,"
                "payments_total,income_total,app_payment_received,uncollected_total,"
                "new_patients,appointments,cancellations,total_points")
        .eq("clinic_id", clinic_id)
        .gte("report_date", start.isoformat())
        .lt("report_date", end.isoformat())
        .order("report_date", desc=False)
        .execute()
    )
    rows = res.data or []
    summary = {
        "clinic_id": clinic_id,
        "month": start.isoformat()[:7],
        "report_count": len(rows),
        "insurance_income": 0.0,
        "self_pay_total": 0.0,
        "misc_income_total": 0.0,
        "payments_total": 0.0,
        "income_total": 0.0,
        "uncollected_total_eom": 0.0,
        "app_payment_received": 0.0,
        "new_patients": 0,
        "appointments": 0,
        "cancellations": 0,
        "total_points": 0,
        "latest_report_date": None,
    }
    for r in rows:
        for k in ("insurance_income", "self_pay_total", "misc_income_total",
                  "payments_total", "income_total", "app_payment_received"):
            summary[k] += float(r.get(k) or 0)
        for k in ("new_patients", "appointments", "cancellations", "total_points"):
            summary[k] += int(r.get(k) or 0)
    if rows:
        # 月内最終 report_date の uncollected_total を採用 (昇順 sort 済の last 要素)
        summary["uncollected_total_eom"] = float(rows[-1].get("uncollected_total") or 0)
        summary["latest_report_date"] = rows[-1].get("report_date")
    summary["gross_revenue"] = (
        summary["insurance_income"] + summary["self_pay_total"]
        + summary["misc_income_total"] + summary["app_payment_received"]
    )
    return summary


def _track_uncollected(sb, clinic_id: str) -> dict:
    """未収金追跡: 直近 daily_report_uncollected の現在残高合計。

    audit-fix(phase-c1) Critical #2 (L1-E): patient_id ごとに最新 1 行のみ採用、
    日跨ぎ繰越時の重複計上を防止。supabase-py に DISTINCT ON が無いため
    Python 側で patient_id 別 created_at 降順 sort + dedup 実装。

    Loop 3 (Codex Loop 2 Minor partial): 同一 created_at tie の決定性確保のため
    id 降順を二次キーとして追加. 同時刻同一 patient の複数 row があっても最大 id を
    最新として一意に選定.
    """
    res = (
        sb.table("daily_report_uncollected")
        .select("id,daily_report_id,patient_id,current_amount,created_at")
        .eq("clinic_id", clinic_id)
        .gt("current_amount", 0)
        .order("created_at", desc=True)
        .order("id", desc=True)
        .execute()
    )
    rows = res.data or []
    # patient_id ごとに最新行のみ (created_at 降順、初出だけ採用)
    seen: set = set()
    latest_rows: list[dict] = []
    for r in rows:
        pid = r.get("patient_id")
        if pid is None or pid in seen:
            continue
        seen.add(pid)
        latest_rows.append(r)
    total = sum(float(r.get("current_amount") or 0) for r in latest_rows)
    distinct_patients = len(seen)
    return {
        "clinic_id": clinic_id,
        "row_count": len(latest_rows),
        "raw_history_rows": len(rows),
        "uncollected_total": total,
        "distinct_patients": distinct_patients,
    }


def _kpi(sb, clinic_id: str, start: date, end: date) -> dict:
    summary = _aggregate_monthly(sb, clinic_id, start, end)
    days = (end - start).days
    return {
        "month": summary["month"],
        "clinic_id": clinic_id,
        "report_count": summary["report_count"],
        "days_in_month": days,
        "active_rate": (summary["report_count"] / days) if days > 0 else 0,
        "gross_revenue": summary["gross_revenue"],
        "avg_daily_revenue": (summary["gross_revenue"] / max(1, summary["report_count"])),
        "new_patients": summary["new_patients"],
        "cancel_rate": (
            summary["cancellations"] / max(1, summary["appointments"])
        ),
        "uncollected_total_eom": summary["uncollected_total_eom"],
    }


def _send_report_to_fukuincho(sb, clinic_id: str, summary: dict, kpi: dict,
                               uncollected: dict, dry_run: bool) -> str | None:
    """副医院長へ pc_handshake INSERT (shogun_kind=dashboard_snapshot)。

    audit-fix(phase-c1) Major (L2): idempotency_key を context_data jsonb に入れるだけでは
    pc_handshake テーブルに unique 列がなく 23505 抑止が機能しない。アプリ層 idempotency
    として INSERT 前に同 key の row を SELECT、存在すれば skip する。

    Loop 3 (Codex Loop 2 Major #6 partial): bucket を JST calendar day 文字列に変更.
    int(now.timestamp() // 86400) は UTC 86400 秒境界で切れるため、JST 早朝 (00:00-08:59)
    と同日 09:00 以降が別 bucket になり、同一 JST 日の重複抑止に穴が空いていた.
    """
    now = _now_jst()
    bucket = now.strftime("%Y-%m-%d")  # JST calendar day (Loop 3 修正)
    idem = f"ai-jimucho-monthly-{clinic_id}-{summary['month']}-{bucket}"
    content = (
        f"[AI 事務長 月次レポート] clinic={clinic_id} month={summary['month']}\n"
        f"  report_count={summary['report_count']} days={kpi['days_in_month']} active_rate={kpi['active_rate']:.2%}\n"
        f"  gross_revenue={summary['gross_revenue']:.0f} 円\n"
        f"  insurance={summary['insurance_income']:.0f} self_pay={summary['self_pay_total']:.0f} "
        f"misc={summary['misc_income_total']:.0f} app={summary['app_payment_received']:.0f}\n"
        f"  new_patients={summary['new_patients']} appointments={summary['appointments']} "
        f"cancellations={summary['cancellations']} (cancel_rate={kpi['cancel_rate']:.2%})\n"
        f"  total_points={summary['total_points']}\n"
        f"  uncollected_eom={summary['uncollected_total_eom']:.0f} 円 "
        f"(現在 {uncollected['row_count']} 件 / {uncollected['distinct_patients']} 患者)\n"
    )
    _abort_if_pii(content, "content")
    payload = {
        "from_pc": "main_pc",
        "to_pc": "fukuincho",
        "priority": "normal",
        "topic": f"AI 事務長 月次レポート {clinic_id} {summary['month']}",
        "content": content,
        "message_type": "status_update",
        "requires_response": False,
        "clinic_id": clinic_id,
        "context_data": {
            "shogun_kind": "dashboard_snapshot",
            "kind": "ai_jimucho_monthly",
            "summary": summary,
            "kpi": kpi,
            "uncollected": uncollected,
            "idempotency_key": idem,
        },
    }
    if dry_run:
        sys.stderr.write(f"[ai_jimucho] (dry-run) report content prepared\n")
        sys.stdout.write(content)
        return None
    # audit-fix(phase-c1) Major (L2): アプリ層 idempotency — context_data->>'idempotency_key' で
    # 既存 row を SELECT して重複抑止 (pc_handshake テーブルに unique 列を追加せず)
    try:
        existing = (
            sb.table("pc_handshake")
            .select("id")
            .eq("clinic_id", clinic_id)
            .eq("from_pc", "main_pc")
            .eq("to_pc", "fukuincho")
            .eq("topic", payload["topic"])
            .filter("context_data->>idempotency_key", "eq", idem)
            .limit(1)
            .execute()
        )
        if existing.data:
            sys.stderr.write(
                f"[ai_jimucho] idempotency hit (existing handshake id={existing.data[0]['id']}), skip\n"
            )
            return None
    except Exception:
        # 検索失敗時は INSERT を試行 (副医院長報告は失わない方針)
        pass
    try:
        res = sb.table("pc_handshake").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as exc:
        msg = str(exc)
        if "duplicate key" in msg or "23505" in msg:
            sys.stderr.write(f"[ai_jimucho] idempotency conflict (DB unique), skip\n")
            return None
        sys.stderr.write(f"[ai_jimucho] handshake INSERT failed: {exc}\n")
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI 事務長 (DD-046)")
    sub = parser.add_mutually_exclusive_group(required=True)
    sub.add_argument("--monthly-summary", action="store_true",
                     help="月次集計を表示 (and option report)")
    sub.add_argument("--uncollected-track", action="store_true",
                     help="未収金追跡")
    sub.add_argument("--kpi", action="store_true",
                     help="月次 KPI 表示")

    parser.add_argument("--clinic-id", default=CLINIC_ID)
    parser.add_argument("--month", default=_now_jst().strftime("%Y-%m"),
                        help="集計対象月 YYYY-MM (default: 当月 JST)")
    parser.add_argument("--report-fukuincho", action="store_true",
                        help="副医院長へ pc_handshake で送信")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    sb = _supabase_client()

    if args.uncollected_track:
        u = _track_uncollected(sb, args.clinic_id)
        sys.stdout.write(f"[ai_jimucho] uncollected: {u}\n")
        return 0

    try:
        start, end = _month_range(args.month)
    except Exception:
        sys.stderr.write(f"[ai_jimucho] invalid --month '{args.month}'\n")
        return 2

    if args.kpi:
        kpi = _kpi(sb, args.clinic_id, start, end)
        sys.stdout.write(f"[ai_jimucho] KPI: {kpi}\n")
        return 0

    if args.monthly_summary:
        summary = _aggregate_monthly(sb, args.clinic_id, start, end)
        kpi = _kpi(sb, args.clinic_id, start, end)
        uncollected = _track_uncollected(sb, args.clinic_id)
        sys.stdout.write(f"[ai_jimucho] === 月次集計 {args.clinic_id} {args.month} ===\n")
        for k, v in summary.items():
            sys.stdout.write(f"  {k}: {v}\n")
        sys.stdout.write(f"[ai_jimucho] KPI: {kpi}\n")
        sys.stdout.write(f"[ai_jimucho] uncollected: {uncollected}\n")
        if args.report_fukuincho:
            hid = _send_report_to_fukuincho(sb, args.clinic_id, summary, kpi, uncollected, args.dry_run)
            if hid:
                sys.stdout.write(f"[ai_jimucho] fukuincho 報告 INSERT ok id={hid}\n")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
