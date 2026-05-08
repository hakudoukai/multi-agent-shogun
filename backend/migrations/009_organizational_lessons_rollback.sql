-- migrations/009_organizational_lessons_rollback.sql
-- cmd_organizational_lessons_supabase_001 — rollback script
--
-- 用途:
--   migrations/007_organizational_lessons.sql + 008_organizational_lessons_seed.sql の取消。
--   migration apply に問題が発生した場合、または table 設計を再構築する場合に逆順実行する。
--
-- 安全装置:
--   - audit table を先に drop しないこと (= main table の drop trigger により記録されるため)
--   - DROP TRIGGER は table drop 前に明示
--   - service_role 推奨 (= RLS bypass)
--
-- Boy Scout Rule:
--   - 適用前に SELECT count(*) FROM public.organizational_lessons; で row 数確認
--   - audit log は别途 export (CSV / pg_dump) してから rollback すること推奨
--   - rollback 履歴は organizational_lessons_audit を pg_dump で残してから drop
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- ============================================================
-- (1) RLS policy drop — organizational_lessons
-- ============================================================
DROP POLICY IF EXISTS organizational_lessons_service_full ON public.organizational_lessons;
DROP POLICY IF EXISTS organizational_lessons_delete_rijicho ON public.organizational_lessons;
DROP POLICY IF EXISTS organizational_lessons_update_writers ON public.organizational_lessons;
DROP POLICY IF EXISTS organizational_lessons_insert_writers ON public.organizational_lessons;
DROP POLICY IF EXISTS organizational_lessons_read_all ON public.organizational_lessons;

-- ============================================================
-- (2) RLS policy drop — organizational_lessons_audit
-- ============================================================
DROP POLICY IF EXISTS organizational_lessons_audit_service_full ON public.organizational_lessons_audit;
DROP POLICY IF EXISTS organizational_lessons_audit_read_all ON public.organizational_lessons_audit;

-- ============================================================
-- (3) RLS disable
-- ============================================================
ALTER TABLE IF EXISTS public.organizational_lessons DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.organizational_lessons_audit DISABLE ROW LEVEL SECURITY;

-- ============================================================
-- (4) trigger drop
-- ============================================================
DROP TRIGGER IF EXISTS organizational_lessons_audit_trg ON public.organizational_lessons;
DROP TRIGGER IF EXISTS organizational_lessons_updated_at ON public.organizational_lessons;

-- ============================================================
-- (5) function drop
-- ============================================================
DROP FUNCTION IF EXISTS public.organizational_lessons_audit_log();
DROP FUNCTION IF EXISTS public.organizational_lessons_set_updated_at();

-- ============================================================
-- (6) index drop (= table drop で連鎖するが明示しておく)
-- ============================================================
DROP INDEX IF EXISTS public.organizational_lessons_audit_at_idx;
DROP INDEX IF EXISTS public.organizational_lessons_audit_lesson_idx;
DROP INDEX IF EXISTS public.organizational_lessons_tags_gin_idx;
DROP INDEX IF EXISTS public.organizational_lessons_category_idx;
DROP INDEX IF EXISTS public.organizational_lessons_incident_date_idx;

-- ============================================================
-- (7) table drop
-- ============================================================
-- 注: audit table を先に drop すると、main table 側の trigger が動作した場合に
-- 記録先が消えることになるが、本 rollback は trigger も既に drop 済ゆえ安全。
DROP TABLE IF EXISTS public.organizational_lessons_audit;
DROP TABLE IF EXISTS public.organizational_lessons;

COMMIT;

-- ============================================================
-- 動作確認 SQL (= rollback 後の検証用、参考)
-- ============================================================
-- SELECT to_regclass('public.organizational_lessons');                  -- 期待: NULL
-- SELECT to_regclass('public.organizational_lessons_audit');            -- 期待: NULL
-- SELECT proname FROM pg_proc
--   WHERE proname LIKE 'organizational_lessons%';                       -- 期待: 0 row
