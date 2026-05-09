-- migrations/002_phase_b4_clinic_id_4ai_tables.sql
-- Phase B-4 task 2: 4AI tables へ clinic_id 列追加 + RLS
--
-- 対象: mcp_audit_log / dev_lessons / pc_env_sync_log / session_minutes
-- 既存 1400+ row は default 'hakudoukai_main' で backfill (Phase R2 と同パターン)
--
-- 背景: PHASE_B_ROADMAP §4 task 2 + Phase B-3 backlog (dev_lessons clinic_id Gemini 提案)。
--   7 医院 SaaS 化時に各院の dev_lessons / 監査ログ / セッション議事録が clinic boundary で分離されることを保証。
--
-- 適用前確認:
--   - 理事長承認 (grant_permission handshake、🔴 既存テーブル変更含む)
--   - 副医院長 strategic 適合判定
--   - 山ちゃん 法令適合審査
--   - Codex+Gemini dual 🟢 監査
--   - 既存 row count を verbatim 確認 (apply 後の row count 一致確認用)
--
-- Codex audit B-4-3 #1-2 修正: 再実行安全性のため DROP CONSTRAINT IF EXISTS → ADD CONSTRAINT、
-- DROP POLICY IF EXISTS → CREATE POLICY pattern を全箇所で適用。
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- ============================================================
-- (1) dev_lessons table
-- ============================================================
ALTER TABLE public.dev_lessons
    ADD COLUMN IF NOT EXISTS clinic_id text NOT NULL DEFAULT 'hakudoukai_main';

ALTER TABLE public.dev_lessons DROP CONSTRAINT IF EXISTS dev_lessons_clinic_id_format;
ALTER TABLE public.dev_lessons
    ADD CONSTRAINT dev_lessons_clinic_id_format
    CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64);

CREATE INDEX IF NOT EXISTS dev_lessons_clinic_id_idx
    ON public.dev_lessons (clinic_id);

ALTER TABLE public.dev_lessons ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS dev_lessons_4layer_clinic ON public.dev_lessons;
CREATE POLICY dev_lessons_4layer_clinic ON public.dev_lessons
    FOR ALL
    TO hakudokai_4layer_role
    USING (clinic_id = current_setting('app.current_clinic_id', true))
    WITH CHECK (clinic_id = current_setting('app.current_clinic_id', true));

-- ============================================================
-- (2) mcp_audit_log table
-- ============================================================
ALTER TABLE public.mcp_audit_log
    ADD COLUMN IF NOT EXISTS clinic_id text NOT NULL DEFAULT 'hakudoukai_main';

ALTER TABLE public.mcp_audit_log DROP CONSTRAINT IF EXISTS mcp_audit_log_clinic_id_format;
ALTER TABLE public.mcp_audit_log
    ADD CONSTRAINT mcp_audit_log_clinic_id_format
    CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64);

CREATE INDEX IF NOT EXISTS mcp_audit_log_clinic_id_idx
    ON public.mcp_audit_log (clinic_id);

ALTER TABLE public.mcp_audit_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS mcp_audit_log_4layer_clinic ON public.mcp_audit_log;
CREATE POLICY mcp_audit_log_4layer_clinic ON public.mcp_audit_log
    FOR ALL
    TO hakudokai_4layer_role
    USING (clinic_id = current_setting('app.current_clinic_id', true))
    WITH CHECK (clinic_id = current_setting('app.current_clinic_id', true));

-- ============================================================
-- (3) pc_env_sync_log table
-- ============================================================
ALTER TABLE public.pc_env_sync_log
    ADD COLUMN IF NOT EXISTS clinic_id text NOT NULL DEFAULT 'hakudoukai_main';

ALTER TABLE public.pc_env_sync_log DROP CONSTRAINT IF EXISTS pc_env_sync_log_clinic_id_format;
ALTER TABLE public.pc_env_sync_log
    ADD CONSTRAINT pc_env_sync_log_clinic_id_format
    CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64);

CREATE INDEX IF NOT EXISTS pc_env_sync_log_clinic_id_idx
    ON public.pc_env_sync_log (clinic_id);

ALTER TABLE public.pc_env_sync_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS pc_env_sync_log_4layer_clinic ON public.pc_env_sync_log;
CREATE POLICY pc_env_sync_log_4layer_clinic ON public.pc_env_sync_log
    FOR ALL
    TO hakudokai_4layer_role
    USING (clinic_id = current_setting('app.current_clinic_id', true))
    WITH CHECK (clinic_id = current_setting('app.current_clinic_id', true));

