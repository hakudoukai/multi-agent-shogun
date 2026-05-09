-- migrations/006_phase_c2_patient_app.sql
-- Phase C-2: 患者アプリ DD-041 §1-§5 (PWA + 歯式 tap + AIチャット + 通知 + 予約連携) sandbox
--
-- 背景: DD-041 (id=53fd9943, active) §1-§5。
--   §6/§7 は Phase C-1 で実装済 (高速会計 + paylight)、本 migration は §1-§5。
--   理事長 verbatim「次の作業を与えて」 + 副医院長 99a84dd7 GO。
--   DD-054 第3層 (患者接点・会計待ちゼロ) 完成 = 柱 4 (患者アプリ+AIチャット) と柱 7 (リアルタイム会計、Phase C-1) 連動。
--
-- 適用前確認:
--   - 理事長承認 (grant_permission handshake、🔴 7 新規 table)
--   - 副医院長 strategic 適合判定
--   - 山ちゃん 法令適合審査 (個人情報保護法 + AIチャット診断禁止 keyword filter 設計確認)
--   - Codex+Gemini dual 🟢 監査
--   - patient_master / clinic_master との外部キー整合 (本 migration では FK は緩く、運用後 ALTER で追加可)
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- ============================================================
-- (1) patient_app_session — 患者ログイン session
-- ============================================================
CREATE TABLE IF NOT EXISTS public.patient_app_session (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    patient_id      uuid          NOT NULL,
    session_token   text          NOT NULL,
    device_kind     text          NULL
        CHECK (device_kind IS NULL OR device_kind IN ('pwa_web','ios','android','line_liff')),
    created_at      timestamptz   NOT NULL DEFAULT now(),
    expires_at      timestamptz   NULL,
    revoked_at      timestamptz   NULL,

    CONSTRAINT patient_app_session_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT patient_app_session_token_uniq UNIQUE (session_token)
);

CREATE INDEX IF NOT EXISTS patient_app_session_patient_idx
    ON public.patient_app_session (clinic_id, patient_id, created_at DESC);

-- ============================================================
-- (2) patient_app_view_log — 歯式部位 tap / 画面閲覧ログ
-- ============================================================
CREATE TABLE IF NOT EXISTS public.patient_app_view_log (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    patient_id      uuid          NOT NULL,
    session_id      uuid          NULL,
    view_kind       text          NOT NULL DEFAULT 'tooth_tap'
        CHECK (view_kind IN ('tooth_tap','treatment_options','comparison_table','image_view','plan_review','other')),
    tooth_no        text          NULL,         -- FDI 番号 or 内部表記
    treatment_plan_item_id uuid   NULL,         -- DD-040 treatment_plan_items 参照 (本 migration では FK 緩い)
    payload         jsonb         NOT NULL DEFAULT '{}'::jsonb,
    viewed_at       timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT patient_view_log_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64)
);

CREATE INDEX IF NOT EXISTS patient_view_log_patient_idx
    ON public.patient_app_view_log (clinic_id, patient_id, viewed_at DESC);

CREATE INDEX IF NOT EXISTS patient_view_log_session_idx
    ON public.patient_app_view_log (session_id);

-- ============================================================
-- (3) patient_chat_log — AIチャット (患者発話)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.patient_chat_log (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    patient_id      uuid          NOT NULL,
    session_id      uuid          NULL,
    chat_thread_id  uuid          NOT NULL DEFAULT gen_random_uuid(),
    sender          text          NOT NULL DEFAULT 'patient'
        CHECK (sender IN ('patient','ai','staff')),
    message_text    text          NOT NULL,
    -- 法令準拠: 診断禁止 / 治療強制禁止 keyword filter 結果
    forbidden_keyword_detected boolean NOT NULL DEFAULT false,
    forbidden_categories       text[]  NOT NULL DEFAULT '{}',
    created_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT patient_chat_log_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64)
);

CREATE INDEX IF NOT EXISTS patient_chat_log_thread_idx
    ON public.patient_chat_log (clinic_id, chat_thread_id, created_at);

CREATE INDEX IF NOT EXISTS patient_chat_log_patient_idx
    ON public.patient_chat_log (clinic_id, patient_id, created_at DESC);

