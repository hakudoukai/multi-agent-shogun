-- migrations/003_phase_b4_pc_handshake_partition.sql
-- Phase B-4 task 8 (Phase B-2 backlog 統合): pc_handshake heartbeat partition / archive 戦略
--
-- 背景: Gemini 拡張監査 Phase B-2 backlog (handshake 01adc1fd)。
--   heartbeat 5min × 5 role × 7 医院 = 月 151,200 行、5 年で約 900 万行。
--   Postgres B-tree index でも実用許容範囲だが、
--   FKI-NO-FUTURE-DEBT-01 (5年10年運用視点) で月次 partition / archive 戦略を導入する。
--
-- 戦略:
--   (a) heartbeat record を別テーブル pc_handshake_heartbeat へ退避 (移行コスト低)
--   (b) pc_handshake 本体は cmd / report / escalation / skill_candidate のみ保持
--   (c) heartbeat_check は両テーブルを UNION で参照、または heartbeat table のみ参照に切替
--
-- 適用前確認:
--   - 理事長承認 (grant_permission handshake、🔴 既存テーブル運用変更)
--   - 副医院長 strategic 適合判定
--   - heartbeat sender / heartbeat_check のリリース調整 (script の参照テーブル切替)
--   - Codex+Gemini dual 🟢 監査
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- ============================================================
-- (1) pc_handshake_heartbeat 新規テーブル (heartbeat 専用)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.pc_handshake_heartbeat (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL DEFAULT 'hakudoukai_main',
    role            text          NOT NULL,
    from_pc         text          NOT NULL,
    ts              timestamptz   NOT NULL DEFAULT now(),
    interval_sec    int           NOT NULL DEFAULT 300,
    bucket_sec      int           NOT NULL DEFAULT 300,
    bucket          bigint        NOT NULL,
    idempotency_key text          NULL,
    created_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT pc_heartbeat_clinic_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT pc_heartbeat_role_check
        CHECK (role IN ('fukuincho', 'yama', 'kuro', 'sakura', 'kouchan'))
);

-- 重複防止 (idempotency UNIQUE、bucket 衝突排除)
CREATE UNIQUE INDEX IF NOT EXISTS pc_heartbeat_idem_uidx
    ON public.pc_handshake_heartbeat (clinic_id, role, bucket_sec, bucket);

CREATE INDEX IF NOT EXISTS pc_heartbeat_role_ts_idx
    ON public.pc_handshake_heartbeat (clinic_id, role, ts DESC);

CREATE INDEX IF NOT EXISTS pc_heartbeat_ts_idx
    ON public.pc_handshake_heartbeat (ts);

ALTER TABLE public.pc_handshake_heartbeat ENABLE ROW LEVEL SECURITY;

-- Codex audit B-4-3 #3 修正: 再実行安全性のため DROP POLICY IF EXISTS → CREATE POLICY pattern
DROP POLICY IF EXISTS pc_heartbeat_4layer_clinic ON public.pc_handshake_heartbeat;
CREATE POLICY pc_heartbeat_4layer_clinic ON public.pc_handshake_heartbeat
    FOR ALL
    TO hakudokai_4layer_role
    USING (clinic_id = current_setting('app.current_clinic_id', true))
    WITH CHECK (clinic_id = current_setting('app.current_clinic_id', true));

DROP POLICY IF EXISTS pc_heartbeat_service_full ON public.pc_handshake_heartbeat;
CREATE POLICY pc_heartbeat_service_full ON public.pc_handshake_heartbeat
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

COMMENT ON TABLE public.pc_handshake_heartbeat IS '博道会 heartbeat 専用 (Phase B-4 task 8 / B-2 backlog 統合, DD-146)';

-- ============================================================
-- (2) 既存 pc_handshake 内 heartbeat row の移行 (option、運用判断)
-- ============================================================
-- 注: 既存 heartbeat row を heartbeat table へ移行する場合、以下を実行 (option)
-- bucket = floor(epoch(created_at) / bucket_sec) で派生計算 (idempotency_key text 列ではない)
-- Codex audit B-4-3 #3 修正: 旧 idempotency_key bigint cast を bucket 派生計算に置換
-- INSERT INTO public.pc_handshake_heartbeat (
--     id, clinic_id, role, from_pc, ts, interval_sec, bucket_sec, bucket, idempotency_key, created_at
-- )
-- SELECT
--     id,
--     clinic_id,
--     COALESCE((context_data->>'role'), from_pc),
--     from_pc,
--     created_at,
--     COALESCE((context_data->>'interval_sec')::int, 300),
--     COALESCE((context_data->>'bucket_sec')::int, 300),
--     (EXTRACT(epoch FROM created_at)::bigint
--         / GREATEST(60, COALESCE((context_data->>'bucket_sec')::int, 300)))::bigint,
--     (context_data->>'idempotency_key'),
--     created_at
-- FROM public.pc_handshake
-- WHERE context_data->>'shogun_kind' = 'heartbeat';
-- 移行後に元 row を削除する場合は別 transaction で慎重に:
-- DELETE FROM public.pc_handshake WHERE context_data->>'shogun_kind' = 'heartbeat';

-- ============================================================
-- (3) 古い heartbeat archive (90日経過分)
-- ============================================================
-- pg_cron などで定期実行 (本 migration には apply 含めない、運用設計のみ提示)
-- 例:
-- DELETE FROM public.pc_handshake_heartbeat
-- WHERE ts < now() - interval '90 days';
-- もしくは別 archive table へ INSERT 後 DELETE。

COMMIT;

-- ============================================================
-- rollback: 失敗時は逆順実行
-- ============================================================
-- BEGIN;
-- DROP POLICY IF EXISTS pc_heartbeat_service_full ON public.pc_handshake_heartbeat;
-- DROP POLICY IF EXISTS pc_heartbeat_4layer_clinic ON public.pc_handshake_heartbeat;
-- ALTER TABLE public.pc_handshake_heartbeat DISABLE ROW LEVEL SECURITY;
-- DROP INDEX IF EXISTS public.pc_heartbeat_ts_idx;
-- DROP INDEX IF EXISTS public.pc_heartbeat_role_ts_idx;
-- DROP INDEX IF EXISTS public.pc_heartbeat_idem_uidx;
-- DROP TABLE IF EXISTS public.pc_handshake_heartbeat;
-- COMMIT;
