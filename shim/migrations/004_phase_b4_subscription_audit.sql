-- migrations/004_phase_b4_subscription_audit.sql
-- Phase B-4 続編 task 6: subscription_tier 変更履歴 audit table
--
-- 背景: Gemini 拡張監査 Phase B-4-4 backlog #1 (handshake 1d8af923)。
--   clinic_master.subscription_tier (T15/T17/T19) 変更時の audit log を専用 table で保持し、
--   billing 連動 + 緊急時切替記録 + 5/7 年保管法令対応 (医療情報安全管理ガイドライン) を満たす。
--
-- 適用前確認:
--   - 理事長承認 (grant_permission handshake、🔴 既存テーブル運用変更含む)
--   - 副医院長 strategic 適合判定
--   - 山ちゃん 法令適合審査
--   - Codex+Gemini dual 🟢 監査
--   - clinic_master (migrations/001) apply 後 (前提依存)
--
-- 設計:
--   - clinic_master.subscription_tier UPDATE 時に trigger で audit row 自動 INSERT
--   - 旧 tier / 新 tier / 変更日時 / 変更理由 (option) / 変更者 (option) を記録
--   - clinic_id boundary RLS で他院の audit log 参照不可
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- ============================================================
-- (1) clinic_subscription_audit テーブル新規作成
-- ============================================================
CREATE TABLE IF NOT EXISTS public.clinic_subscription_audit (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    tier_before     text          NULL
        CHECK (tier_before IS NULL OR tier_before IN ('T15', 'T17', 'T19')),
    tier_after      text          NOT NULL
        CHECK (tier_after IN ('T15', 'T17', 'T19')),
    changed_at      timestamptz   NOT NULL DEFAULT now(),
    change_reason   text          NULL,
    changed_by      text          NULL,
    -- Phase A 互換: 既存 row backfill 用、source = 'system' / 'fukuincho' / 'rijicho' 等
    source          text          NOT NULL DEFAULT 'system',
    created_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT clinic_subscription_audit_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64)
);

CREATE INDEX IF NOT EXISTS clinic_subscription_audit_clinic_idx
    ON public.clinic_subscription_audit (clinic_id, changed_at DESC);

CREATE INDEX IF NOT EXISTS clinic_subscription_audit_changed_at_idx
    ON public.clinic_subscription_audit (changed_at DESC);

COMMENT ON TABLE public.clinic_subscription_audit IS
    '博道会 7 医院 subscription_tier 変更 audit (Phase B-4 続編 task 6, DD-146 / Gemini backlog #1)';

-- ============================================================
-- (2) clinic_master.subscription_tier 変更 trigger
-- ============================================================
CREATE OR REPLACE FUNCTION public.clinic_subscription_audit_log()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- INSERT 時 (新規 clinic_master row): tier_before=NULL, tier_after=NEW.subscription_tier
    IF TG_OP = 'INSERT' THEN
        INSERT INTO public.clinic_subscription_audit (
            clinic_id, tier_before, tier_after, changed_at, source
        ) VALUES (
            NEW.clinic_id, NULL, NEW.subscription_tier, now(), 'system_initial'
        );
        RETURN NEW;
    END IF;

    -- UPDATE 時: subscription_tier 変更がある場合のみ audit 記録
    IF TG_OP = 'UPDATE' AND
       (OLD.subscription_tier IS DISTINCT FROM NEW.subscription_tier) THEN
        INSERT INTO public.clinic_subscription_audit (
            clinic_id, tier_before, tier_after, changed_at, source
        ) VALUES (
            NEW.clinic_id, OLD.subscription_tier, NEW.subscription_tier,
            now(), 'system_update'
        );
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS clinic_master_subscription_audit ON public.clinic_master;
CREATE TRIGGER clinic_master_subscription_audit
    AFTER INSERT OR UPDATE ON public.clinic_master
    FOR EACH ROW EXECUTE FUNCTION public.clinic_subscription_audit_log();

-- ============================================================
-- (3) RLS 適用 (clinic_id boundary)
-- ============================================================
ALTER TABLE public.clinic_subscription_audit ENABLE ROW LEVEL SECURITY;

-- 4 layer role: 自身の clinic_id のみ SELECT 可
DROP POLICY IF EXISTS clinic_subscription_audit_4layer_select ON public.clinic_subscription_audit;
CREATE POLICY clinic_subscription_audit_4layer_select ON public.clinic_subscription_audit
    FOR SELECT
    TO hakudokai_4layer_role
    USING (clinic_id = current_setting('app.current_clinic_id', true));

-- service_role: Phase A 互換のため全 clinic 参照可 (Phase B 切替後 revoke)
DROP POLICY IF EXISTS clinic_subscription_audit_service_full ON public.clinic_subscription_audit;
CREATE POLICY clinic_subscription_audit_service_full ON public.clinic_subscription_audit
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- (4) 既存 clinic_master row の backfill (migrations/001 で 7 医院 INSERT 済み)
-- ============================================================
-- migrations/001 適用後にこの migration を apply する場合、既存 7 row 分の audit を backfill
-- ON CONFLICT 不要 (audit table の id は新規 uuid 生成)
INSERT INTO public.clinic_subscription_audit (
    clinic_id, tier_before, tier_after, changed_at, source
)
SELECT
    cm.clinic_id, NULL, cm.subscription_tier, cm.created_at, 'backfill_migration_004'
FROM public.clinic_master cm
WHERE NOT EXISTS (
    SELECT 1 FROM public.clinic_subscription_audit a
    WHERE a.clinic_id = cm.clinic_id
);

COMMIT;

-- ============================================================
-- rollback: 失敗時は逆順実行
-- ============================================================
-- BEGIN;
-- DROP POLICY IF EXISTS clinic_subscription_audit_service_full ON public.clinic_subscription_audit;
-- DROP POLICY IF EXISTS clinic_subscription_audit_4layer_select ON public.clinic_subscription_audit;
-- ALTER TABLE public.clinic_subscription_audit DISABLE ROW LEVEL SECURITY;
-- DROP TRIGGER IF EXISTS clinic_master_subscription_audit ON public.clinic_master;
-- DROP FUNCTION IF EXISTS public.clinic_subscription_audit_log();
-- DROP INDEX IF EXISTS public.clinic_subscription_audit_changed_at_idx;
-- DROP INDEX IF EXISTS public.clinic_subscription_audit_clinic_idx;
-- DROP TABLE IF EXISTS public.clinic_subscription_audit;
-- COMMIT;