-- ============================================================
-- (4) patient_chat_response — AI 応答 (法令フィルター + 蜘蛛の糸 連携)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.patient_chat_response (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    chat_log_id     uuid          NOT NULL,
    response_text   text          NOT NULL,
    -- 診断禁止 / 治療強制禁止 keyword filter 結果 (AI 出力側、§3 法令準拠)
    diagnosis_phrase_replaced  boolean NOT NULL DEFAULT false,
    treatment_force_replaced   boolean NOT NULL DEFAULT false,
    crm_referenced             boolean NOT NULL DEFAULT false,
    spider_thread_pushed       boolean NOT NULL DEFAULT false,  -- DD-020 蜘蛛の糸 連携
    model_id        text          NULL,
    tokens_used     integer       NULL,
    created_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT patient_chat_response_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT patient_chat_response_chat_log_uniq UNIQUE (chat_log_id),
    CONSTRAINT fk_patient_chat_response_log
        FOREIGN KEY (chat_log_id) REFERENCES public.patient_chat_log(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS patient_chat_response_clinic_idx
    ON public.patient_chat_response (clinic_id, created_at DESC);

-- ============================================================
-- (5) patient_notification_log — メール/SMS/LINE 配信ログ (DD-044 連動)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.patient_notification_log (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    patient_id      uuid          NOT NULL,
    channel         text          NOT NULL
        CHECK (channel IN ('email','sms','line','push','app_inbox')),
    purpose         text          NOT NULL DEFAULT 'general'
        CHECK (purpose IN ('general','reminder','receipt','payment_request','recall','treatment_explanation')),
    -- 患者個人情報を直書きしない: subject / body は redacted_template_key + variables (jsonb) 経由で生成
    template_key    text          NOT NULL,
    -- Codex audit C-2-6 #1 修正: variables jsonb で patient_id/uuid 等の masked 値を永続化
    -- DD-044 連携で報告書 PDF 配信時の report_id 等を保持、後段 service が template_key + variables から
    -- subject/body を組立て (PII guard 範囲内)
    variables       jsonb         NOT NULL DEFAULT '{}'::jsonb,
    delivered_at    timestamptz   NULL,
    delivery_status text          NOT NULL DEFAULT 'queued'
        CHECK (delivery_status IN ('queued','sent','delivered','failed','bounced')),
    external_id     text          NULL,         -- メール gateway / SMS / LINE provider 側の ID
    -- idempotency: 同 patient × purpose × template × 1h bucket は 1 row のみ
    idempotency_key text          NOT NULL,
    created_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT patient_notification_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT patient_notification_idem_uniq UNIQUE (clinic_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS patient_notification_patient_idx
    ON public.patient_notification_log (clinic_id, patient_id, created_at DESC);

CREATE INDEX IF NOT EXISTS patient_notification_channel_idx
    ON public.patient_notification_log (clinic_id, channel, delivery_status);

-- ============================================================
-- (6) patient_app_settings — 患者個別設定 (通知 opt-in 等)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.patient_app_settings (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    patient_id      uuid          NOT NULL,
    notify_email    boolean       NOT NULL DEFAULT true,
    notify_sms      boolean       NOT NULL DEFAULT true,
    notify_line     boolean       NOT NULL DEFAULT false,
    notify_push     boolean       NOT NULL DEFAULT true,
    chat_enabled    boolean       NOT NULL DEFAULT true,
    locale          text          NOT NULL DEFAULT 'ja-JP',
    created_at      timestamptz   NOT NULL DEFAULT now(),
    updated_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT patient_app_settings_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT patient_app_settings_clinic_patient_uniq UNIQUE (clinic_id, patient_id)
);

-- ============================================================
-- (7) clinic_app_branding — 院別ブランディング (PWA UI、院ロゴ等)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.clinic_app_branding (
    clinic_id       text          PRIMARY KEY,
    app_title       text          NOT NULL DEFAULT 'My DentalBI',
    primary_color   text          NULL,
    accent_color    text          NULL,
    logo_url        text          NULL,
    chat_greeting   text          NULL,
    created_at      timestamptz   NOT NULL DEFAULT now(),
    updated_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT clinic_app_branding_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64)
);

-- ============================================================
-- updated_at trigger (共通 function)
-- ============================================================
CREATE OR REPLACE FUNCTION public.patient_app_set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS patient_app_settings_set_updated_at ON public.patient_app_settings;
CREATE TRIGGER patient_app_settings_set_updated_at
    BEFORE UPDATE ON public.patient_app_settings
    FOR EACH ROW EXECUTE FUNCTION public.patient_app_set_updated_at();

DROP TRIGGER IF EXISTS clinic_app_branding_set_updated_at ON public.clinic_app_branding;
CREATE TRIGGER clinic_app_branding_set_updated_at
    BEFORE UPDATE ON public.clinic_app_branding
    FOR EACH ROW EXECUTE FUNCTION public.patient_app_set_updated_at();

-- ============================================================
-- Phase C-2 全体設計やり直し (FKI-DEV-ROOT-CURE-FIRST-01):
-- patient_id boundary trigger (chat thread per-patient 隔離)
-- ============================================================
-- chat_log/chat_response/view_log/notification_log 等の patient 系 child table で
-- session_id が指定されている場合に session の patient_id と一致するか物理保証.
-- session_id NULL の場合 (内部 batch INSERT 等) は trigger スキップ.
CREATE OR REPLACE FUNCTION public.t_check_patient_session_match()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_session_patient uuid;
    v_session_clinic text;
    v_session_revoked timestamptz;
    v_session_expires timestamptz;
BEGIN
    -- session_id 不在時は skip (Phase A 内部呼出許容、Phase B で session_id 必須化検討)
    IF NEW.session_id IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT patient_id, clinic_id, revoked_at, expires_at
      INTO v_session_patient, v_session_clinic, v_session_revoked, v_session_expires
      FROM public.patient_app_session
     WHERE id = NEW.session_id;
    IF v_session_patient IS NULL THEN
        RAISE EXCEPTION 'patient_app_session not found (session_id=%)', NEW.session_id
            USING ERRCODE = 'P0002';
    END IF;
    IF v_session_patient <> NEW.patient_id THEN
        RAISE EXCEPTION
            'session/patient mismatch: session.patient_id=% NEW.patient_id=% (session_id=%)',
            v_session_patient, NEW.patient_id, NEW.session_id
            USING ERRCODE = 'P0001';
    END IF;
    IF v_session_clinic <> NEW.clinic_id THEN
        RAISE EXCEPTION
            'session/clinic mismatch: session.clinic_id=% NEW.clinic_id=% (session_id=%)',
            v_session_clinic, NEW.clinic_id, NEW.session_id
            USING ERRCODE = 'P0001';
    END IF;
    IF v_session_revoked IS NOT NULL THEN
        RAISE EXCEPTION 'patient_app_session revoked (session_id=%, revoked_at=%)',
            NEW.session_id, v_session_revoked
            USING ERRCODE = 'P0001';
    END IF;
    IF v_session_expires IS NOT NULL AND v_session_expires < now() THEN
        RAISE EXCEPTION 'patient_app_session expired (session_id=%, expires_at=%)',
            NEW.session_id, v_session_expires
            USING ERRCODE = 'P0001';
    END IF;
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.t_check_patient_session_match IS
    'Phase C-2 全体設計やり直し: session_id が指定された場合に session/patient/clinic 一致を物理保証';

-- session_id を持つ child table に trigger 適用
DO $$
DECLARE
    t text;
    child_tables text[] := ARRAY[
        'patient_app_view_log',
        'patient_chat_log'
    ];
BEGIN
    FOREACH t IN ARRAY child_tables LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I_session_match_check ON public.%I', t, t);
        EXECUTE format($f$
            CREATE TRIGGER %I_session_match_check
                BEFORE INSERT OR UPDATE OF session_id, patient_id, clinic_id ON public.%I
                FOR EACH ROW EXECUTE FUNCTION public.t_check_patient_session_match()
        $f$, t, t);
    END LOOP;
END $$;

-- ============================================================
-- RLS 適用 (全 7 table)
-- ============================================================
DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'patient_app_session',
        'patient_app_view_log',
        'patient_chat_log',
        'patient_chat_response',
        'patient_notification_log',
        'patient_app_settings',
        'clinic_app_branding'
    ];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS %I_4layer_clinic ON public.%I', t, t);
        EXECUTE format($f$
            CREATE POLICY %I_4layer_clinic ON public.%I
                FOR ALL TO hakudokai_4layer_role
                USING (clinic_id = current_setting('app.current_clinic_id', true))
                WITH CHECK (clinic_id = current_setting('app.current_clinic_id', true))
        $f$, t, t);
        EXECUTE format('DROP POLICY IF EXISTS %I_service_full ON public.%I', t, t);
        EXECUTE format($f$
            CREATE POLICY %I_service_full ON public.%I
                FOR ALL TO service_role
                USING (true) WITH CHECK (true)
        $f$, t, t);
    END LOOP;
END $$;

COMMIT;

-- ============================================================
-- rollback: 失敗時は逆順実行
-- ============================================================
-- BEGIN;
-- DO $$
-- DECLARE
--     t text;
--     tables text[] := ARRAY[
--         'clinic_app_branding','patient_app_settings','patient_notification_log',
--         'patient_chat_response','patient_chat_log','patient_app_view_log','patient_app_session'
--     ];
-- BEGIN
--     FOREACH t IN ARRAY tables LOOP
--         EXECUTE format('DROP POLICY IF EXISTS %I_service_full ON public.%I', t, t);
--         EXECUTE format('DROP POLICY IF EXISTS %I_4layer_clinic ON public.%I', t, t);
--         EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY', t);
--     END LOOP;
-- END $$;
-- DROP TRIGGER IF EXISTS clinic_app_branding_set_updated_at ON public.clinic_app_branding;
-- DROP TRIGGER IF EXISTS patient_app_settings_set_updated_at ON public.patient_app_settings;
-- DROP FUNCTION IF EXISTS public.patient_app_set_updated_at();
-- DROP TABLE IF EXISTS public.clinic_app_branding CASCADE;
-- DROP TABLE IF EXISTS public.patient_app_settings CASCADE;
-- DROP TABLE IF EXISTS public.patient_notification_log CASCADE;
-- DROP TABLE IF EXISTS public.patient_chat_response CASCADE;
-- DROP TABLE IF EXISTS public.patient_chat_log CASCADE;
-- DROP TABLE IF EXISTS public.patient_app_view_log CASCADE;
-- DROP TABLE IF EXISTS public.patient_app_session CASCADE;
-- COMMIT;
