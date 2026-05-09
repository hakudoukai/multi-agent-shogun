#!/usr/bin/env python3
"""
hakudokai_heartbeat_archive.py — heartbeat 月次 archive 自動化 (Phase B-4 続編 task 7)

docs/partition-strategy.md §2.2 + Gemini backlog #2 (heartbeat 参照テーブル切替自動化)。
pc_handshake_heartbeat (migrations/003 適用済) から 90 日経過分を archive table へ退避し、
本体 table から削除する。医療情報安全管理ガイドライン 5/7 年保管法令対応。

Usage:
  hakudokai_heartbeat_archive.py [--days 90] [--dry-run] [--archive-table NAME]

設計方針 (docs/partition-strategy.md §2.2):
  (a) DELETE のみ (シンプル、本 script default 動作 = false)
  (b) 別 archive table へ移行 (5/7 年保管法令要件、本 script default 動作 = true)

cron 設定例: 月次 03:00 実行
  0 3 1 * * cd ~/projects/hakudokai-shogun && \\
    HAKUDOKAI_CLINIC_ID=hakudoukai_main \\
    python3 scripts/hakudokai_heartbeat_archive.py --days 90

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[heartbeat_archive] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
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
            "[heartbeat_archive] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _table_exists(sb, name: str) -> bool:
    try:
        sb.table(name).select("id").limit(1).execute()
        return True
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai heartbeat 月次 archive")
    parser.add_argument(
        "--days", type=int, default=90,
        help="保管日数 (default: 90)、これより古い row を archive へ退避",
    )
    parser.add_argument(
        "--archive-table", default="pc_handshake_heartbeat_archive",
        help="archive 先 table 名 (default: pc_handshake_heartbeat_archive)",
    )
    parser.add_argument(
        "--no-archive", action="store_true",
        help="DELETE のみで archive table へ退避しない (法令要件不適合、運用判断のみ)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="対象 row 数のみ報告、archive/DELETE 実行せず",
    )
    args = parser.parse_args(argv)

    sb = _supabase_client()
    src_table = "pc_handshake_heartbeat"

    if not _table_exists(sb, src_table):
        sys.stderr.write(
            f"[heartbeat_archive] {src_table} not found "
            f"(migrations/003 未適用?)、Phase A 経路では archive 対象なし\n"
        )
        return 0

    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=args.days)
    cutoff = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 対象 row 確認
    try:
        res = (
            sb.table(src_table)
            .select("id", count="exact")
            .lt("ts", cutoff)
            .execute()
        )
        target_count = res.count or 0
    except Exception as exc:
        sys.stderr.write(f"[heartbeat_archive] count failed: {exc}\n")
        return 4

    sys.stderr.write(
        f"[heartbeat_archive] cutoff={cutoff} (>{args.days} days), "
        f"target {target_count} rows in {src_table}\n"
    )

    if target_count == 0:
        sys.stderr.write("[heartbeat_archive] no rows to archive\n")
        return 0

    if args.dry_run:
        sys.stderr.write(
            f"[heartbeat_archive] (dry-run) would archive {target_count} rows "
            f"to {args.archive_table}\n"
        )
        return 0

    # archive 先 table 確認
    # Codex audit B-4-EXT #2 修正: archive table 不在時は明示的 --no-archive 指定がなければ abort
    # (warning 後に DELETE 実行は法令保管要件に抵触するため)
    if args.no_archive:
        archive_exists = False
        sys.stderr.write(
            f"[heartbeat_archive] --no-archive 指定、archive 退避なしで DELETE のみ実行。 "
            f"法令保管要件 (5/7 年) 適合は呼出元責任。\n"
        )
    else:
        archive_exists = _table_exists(sb, args.archive_table)
        if not archive_exists:
            sys.stderr.write(
                f"[heartbeat_archive] FATAL: archive table {args.archive_table} not found。"
                f"法令保管要件 (医療情報安全管理 5/7 年) 抵触リスクのため abort。\n"
                f"  hint: archive table を先に作成、or 明示的に --no-archive を指定して保管なし削除を許可。\n"
            )
            return 4

    # archive 退避
    if archive_exists:
        try:
            # SELECT して INSERT する形式 (PostgREST に INSERT INTO ... SELECT は無いため、batch fetch + insert)
            page_size = 500
            offset = 0
            archived_total = 0
            while True:
                fetch = (
                    sb.table(src_table)
                    .select("*")
                    .lt("ts", cutoff)
                    .order("ts")
                    .range(offset, offset + page_size - 1)
                    .execute()
                )
                rows = fetch.data or []
                if not rows:
                    break
                ins = sb.table(args.archive_table).insert(rows).execute()
                archived_total += len(ins.data or [])
                offset += page_size
            sys.stderr.write(
                f"[heartbeat_archive] archived {archived_total} rows to {args.archive_table}\n"
            )
        except Exception as exc:
            sys.stderr.write(
                f"[heartbeat_archive] FATAL archive INSERT failed: {exc}, abort DELETE\n"
            )
            return 4

    # DELETE 実行 (archive 成功時のみ)
    try:
        sb.table(src_table).delete().lt("ts", cutoff).execute()
        sys.stderr.write(
            f"[heartbeat_archive] deleted {target_count} rows from {src_table}\n"
        )
    except Exception as exc:
        sys.stderr.write(f"[heartbeat_archive] DELETE failed: {exc}\n")
        return 4

    sys.stderr.write("[heartbeat_archive] DONE\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
