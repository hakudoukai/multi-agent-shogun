-- migrations/009_organizational_lessons_rollback.sql
-- cmd_organizational_lessons_supabase_001 — rollback script
--
-- 用途:
--   migrations/007_organizational_lessons.sql + 008_organizational_lessons_seed.sql の取消。
--   migration apply に問題が発生した場合、または table 設計を再構築する場合に逆順実行する。
--
-- 安全装置:
--   - 本 rollback は (4) で trigger を drop した後に table を drop するため、
--     DROP TABLE 時の削除イベントは audit log に **記録されない**。
--     audit log を保全したい場合は本 script 実行**前**に必ず export すること (下記 必須手順)。
--   - DROP TRIGGER は table drop 前に明示
--   - service_role 推奨 (= RLS bypass)
--
-- 適用前 必須手順:
--   1. SELECT count(*) FROM public.organizational_lessons;             -- row 数確認
--   2. SELECT count(*) FROM public.organizational_lessons_audit;       -- audit row 数確認
--   3. pg_dump -t public.organizational_lessons_audit > audit_export.sql
--      (= trigger drop 前に必ず export、本 rollback は audit を破壊する破壊的操作)
--   4. organizational_lessons 本体も必要なら pg_dump で別途 export
--
-- Boy Scout Rule:
--   - 上記 必須手順 を実行せずに本 rollback を流すと audit 履歴が完全消失する
--   - rollback は idempotent (= 再実行可)、ただし二度目以降は drop 対象が既に存在しない
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
-- 注: 本 rollback は (4) で trigger を drop 済のため、以下 DROP TABLE の
-- 削除イベントは audit log に記録されない (= ヘッダ「適用前 必須手順」参照、
-- audit export は本 script 実行前に完了している前提)。
-- audit table を main table より先に drop するのは、その方が安全だが、いずれにせよ
-- trigger drop 後ゆえ順序による audit 記録挙動への影響はない。
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
