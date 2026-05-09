-- migrations/001_phase_b4_clinic_master.sql
-- Phase B-4 task 1: clinic_master テーブル新規作成 + 7 医院 row backfill
--
-- 背景: PHASE_B_ROADMAP §4 task 1 に基づく 7 医院 standard construct 化 第一歩。
--   billing 連動 (T15/T17/T19) + regulatory compliance (個人情報保護法 / 医療情報安全管理 / 3省) を
--   見据えた SaaS マルチテナント基盤の master table を確立する。
--
-- 適用前確認:
--   - 理事長承認 (grant_permission handshake)
--   - 副医院長 strategic 適合判定
--   - 山ちゃん 法令適合審査
--   - Codex+Gemini dual 🟢 監査
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

CREATE TABLE IF NOT EXISTS public.clinic_master (
    clinic_id           text         PRIMARY KEY,
    clinic_name         text         NOT NULL,
    postal_address      text         NULL,
    phone               text         NULL,
    email               text         NULL,
    subscription_tier   text         NOT NULL DEFAULT 'T15'
        CHECK (subscription_tier IN ('T15', 'T17', 'T19')),
    billing_start_at    timestamptz  NULL,
    active              boolean      NOT NULL DEFAULT true,
    created_at          timestamptz  NOT NULL DEFAULT now(),
    updated_at          timestamptz  NOT NULL DEFAULT now(),

    -- clinic_id format check (既存 pc_handshake.clinic_id と同一規約)
    CONSTRAINT clinic_master_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64)
);

CREATE INDEX IF NOT EXISTS clinic_master_active_idx
    ON public.clinic_master (active)
    WHERE active = true;

COMMENT ON TABLE  public.clinic_master IS '博道会 7 医院 SaaS マルチテナント master (Phase B-4 task 1, DD-146)';
COMMENT ON COLUMN public.clinic_master.clinic_id IS 'pc_handshake.clinic_id 等と整合 (^[a-z0-9_]+$ 3-64)';
COMMENT ON COLUMN public.clinic_master.subscription_tier IS 'T15 / T17 / T19 (DentalBI 構想完全版 v2.0)';

-- 7 医院 row backfill (CLAUDE.md §Clinic ID体系 準拠)
INSERT INTO public.clinic_master (clinic_id, clinic_name, subscription_tier, active)
VALUES
    ('hakudoukai_main',   '佐世保本院',           'T19', true),
    ('marquise',          'マークイズ',           'T17', true),
    ('island_city',       'アイランドシティ',     'T17', true),
    ('kashii_teriha',     '香椎照葉',             'T17', true),
    ('roppon_matsu',      '六本松',               'T15', true),
    ('tenjin',            '天神',                 'T15', true),
    ('hakata',            '博多',                 'T15', true)
ON CONFLICT (clinic_id) DO NOTHING;

-- RLS 有効化 (default deny、policy で hakudokai_4layer_role に許可)
-- Codex audit B-4-3 #1 修正: 再実行安全性のため DROP IF EXISTS → CREATE pattern
ALTER TABLE public.clinic_master ENABLE ROW LEVEL SECURITY;

-- 4 layer role: 自身の clinic_id のみ SELECT 可
DROP POLICY IF EXISTS clinic_master_4layer_select ON public.clinic_master;
CREATE POLICY clinic_master_4layer_select ON public.clinic_master
    FOR SELECT
    TO hakudokai_4layer_role
    USING (clinic_id = current_setting('app.current_clinic_id', true));

-- service_role は Phase A 互換のため全 clinic 参照可 (Phase B 切替後は revoke)
DROP POLICY IF EXISTS clinic_master_service_full ON public.clinic_master;
CREATE POLICY clinic_master_service_full ON public.clinic_master
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- updated_at trigger
CREATE OR REPLACE FUNCTION public.clinic_master_set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS clinic_master_set_updated_at ON public.clinic_master;
CREATE TRIGGER clinic_master_set_updated_at
    BEFORE UPDATE ON public.clinic_master
    FOR EACH ROW EXECUTE FUNCTION public.clinic_master_set_updated_at();

COMMIT;

-- ============================================================
-- rollback: 失敗時は逆順実行
-- ============================================================
-- BEGIN;
-- DROP TRIGGER IF EXISTS clinic_master_set_updated_at ON public.clinic_master;
-- DROP FUNCTION IF EXISTS public.clinic_master_set_updated_at();
-- DROP POLICY IF EXISTS clinic_master_service_full ON public.clinic_master;
-- DROP POLICY IF EXISTS clinic_master_4layer_select ON public.clinic_master;
-- ALTER TABLE public.clinic_master DISABLE ROW LEVEL SECURITY;
-- DROP INDEX IF EXISTS public.clinic_master_active_idx;
-- DROP TABLE IF EXISTS public.clinic_master;
-- COMMIT;
