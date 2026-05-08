-- migrations/007_organizational_lessons.sql
-- cmd_organizational_lessons_supabase_001 — Supabase organizational_lessons table 設計 + RLS
--
-- 背景:
--   信長殿大命 cmd_root_resolution_001 (= 草案 docs/cmd_root_resolution_001_draft.md) 並走
--   3 本柱の 1 本。本朝事故 9 件 + 過去事故含む 組織改革事例の永続蓄積データレイヤー。
--   本多 retrospective audit (cmd_phase16_3_honda_initial_audit_001) の出力先 + 全
--   retrospective audit 出力先 + 95% target 戦略の中核データレイヤー、自走 + 自己進化体制基盤。
--
-- 設計方針 (信長殿明示):
--   - column: id, incident_date, category, root_cause, resolution, skill_impact,
--             lessons, tags
--   - RLS:
--       全 read 可 (= 学習 + retrospective 用)
--       書込 (INSERT/UPDATE) は honda / hideyoshi / shogun のみ
--       DELETE は理事長殿 (rijicho) のみ (= 事例消失防止)
--   - audit_log table 連動: 全 INSERT/UPDATE/DELETE を organizational_lessons_audit へ trigger 自動記録
--
-- agent identity 識別 mechanism:
--   - PostgreSQL GUC (current_setting('app.current_agent', true)) を採用
--   - application 層で `SET LOCAL app.current_agent = '<agent_id>'` を transaction 開始時に発行
--   - service_role bypass あり (= migration apply 時 / 緊急時の rescue)
--
-- 適用前確認:
--   - 理事長承認 (= 信長殿大命 cmd_root_resolution_001 配下の 1 本)
--   - 三者監査 (家康 self-audit + Codex 6軸 + Gemini 8観点)
--   - 既存 migration 001-006 apply 後 (= shim/migrations/ chain)
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- ============================================================
-- (1) organizational_lessons — 組織改革事例蓄積 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.organizational_lessons (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_date   timestamptz   NOT NULL,
    category        text          NULL
        CHECK (category IS NULL OR category IN (
            'routing',
            'pane_drift',
            'token_limit',
            'watcher_silent_death',
            'misroute',
            'cleanup',
            'autonomy',
            'self_audit',
            'regime_change',
            'section18_lockin',
            'skill_violation',
            'consumption_anomaly',
            'split_brain',
            'misidentification',
            'other'
        )),
    root_cause      text          NOT NULL,
    resolution      text          NULL,
    skill_impact    text          NULL,
    lessons         text          NOT NULL,
    tags            text[]        NOT NULL DEFAULT ARRAY[]::text[],
    created_at      timestamptz   NOT NULL DEFAULT now(),
    updated_at      timestamptz   NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS organizational_lessons_incident_date_idx
    ON public.organizational_lessons (incident_date DESC);

CREATE INDEX IF NOT EXISTS organizational_lessons_category_idx
    ON public.organizational_lessons (category);

CREATE INDEX IF NOT EXISTS organizational_lessons_tags_gin_idx
    ON public.organizational_lessons USING GIN (tags);

COMMENT ON TABLE public.organizational_lessons IS
    '組織改革事例蓄積 (cmd_organizational_lessons_supabase_001 / cmd_root_resolution_001 並走 3 本柱の 1 本、本多 retrospective audit 出力先)';

COMMENT ON COLUMN public.organizational_lessons.skill_impact IS
    '§19 skill との関連 (新規 / 拡張 / archive 候補)';

-- ============================================================
-- (2) organizational_lessons_audit — 全 INSERT / UPDATE / DELETE 監査
-- ============================================================
CREATE TABLE IF NOT EXISTS public.organizational_lessons_audit (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id       uuid          NOT NULL,
    operation       text          NOT NULL
        CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    performed_by    text          NULL,
    performed_at    timestamptz   NOT NULL DEFAULT now(),
    before_state    jsonb         NULL,
    after_state     jsonb         NULL,
    -- 注: lesson_id 側の DELETE 後に audit が残せるよう FK は張らず、application 層整合
    CONSTRAINT organizational_lessons_audit_pb_format
        CHECK (performed_by IS NULL OR (performed_by ~ '^[a-z0-9_]+$' AND char_length(performed_by) BETWEEN 2 AND 64))
);

CREATE INDEX IF NOT EXISTS organizational_lessons_audit_lesson_idx
    ON public.organizational_lessons_audit (lesson_id, performed_at DESC);

CREATE INDEX IF NOT EXISTS organizational_lessons_audit_at_idx
    ON public.organizational_lessons_audit (performed_at DESC);

COMMENT ON TABLE public.organizational_lessons_audit IS
    'organizational_lessons の全 INSERT / UPDATE / DELETE 監査ログ (trigger 自動記録)';

-- ============================================================
-- (3) updated_at 自動更新 trigger
-- ============================================================
CREATE OR REPLACE FUNCTION public.organizational_lessons_set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS organizational_lessons_updated_at ON public.organizational_lessons;
CREATE TRIGGER organizational_lessons_updated_at
    BEFORE UPDATE ON public.organizational_lessons
    FOR EACH ROW EXECUTE FUNCTION public.organizational_lessons_set_updated_at();

-- ============================================================
-- (4) audit trigger (= INSERT / UPDATE / DELETE 全捕捉)
--     SECURITY DEFINER: authenticated 経由で organizational_lessons を変更した場合でも
--                       trigger は migration owner (postgres / supabase_admin 相当) の
--                       elevated 権限で audit table へ INSERT する (= authenticated 直接の
--                       audit INSERT policy 不要、改竄不能を担保)。
--     SET search_path: SECURITY DEFINER と組合せた典型的な search_path 注入対策。
--                       public + pg_temp に固定し、temp schema 経由の関数偽装を遮断。
-- ============================================================
CREATE OR REPLACE FUNCTION public.organizational_lessons_audit_log()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_agent text := current_setting('app.current_agent', true);
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO public.organizational_lessons_audit (
            lesson_id, operation, performed_by, after_state
        ) VALUES (
            NEW.id, 'INSERT', v_agent, to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO public.organizational_lessons_audit (
            lesson_id, operation, performed_by, before_state, after_state
        ) VALUES (
            NEW.id, 'UPDATE', v_agent, to_jsonb(OLD), to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO public.organizational_lessons_audit (
            lesson_id, operation, performed_by, before_state
        ) VALUES (
            OLD.id, 'DELETE', v_agent, to_jsonb(OLD)
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

-- 関数 owner は migration 適用 role (= postgres / supabase_admin) のまま固定。
-- 明示的 OWNER TO は環境差分 (Supabase / 自前 PG / pgserver fixture) が大きいため
-- 記載しない (= migration apply 時の current role が owner となる暗黙挙動を採用)。
-- SECURITY DEFINER ゆえ trigger 実行は本 owner 権限で行われる。

-- 注: 関数のセキュリティ境界 — public schema 内の組織監査専用関数のため、引数なし、
-- 副作用は audit table への append-only INSERT に限定。definer 権限濫用 risk なし。

DROP TRIGGER IF EXISTS organizational_lessons_audit_trg ON public.organizational_lessons;
CREATE TRIGGER organizational_lessons_audit_trg
    AFTER INSERT OR UPDATE OR DELETE ON public.organizational_lessons
    FOR EACH ROW EXECUTE FUNCTION public.organizational_lessons_audit_log();

-- ============================================================
-- (5) RLS — organizational_lessons
--     * 全 read 可 (authenticated)
--     * 書込 (INSERT / UPDATE) は honda / hideyoshi / shogun のみ
--     * DELETE は理事長 (rijicho) のみ
--     * service_role は全権 (= 緊急 rescue + migration apply)
-- ============================================================
ALTER TABLE public.organizational_lessons ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS organizational_lessons_read_all ON public.organizational_lessons;
CREATE POLICY organizational_lessons_read_all ON public.organizational_lessons
    FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS organizational_lessons_insert_writers ON public.organizational_lessons;
CREATE POLICY organizational_lessons_insert_writers ON public.organizational_lessons
    FOR INSERT
    TO authenticated
    WITH CHECK (
        current_setting('app.current_agent', true) IN ('honda', 'hideyoshi', 'shogun')
    );

DROP POLICY IF EXISTS organizational_lessons_update_writers ON public.organizational_lessons;
CREATE POLICY organizational_lessons_update_writers ON public.organizational_lessons
    FOR UPDATE
    TO authenticated
    USING (
        current_setting('app.current_agent', true) IN ('honda', 'hideyoshi', 'shogun')
    )
    WITH CHECK (
        current_setting('app.current_agent', true) IN ('honda', 'hideyoshi', 'shogun')
    );

DROP POLICY IF EXISTS organizational_lessons_delete_rijicho ON public.organizational_lessons;
CREATE POLICY organizational_lessons_delete_rijicho ON public.organizational_lessons
    FOR DELETE
    TO authenticated
    USING (
        current_setting('app.current_agent', true) = 'rijicho'
    );

DROP POLICY IF EXISTS organizational_lessons_service_full ON public.organizational_lessons;
CREATE POLICY organizational_lessons_service_full ON public.organizational_lessons
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- (6) RLS — organizational_lessons_audit
--     * 全 read 可 (authenticated)
--     * 書込は trigger 経由のみ (= 直接 INSERT は service_role に限定)
--     * UPDATE / DELETE 不可 (= audit 不変性)
-- ============================================================
ALTER TABLE public.organizational_lessons_audit ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS organizational_lessons_audit_read_all ON public.organizational_lessons_audit;
CREATE POLICY organizational_lessons_audit_read_all ON public.organizational_lessons_audit
    FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS organizational_lessons_audit_service_full ON public.organizational_lessons_audit;
CREATE POLICY organizational_lessons_audit_service_full ON public.organizational_lessons_audit
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- 注: authenticated に対する INSERT は付与しない。
-- trigger 関数 organizational_lessons_audit_log() は SECURITY DEFINER で定義済 (= (4) 参照)
-- ゆえ、authenticated が organizational_lessons を変更した際の audit INSERT は migration
-- owner (= elevated) 権限で実行され、authenticated 直接の audit INSERT 権限は不要。
-- UPDATE / DELETE policy も付与しない = authenticated は audit row を改竄不可。

COMMIT;

-- ============================================================
-- 動作確認 SQL (= apply 後の検証用、参考)
-- ============================================================
-- SELECT to_regclass('public.organizational_lessons');                  -- 期待: organizational_lessons
-- SELECT to_regclass('public.organizational_lessons_audit');            -- 期待: organizational_lessons_audit
-- SELECT polname FROM pg_policy
--   WHERE polrelid = 'public.organizational_lessons'::regclass;         -- 期待: 5 policy
-- SELECT polname FROM pg_policy
--   WHERE polrelid = 'public.organizational_lessons_audit'::regclass;   -- 期待: 2 policy
-- SET LOCAL app.current_agent = 'honda';
-- INSERT INTO public.organizational_lessons (incident_date, category, root_cause, lessons, tags)
--   VALUES (now(), 'routing', 'test root cause', 'test lesson', ARRAY['test']);
-- SELECT count(*) FROM public.organizational_lessons_audit;             -- 期待: 1 件以上