-- ============================================================
-- (4) session_minutes table
-- ============================================================
ALTER TABLE public.session_minutes
    ADD COLUMN IF NOT EXISTS clinic_id text NOT NULL DEFAULT 'hakudoukai_main';

ALTER TABLE public.session_minutes DROP CONSTRAINT IF EXISTS session_minutes_clinic_id_format;
ALTER TABLE public.session_minutes
    ADD CONSTRAINT session_minutes_clinic_id_format
    CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64);

CREATE INDEX IF NOT EXISTS session_minutes_clinic_id_idx
    ON public.session_minutes (clinic_id);

ALTER TABLE public.session_minutes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS session_minutes_4layer_clinic ON public.session_minutes;
CREATE POLICY session_minutes_4layer_clinic ON public.session_minutes
    FOR ALL
    TO hakudokai_4layer_role
    USING (clinic_id = current_setting('app.current_clinic_id', true))
    WITH CHECK (clinic_id = current_setting('app.current_clinic_id', true));

-- ============================================================
-- service_role policy (Phase A 互換、Phase B 切替後 revoke)
-- ============================================================
DROP POLICY IF EXISTS dev_lessons_service_full ON public.dev_lessons;
CREATE POLICY dev_lessons_service_full ON public.dev_lessons FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS mcp_audit_log_service_full ON public.mcp_audit_log;
CREATE POLICY mcp_audit_log_service_full ON public.mcp_audit_log FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS pc_env_sync_log_service_full ON public.pc_env_sync_log;
CREATE POLICY pc_env_sync_log_service_full ON public.pc_env_sync_log FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS session_minutes_service_full ON public.session_minutes;
CREATE POLICY session_minutes_service_full ON public.session_minutes FOR ALL TO service_role USING (true) WITH CHECK (true);

COMMIT;

-- ============================================================
-- rollback: 失敗時は逆順実行
-- ============================================================
-- BEGIN;
-- DROP POLICY IF EXISTS session_minutes_service_full ON public.session_minutes;
-- DROP POLICY IF EXISTS pc_env_sync_log_service_full ON public.pc_env_sync_log;
-- DROP POLICY IF EXISTS mcp_audit_log_service_full ON public.mcp_audit_log;
-- DROP POLICY IF EXISTS dev_lessons_service_full ON public.dev_lessons;
-- DROP POLICY IF EXISTS session_minutes_4layer_clinic ON public.session_minutes;
-- DROP POLICY IF EXISTS pc_env_sync_log_4layer_clinic ON public.pc_env_sync_log;
-- DROP POLICY IF EXISTS mcp_audit_log_4layer_clinic ON public.mcp_audit_log;
-- DROP POLICY IF EXISTS dev_lessons_4layer_clinic ON public.dev_lessons;
-- ALTER TABLE public.session_minutes DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.pc_env_sync_log DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.mcp_audit_log DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.dev_lessons DISABLE ROW LEVEL SECURITY;
-- DROP INDEX IF EXISTS public.session_minutes_clinic_id_idx;
-- DROP INDEX IF EXISTS public.pc_env_sync_log_clinic_id_idx;
-- DROP INDEX IF EXISTS public.mcp_audit_log_clinic_id_idx;
-- DROP INDEX IF EXISTS public.dev_lessons_clinic_id_idx;
-- ALTER TABLE public.session_minutes DROP CONSTRAINT IF EXISTS session_minutes_clinic_id_format;
-- ALTER TABLE public.pc_env_sync_log DROP CONSTRAINT IF EXISTS pc_env_sync_log_clinic_id_format;
-- ALTER TABLE public.mcp_audit_log DROP CONSTRAINT IF EXISTS mcp_audit_log_clinic_id_format;
-- ALTER TABLE public.dev_lessons DROP CONSTRAINT IF EXISTS dev_lessons_clinic_id_format;
-- ALTER TABLE public.session_minutes DROP COLUMN IF EXISTS clinic_id;
-- ALTER TABLE public.pc_env_sync_log DROP COLUMN IF EXISTS clinic_id;
-- ALTER TABLE public.mcp_audit_log DROP COLUMN IF EXISTS clinic_id;
-- ALTER TABLE public.dev_lessons DROP COLUMN IF EXISTS clinic_id;
-- COMMIT;
