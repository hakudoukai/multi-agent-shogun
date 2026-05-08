"""
tests/migrations/test_organizational_lessons_rls.py
cmd_organizational_lessons_supabase_001 cycle2 — RLS + trigger 実 apply test (Python harness).

呼出: tests/migrations/test_organizational_lessons_rls.sh 経由 (= venv 自動 bootstrap)

検証項目 (task subtask_organizational_lessons_supabase_001_cycle2 仕様):
  T1. honda INSERT 成功 + audit row 生成 (performed_by='honda')
  T2. hideyoshi / shogun も INSERT 成功
  T3. ashigaru1 INSERT 失敗 (= RLS WITH CHECK 拒否)
  T4. rijicho DELETE 成功 (rowcount=1)
  T5. honda DELETE 不可 (= RLS USING で row 不可視、rowcount=0)
  T6. SELECT 全 agent 可 (read_all policy)
  T7. audit_log() prosecdef = true (= SECURITY DEFINER 設定確認)
  T8. audit_log() proconfig に search_path 固定設定があること
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

import pgserver
import psycopg

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATION_PATH = REPO_ROOT / "backend" / "migrations" / "007_organizational_lessons.sql"


def _run_role_op(uri: str, agent: str, sql: str, params: tuple = ()) -> tuple[int, Exception | None]:
    """authenticated role + SET LOCAL app.current_agent で sql 実行、(rowcount, exc) を返す。"""
    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                cur.execute("SET ROLE authenticated")
                cur.execute("SELECT set_config('app.current_agent', %s, true)", (agent,))
                cur.execute(sql, params)
                rc = cur.rowcount
            conn.commit()
            return rc, None
    except Exception as exc:  # noqa: BLE001 — 例外内容の判定が目的
        return -1, exc


def _is_rls_violation(exc: Exception) -> bool:
    """RLS 違反由来の例外か判定 (Postgres 9.5+ は SQLSTATE 42501)。"""
    sqlstate = getattr(exc, "sqlstate", None) or getattr(exc, "diag", None)
    if sqlstate == "42501":
        return True
    msg = str(exc).lower()
    return "row-level security" in msg or "row level security" in msg


def main() -> int:
    fail_count = 0
    results: list[tuple[str, bool, str]] = []

    with tempfile.TemporaryDirectory(prefix="pgrls_") as tmpdir:
        print(f"[pg] starting ephemeral postgres at {tmpdir}")
        server = pgserver.get_server(tmpdir, cleanup_mode="stop")
        try:
            uri = server.get_uri()
            print(f"[pg] uri = {uri}")

            # ------------------------------------------------------------------
            # Pre-apply: Supabase 模倣で authenticated / service_role を作成
            #            (= migration 007 内 `TO authenticated` 参照のため必須)
            # ------------------------------------------------------------------
            with psycopg.connect(uri, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute("CREATE ROLE authenticated NOLOGIN")
                    cur.execute("CREATE ROLE service_role NOLOGIN BYPASSRLS")
            print("[setup] roles created (authenticated, service_role)")

            # ------------------------------------------------------------------
            # Apply migration as superuser (= postgres) → owns audit_log() function
            # ------------------------------------------------------------------
            with psycopg.connect(uri, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute(MIGRATION_PATH.read_text())

                # CRUD grant を別途付与 (= Supabase の auth grants 模倣)
                with conn.cursor() as cur:
                    cur.execute("GRANT USAGE ON SCHEMA public TO authenticated")
                    cur.execute(
                        "GRANT SELECT, INSERT, UPDATE, DELETE "
                        "ON public.organizational_lessons TO authenticated"
                    )
                    # audit table は SELECT のみ (= INSERT は trigger SECURITY DEFINER 経由のみ)
                    cur.execute(
                        "GRANT SELECT ON public.organizational_lessons_audit TO authenticated"
                    )
            print("[apply] migration 007 applied + grants configured")

            # ------------------------------------------------------------------
            # T1. honda INSERT 成功 + audit row 生成
            # ------------------------------------------------------------------
            insert_sql = (
                "INSERT INTO public.organizational_lessons "
                "(incident_date, category, root_cause, lessons, tags) "
                "VALUES (now(), 'routing', 'rc honda', 'lesson honda', ARRAY['t1']) "
                "RETURNING id"
            )
            try:
                with psycopg.connect(uri) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SET ROLE authenticated")
                        cur.execute("SELECT set_config('app.current_agent', 'honda', true)")
                        cur.execute(insert_sql)
                        honda_id = cur.fetchone()[0]
                    conn.commit()
                # audit row 確認 (superuser で読み出し)
                with psycopg.connect(uri, autocommit=True) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT operation, performed_by FROM public.organizational_lessons_audit "
                            "WHERE lesson_id = %s",
                            (honda_id,),
                        )
                        rows = cur.fetchall()
                t1_pass = len(rows) == 1 and rows[0] == ("INSERT", "honda")
                results.append(("T1 honda INSERT + audit row", t1_pass, f"audit rows: {rows}"))
            except Exception as exc:  # noqa: BLE001
                results.append(("T1 honda INSERT + audit row", False, f"unexpected: {exc!r}"))

            # ------------------------------------------------------------------
            # T2. hideyoshi / shogun も INSERT 成功 (writer 全員)
            # ------------------------------------------------------------------
            t2_pass = True
            t2_detail = []
            for writer in ("hideyoshi", "shogun"):
                rc, exc = _run_role_op(
                    uri,
                    writer,
                    (
                        "INSERT INTO public.organizational_lessons "
                        "(incident_date, category, root_cause, lessons, tags) "
                        "VALUES (now(), 'routing', %s, %s, ARRAY['t2'])"
                    ),
                    (f"rc {writer}", f"lesson {writer}"),
                )
                ok = exc is None and rc == 1
                t2_detail.append(f"{writer}: rc={rc}, exc={exc!r}")
                if not ok:
                    t2_pass = False
            results.append(("T2 hideyoshi/shogun INSERT 成功", t2_pass, "; ".join(t2_detail)))

            # ------------------------------------------------------------------
            # T3. ashigaru1 INSERT 失敗
            # ------------------------------------------------------------------
            rc, exc = _run_role_op(
                uri,
                "ashigaru1",
                (
                    "INSERT INTO public.organizational_lessons "
                    "(incident_date, category, root_cause, lessons, tags) "
                    "VALUES (now(), 'routing', 'rc ashigaru', 'lesson ashigaru', ARRAY['t3'])"
                ),
            )
            t3_pass = exc is not None and _is_rls_violation(exc)
            results.append(
                (
                    "T3 ashigaru1 INSERT blocked",
                    t3_pass,
                    f"rc={rc}, exc={exc!r}",
                )
            )

            # ------------------------------------------------------------------
            # T4. rijicho DELETE 成功 (T1 で作った honda_id 行を削除)
            # ------------------------------------------------------------------
            try:
                rc, exc = _run_role_op(
                    uri,
                    "rijicho",
                    "DELETE FROM public.organizational_lessons WHERE id = %s",
                    (honda_id,),
                )
                t4_pass = exc is None and rc == 1
                results.append(("T4 rijicho DELETE 成功", t4_pass, f"rc={rc}, exc={exc!r}"))
            except Exception as exc:  # noqa: BLE001
                results.append(("T4 rijicho DELETE 成功", False, f"unexpected: {exc!r}"))
                honda_id = None

            # ------------------------------------------------------------------
            # T5. honda DELETE 不可 (= RLS USING で row 不可視、rowcount=0)
            #     T2 で hideyoshi/shogun が作った row を honda が DELETE 試行
            # ------------------------------------------------------------------
            with psycopg.connect(uri, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM public.organizational_lessons "
                        "WHERE root_cause = 'rc hideyoshi' LIMIT 1"
                    )
                    row = cur.fetchone()
                    target_id = row[0] if row else None

            if target_id is None:
                results.append(("T5 honda DELETE blocked (rowcount=0)", False, "no target row"))
            else:
                rc, exc = _run_role_op(
                    uri,
                    "honda",
                    "DELETE FROM public.organizational_lessons WHERE id = %s",
                    (target_id,),
                )
                # honda は DELETE policy 不適用ゆえ USING で row 見えず → rowcount=0、例外なし
                t5_pass = exc is None and rc == 0
                results.append(
                    (
                        "T5 honda DELETE blocked (rowcount=0)",
                        t5_pass,
                        f"rc={rc}, exc={exc!r}",
                    )
                )

            # ------------------------------------------------------------------
            # T6. SELECT 全 agent 可
            # ------------------------------------------------------------------
            t6_pass = True
            t6_detail = []
            for agent in ("honda", "hideyoshi", "shogun", "ashigaru1", "rijicho", "unknown"):
                try:
                    with psycopg.connect(uri) as conn:
                        with conn.cursor() as cur:
                            cur.execute("SET ROLE authenticated")
                            cur.execute(
                                "SELECT set_config('app.current_agent', %s, true)", (agent,)
                            )
                            cur.execute("SELECT count(*) FROM public.organizational_lessons")
                            cnt = cur.fetchone()[0]
                    t6_detail.append(f"{agent}={cnt}")
                except Exception as exc:  # noqa: BLE001
                    t6_pass = False
                    t6_detail.append(f"{agent}=ERR({exc!r})")
            results.append(("T6 SELECT all agents", t6_pass, "; ".join(t6_detail)))

            # ------------------------------------------------------------------
            # T7. audit_log() prosecdef = true
            # T8. audit_log() proconfig に search_path 設定
            # ------------------------------------------------------------------
            with psycopg.connect(uri, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT prosecdef, proconfig FROM pg_proc "
                        "WHERE proname = 'organizational_lessons_audit_log' "
                        "AND pronamespace = 'public'::regnamespace"
                    )
                    row = cur.fetchone()
            if row is None:
                results.append(("T7 audit_log() SECURITY DEFINER", False, "function missing"))
                results.append(("T8 audit_log() search_path locked", False, "function missing"))
            else:
                prosecdef, proconfig = row
                t7_pass = prosecdef is True
                results.append(("T7 audit_log() SECURITY DEFINER", t7_pass, f"prosecdef={prosecdef}"))

                proconfig_list = proconfig or []
                search_path_entries = [c for c in proconfig_list if c.startswith("search_path=")]
                t8_pass = len(search_path_entries) > 0
                results.append(
                    (
                        "T8 audit_log() search_path locked",
                        t8_pass,
                        f"proconfig={proconfig_list}",
                    )
                )

            # ------------------------------------------------------------------
            # Report
            # ------------------------------------------------------------------
            print()
            print("=" * 72)
            print("organizational_lessons RLS + SECURITY DEFINER trigger apply test")
            print("=" * 72)
            for name, ok, detail in results:
                mark = "PASS" if ok else "FAIL"
                print(f"  [{mark}] {name}")
                if not ok:
                    print(f"         detail: {detail}")
                    fail_count += 1
            print("=" * 72)
            if fail_count:
                print(f"FAIL: {fail_count}/{len(results)} test(s) failed")
                return 1
            print(f"PASS: all {len(results)} test(s) passed")
            return 0
        finally:
            server.cleanup()


if __name__ == "__main__":
    sys.exit(main())
