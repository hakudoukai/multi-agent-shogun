-- migrations/005_phase_c1_daily_report.sql
-- Phase C-1: DD-042 リアルタイム会計 + 日計表 13 テーブル sandbox
--
-- 背景: DD-042 (id=497b8630, active) + DD-041 §6 高速会計 + DD-041 §7 paylight 連携
--   理事長 verbatim「Phase C-1 へ専念」 (handshake 868ea2b1)。
--   会計待ち時間ゼロ実現 = 博道会 DX 戦略 3 年 30 億円目標達成基盤。
--
-- 適用前確認:
--   - 理事長承認 (grant_permission handshake、🔴 新規 13 テーブル + 4 マスタ)
--   - 副医院長 strategic 適合判定
--   - 山ちゃん 法令適合審査 (個人情報保護法 + 医療情報安全管理 + 領収書交付義務)
--   - Codex+Gemini dual 🟢 監査
--   - 既存 patient_master / clinic_master (migrations/001) との外部キー整合
--
-- 設計:
--   - 全テーブルに clinic_id (multi-tenant boundary) + RLS
--   - daily_report (ヘッダ・集計) → 子テーブル (患者別/雑収入/自費/受入/支払/未収/過収/交際費)
--   - マスタ 4 (product / self_pay / payee / income_source) は院別管理
--   - paylight 連携用 billing_records (DD-044 派生) は別 migration (006) で扱う、本 migration は range 内のみ
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- ============================================================
-- (1) daily_report (ヘッダ・集計・統計)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report (
    id                       uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id                text          NOT NULL,
    report_date              date          NOT NULL,
    status                   text          NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'finalized', 'archived')),

    -- 集計値 (DD-042「計算」セクション)
    prev_day_balance         numeric(12,2) NOT NULL DEFAULT 0,
    insurance_income         numeric(12,2) NOT NULL DEFAULT 0,
    entertainment_total      numeric(12,2) NOT NULL DEFAULT 0,
    uncollected_total        numeric(12,2) NOT NULL DEFAULT 0,
    self_pay_total           numeric(12,2) NOT NULL DEFAULT 0,
    misc_income_total        numeric(12,2) NOT NULL DEFAULT 0,
    payments_total           numeric(12,2) NOT NULL DEFAULT 0,
    income_total             numeric(12,2) NOT NULL DEFAULT 0,
    transferred_to_director  numeric(12,2) NOT NULL DEFAULT 0,
    misc_discount_total      numeric(12,2) NOT NULL DEFAULT 0,
    unidentified_amount      numeric(12,2) NOT NULL DEFAULT 0,
    end_of_day_balance       numeric(12,2) NOT NULL DEFAULT 0,
    total_points             integer       NOT NULL DEFAULT 0,
    insurance_income_total   numeric(12,2) NOT NULL DEFAULT 0,
    app_payment_received     numeric(12,2) NOT NULL DEFAULT 0,  -- DD-044 派生
    -- audit-fix(phase-c1) Critical #1 (L1-A): 明細→ヘッダ集計用 patient_count
    patient_count            integer       NOT NULL DEFAULT 0,

    -- 統計 (DD-042「統計」セクション)
    new_patients             integer       NOT NULL DEFAULT 0,
    re_initial               integer       NOT NULL DEFAULT 0,
    appointments             integer       NOT NULL DEFAULT 0,
    cancellations            integer       NOT NULL DEFAULT 0,
    recalls                  integer       NOT NULL DEFAULT 0,

    finalized_at             timestamptz   NULL,
    finalized_by             text          NULL,
    created_at               timestamptz   NOT NULL DEFAULT now(),
    updated_at               timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT daily_report_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT daily_report_clinic_date_uniq UNIQUE (clinic_id, report_date),
    -- audit-fix(phase-c1) Major (L1-D): composite FK 用 UNIQUE (id, clinic_id)
    -- 親子の clinic_id 一致を物理保証、院またぎデータ汚染防止
    CONSTRAINT daily_report_id_clinic_uniq UNIQUE (id, clinic_id)
);

CREATE INDEX IF NOT EXISTS daily_report_clinic_date_idx
    ON public.daily_report (clinic_id, report_date DESC);

-- ============================================================
-- (2) daily_report_patients (患者別明細)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_patients (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    seq_no              integer       NOT NULL,
    column_side         text          NOT NULL DEFAULT 'left'
        CHECK (column_side IN ('left', 'right')),
    patient_id          uuid          NULL,    -- patient_master 参照、PII guard のため直書き禁止
    points              integer       NOT NULL DEFAULT 0,
    request_amount      numeric(12,2) NOT NULL DEFAULT 0,
    received_amount     numeric(12,2) NOT NULL DEFAULT 0,
    credit_amount       numeric(12,2) NOT NULL DEFAULT 0,
    payment_method      text          NOT NULL DEFAULT 'cash'
        CHECK (payment_method IN ('cash','credit','app','fast_payment','partial','uncollected')),
    fast_payment_status text          NULL
        CHECK (fast_payment_status IS NULL OR fast_payment_status IN ('pending','finalized','adjusted')),
    paylight_txn_id     text          NULL,    -- DD-041 §7
    notes               text          NULL,
    created_at          timestamptz   NOT NULL DEFAULT now(),
    updated_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT daily_report_patients_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_daily_report_patients_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS daily_report_patients_report_idx
    ON public.daily_report_patients (daily_report_id, column_side, seq_no);

-- Codex audit C-1-6 #1 修正: 高速会計の重複計上防止 (clinic_id, daily_report_id, patient_id, payment_method='fast_payment')
-- partial UNIQUE で fast_payment 行のみ 1 患者 1 日 1 行に限定
CREATE UNIQUE INDEX IF NOT EXISTS daily_report_patients_fast_payment_uidx
    ON public.daily_report_patients (clinic_id, daily_report_id, patient_id)
    WHERE payment_method = 'fast_payment' AND patient_id IS NOT NULL;

-- Codex audit C-1-6 #2 修正: paylight 重複計上防止 (paylight_txn_id NULL 許容、非 NULL 時 UNIQUE)
CREATE UNIQUE INDEX IF NOT EXISTS daily_report_patients_paylight_txn_uidx
    ON public.daily_report_patients (paylight_txn_id)
    WHERE paylight_txn_id IS NOT NULL;

-- audit-fix(phase-c1) Loop 5 修正 (Codex Loop 4 Critical #2): seq_no UNIQUE index 追加
-- paylight retry が seq_uidx 23505 衝突を前提に再採番するため、UNIQUE 制約必須
-- 同一 daily_report_id + column_side 内で seq_no 一意性保証
CREATE UNIQUE INDEX IF NOT EXISTS daily_report_patients_seq_uidx
    ON public.daily_report_patients (daily_report_id, column_side, seq_no);

-- ============================================================
-- Phase C-1 全体設計やり直し (FKI-DEV-ROOT-CURE-FIRST-01 priority=120):
-- 親子 clinic_id 同一性 trigger function 定義
-- (実 trigger 付与は migration 末尾、全 child table 作成後)
-- ============================================================
-- 副医院長 56cf5934 命令 #4: daily_report_patients.clinic_id = daily_report.clinic_id を物理保証
-- composite FK は (daily_report_id, clinic_id) → daily_report(id, clinic_id) で既に整合保証あり
-- (3f515e8 で導入済) だが、明示的な BEFORE INSERT/UPDATE trigger で二重防御.
CREATE OR REPLACE FUNCTION public.t_check_daily_report_clinic_match()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_parent_clinic text;
BEGIN
    SELECT clinic_id INTO v_parent_clinic
    FROM public.daily_report
    WHERE id = NEW.daily_report_id;
    IF v_parent_clinic IS NULL THEN
        RAISE EXCEPTION
            'parent daily_report not found (daily_report_id=%)', NEW.daily_report_id
            USING ERRCODE = 'P0002';
    END IF;
    IF v_parent_clinic <> NEW.clinic_id THEN
        RAISE EXCEPTION
            'clinic_id mismatch: child=% parent=% (daily_report_id=%)',
            NEW.clinic_id, v_parent_clinic, NEW.daily_report_id
            USING ERRCODE = 'P0001';
    END IF;
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.t_check_daily_report_clinic_match IS
    'Phase C-1 全体設計やり直し: 親子 clinic_id 同一性物理保証 trigger function';

-- ============================================================
-- (3) product_master (物販品マスタ)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.product_master (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    product_code    text          NOT NULL,
    product_name    text          NOT NULL,
    unit_price      numeric(12,2) NOT NULL DEFAULT 0,
    active          boolean       NOT NULL DEFAULT true,
    created_at      timestamptz   NOT NULL DEFAULT now(),
    updated_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT product_master_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT product_master_clinic_code_uniq UNIQUE (clinic_id, product_code)
);

-- ============================================================
-- (4) daily_report_misc_income (雑収入明細)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_misc_income (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    seq_no              integer       NOT NULL,
    product_id          uuid          NULL,
    product_code        text          NULL,
    product_name        text          NOT NULL,
    quantity            integer       NOT NULL DEFAULT 1,
    misc_income         numeric(12,2) NOT NULL DEFAULT 0,
    discount            numeric(12,2) NOT NULL DEFAULT 0,
    created_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT misc_income_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_misc_income_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS misc_income_report_idx
    ON public.daily_report_misc_income (daily_report_id, seq_no);

-- ============================================================
-- (5) self_pay_master (自費項目マスタ)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.self_pay_master (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    item_code       text          NOT NULL,
    item_name       text          NOT NULL,
    standard_price  numeric(12,2) NOT NULL DEFAULT 0,
    active          boolean       NOT NULL DEFAULT true,
    created_at      timestamptz   NOT NULL DEFAULT now(),
    updated_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT self_pay_master_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT self_pay_master_clinic_code_uniq UNIQUE (clinic_id, item_code)
);

-- ============================================================
-- (6) daily_report_self_pay (自費領収明細)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_self_pay (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    receipt_no          text          NULL,
    patient_id          uuid          NULL,
    item_id             uuid          NULL,
    item_detail         text          NULL,
    received_amount     numeric(12,2) NOT NULL DEFAULT 0,
    created_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT self_pay_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_self_pay_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS self_pay_report_idx
    ON public.daily_report_self_pay (daily_report_id);

-- ============================================================
-- (7) income_source_master (受入先マスタ)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.income_source_master (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    source_code     text          NOT NULL,
    source_name     text          NOT NULL,
    active          boolean       NOT NULL DEFAULT true,
    created_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT income_source_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT income_source_clinic_code_uniq UNIQUE (clinic_id, source_code)
);

-- ============================================================
-- (8) daily_report_income (受入明細)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_income (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    source_id           uuid          NULL,
    source_name         text          NULL,
    received_amount     numeric(12,2) NOT NULL DEFAULT 0,
    notes               text          NULL,
    created_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT income_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_income_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

-- ============================================================
-- (9) payee_master (支払先マスタ)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.payee_master (
    id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id       text          NOT NULL,
    payee_code      text          NOT NULL,
    payee_name      text          NOT NULL,
    payee_type      text          NOT NULL DEFAULT 'other'
        CHECK (payee_type IN ('bank','technician','vendor','tax','salary','other')),
    active          boolean       NOT NULL DEFAULT true,
    created_at      timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT payee_master_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT payee_master_clinic_code_uniq UNIQUE (clinic_id, payee_code)
);

-- ============================================================
-- (10) daily_report_payments (支払明細)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_payments (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    payee_id            uuid          NULL,
    payee_name          text          NULL,
    payment_amount      numeric(12,2) NOT NULL DEFAULT 0,
    notes               text          NULL,
    created_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT payments_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_payments_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

-- ============================================================
-- (11) daily_report_uncollected (未収金)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_uncollected (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    management_no       text          NULL,
    patient_id          uuid          NULL,
    prev_day_amount     numeric(12,2) NOT NULL DEFAULT 0,
    current_amount      numeric(12,2) NOT NULL DEFAULT 0,
    notes               text          NULL,
    created_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT uncollected_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_uncollected_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

-- ============================================================
-- (12) daily_report_overcollected (過収金)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_overcollected (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    management_no       text          NULL,
    patient_id          uuid          NULL,
    over_amount         numeric(12,2) NOT NULL DEFAULT 0,
    notes               text          NULL,
    created_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT overcollected_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_overcollected_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

-- ============================================================
-- (13) daily_report_entertainment (交際費)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.daily_report_entertainment (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_report_id     uuid          NOT NULL,
    clinic_id           text          NOT NULL,
    management_no       text          NULL,
    patient_id          uuid          NULL,
    entertainment_amount numeric(12,2) NOT NULL DEFAULT 0,
    notes               text          NULL,
    created_at          timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT entertainment_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64),
    CONSTRAINT fk_entertainment_report
        -- audit-fix(phase-c1) Major (L1-D): composite FK で親子 clinic_id 一致を物理保証
        FOREIGN KEY (daily_report_id, clinic_id) REFERENCES public.daily_report(id, clinic_id) ON DELETE CASCADE
);

-- ============================================================
-- (14) clinic_payment_settings (院別決済設定 + 高速会計設定 + paylight 連携)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.clinic_payment_settings (
    id                          uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id                   text          NOT NULL UNIQUE,

    -- DD-041 §6 高速会計
    fast_payment_enabled        boolean       NOT NULL DEFAULT true,
    fast_payment_subsidy_region text          NULL,        -- 例: '福岡市'
    fast_payment_age_max        integer       NULL,        -- 例: 15
    fast_payment_fixed_amount   numeric(12,2) NULL,        -- 例: 500.00

    -- DD-041 §7 paylight
    paylight_enabled            boolean       NOT NULL DEFAULT false,
    paylight_merchant_id        text          NULL,
    paylight_fee_rate           numeric(6,4)  NOT NULL DEFAULT 0.0105,  -- 1.05%
    paylight_endpoint           text          NULL,

    created_at                  timestamptz   NOT NULL DEFAULT now(),
    updated_at                  timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT clinic_payment_settings_clinic_id_format
        CHECK (clinic_id ~ '^[a-z0-9_]+$' AND char_length(clinic_id) BETWEEN 3 AND 64)
);

-- ============================================================
-- updated_at trigger (共通)
-- ============================================================
CREATE OR REPLACE FUNCTION public.daily_report_set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS daily_report_set_updated_at ON public.daily_report;
CREATE TRIGGER daily_report_set_updated_at
    BEFORE UPDATE ON public.daily_report
    FOR EACH ROW EXECUTE FUNCTION public.daily_report_set_updated_at();

-- ============================================================
-- audit-fix(phase-c1) Loop 3: atomic increment RPC (Critical #1 完全根治)
-- read-modify-write による lost update を防止、SQL atomic UPDATE で増分
-- ============================================================
-- カラム参照注:
--   daily_report.insurance_income (line 37) = 当日保険収入 (集計対象列、ai_jimucho が SELECT)
--   daily_report.insurance_income_total (line 49) = 月次保険収入累計 (将来用、Phase A では未使用)
--   本 RPC は insurance_income を更新 (実運用集計列、ai_jimucho と整合)
CREATE OR REPLACE FUNCTION public.rpc_increment_daily_report_header(
    p_daily_report_id uuid,
    p_clinic_id text,
    p_self_pay_delta numeric DEFAULT 0,
    p_insurance_delta numeric DEFAULT 0,
    p_misc_delta numeric DEFAULT 0,
    p_payments_delta numeric DEFAULT 0,
    p_app_payment_delta numeric DEFAULT 0,
    p_patient_delta integer DEFAULT 1,
    p_points_delta integer DEFAULT 0
) RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected integer;
BEGIN
    UPDATE public.daily_report
       SET self_pay_total       = self_pay_total + p_self_pay_delta,
           insurance_income     = insurance_income + p_insurance_delta,
           misc_income_total    = misc_income_total + p_misc_delta,
           payments_total       = payments_total + p_payments_delta,
           app_payment_received = app_payment_received + p_app_payment_delta,
           income_total         = (insurance_income + p_insurance_delta)
                                 + (self_pay_total + p_self_pay_delta)
                                 + (misc_income_total + p_misc_delta)
                                 + (app_payment_received + p_app_payment_delta),
           patient_count        = patient_count + p_patient_delta,
           total_points         = total_points + p_points_delta,
           updated_at           = now()
     WHERE id = p_daily_report_id
       AND clinic_id = p_clinic_id;
    GET DIAGNOSTICS v_affected = ROW_COUNT;
    -- audit-fix(phase-c1) Loop 4 修正 (Codex Loop 3 Critical fail-open):
    -- 0 row HIT は明示的に EXCEPTION raise、caller 側で握り潰し不可とする
    IF v_affected < 1 THEN
        RAISE EXCEPTION
            'rpc_increment_daily_report_header: 0 row hit (daily_report_id=% clinic_id=%)',
            p_daily_report_id, p_clinic_id
            USING ERRCODE = 'P0002';
    END IF;
    RETURN v_affected;
END;
$$;

COMMENT ON FUNCTION public.rpc_increment_daily_report_header IS
    'Phase C-1 atomic header increment (audit-fix Loop 3 Critical #1 lost update 根治)';

-- ============================================================
-- audit-fix(phase-c1) Loop 5: detail INSERT + header 増分 1 transaction 化 RPC
-- (Codex Loop 4 Critical #1 header/detail atomic 化未達 完全根治)
-- ============================================================
CREATE OR REPLACE FUNCTION public.rpc_insert_patient_with_header_increment(
    p_clinic_id text,
    p_daily_report_id uuid,
    p_seq_no integer,
    p_column_side text,
    p_patient_id uuid,
    p_points integer DEFAULT 0,
    p_request_amount numeric DEFAULT 0,
    p_received_amount numeric DEFAULT 0,
    p_credit_amount numeric DEFAULT 0,
    p_payment_method text DEFAULT NULL,
    p_fast_payment_status text DEFAULT NULL,
    p_paylight_txn_id text DEFAULT NULL,
    p_notes text DEFAULT NULL,
    p_self_pay_delta numeric DEFAULT 0,
    p_insurance_delta numeric DEFAULT 0,
    p_misc_delta numeric DEFAULT 0,
    p_payments_delta numeric DEFAULT 0,
    p_app_payment_delta numeric DEFAULT 0,
    p_patient_delta integer DEFAULT 1,
    p_points_delta integer DEFAULT 0
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
    v_inserted_id uuid;
    v_affected integer;
BEGIN
    -- Step 1: detail INSERT (1 transaction 内)
    INSERT INTO public.daily_report_patients (
        daily_report_id, clinic_id, seq_no, column_side, patient_id,
        points, request_amount, received_amount, credit_amount,
        payment_method, fast_payment_status, paylight_txn_id, notes
    ) VALUES (
        p_daily_report_id, p_clinic_id, p_seq_no, p_column_side, p_patient_id,
        p_points, p_request_amount, p_received_amount, p_credit_amount,
        p_payment_method, p_fast_payment_status, p_paylight_txn_id, p_notes
    )
    RETURNING id INTO v_inserted_id;

    -- Step 2: header 増分 (同 transaction 内、失敗時自動 rollback で detail も巻戻り)
    -- Gemini Pass 1 修正: total_points 増分追加 (p_points_delta 引数経由)
    UPDATE public.daily_report
       SET self_pay_total       = self_pay_total + p_self_pay_delta,
           insurance_income     = insurance_income + p_insurance_delta,
           misc_income_total    = misc_income_total + p_misc_delta,
           payments_total       = payments_total + p_payments_delta,
           app_payment_received = app_payment_received + p_app_payment_delta,
           income_total         = (insurance_income + p_insurance_delta)
                                 + (self_pay_total + p_self_pay_delta)
                                 + (misc_income_total + p_misc_delta)
                                 + (app_payment_received + p_app_payment_delta),
           patient_count        = patient_count + p_patient_delta,
           total_points         = total_points + COALESCE(p_points_delta, p_points, 0),
           updated_at           = now()
     WHERE id = p_daily_report_id
       AND clinic_id = p_clinic_id;
    GET DIAGNOSTICS v_affected = ROW_COUNT;
    IF v_affected < 1 THEN
        -- header 更新失敗 → 例外 raise で transaction 全体 rollback (detail も含む)
        RAISE EXCEPTION
            'rpc_insert_patient_with_header_increment: header 0 row hit (daily_report_id=% clinic_id=%)',
            p_daily_report_id, p_clinic_id
            USING ERRCODE = 'P0002';
    END IF;

    RETURN v_inserted_id;
END;
$$;

COMMENT ON FUNCTION public.rpc_insert_patient_with_header_increment IS
    'Phase C-1 atomic INSERT + header increment (audit-fix Loop 5 Critical #1 header/detail 乖離根治、1 transaction 完結)';

DROP TRIGGER IF EXISTS daily_report_patients_set_updated_at ON public.daily_report_patients;
CREATE TRIGGER daily_report_patients_set_updated_at
    BEFORE UPDATE ON public.daily_report_patients
    FOR EACH ROW EXECUTE FUNCTION public.daily_report_set_updated_at();

DROP TRIGGER IF EXISTS clinic_payment_settings_set_updated_at ON public.clinic_payment_settings;
CREATE TRIGGER clinic_payment_settings_set_updated_at
    BEFORE UPDATE ON public.clinic_payment_settings
    FOR EACH ROW EXECUTE FUNCTION public.daily_report_set_updated_at();

DROP TRIGGER IF EXISTS product_master_set_updated_at ON public.product_master;
CREATE TRIGGER product_master_set_updated_at
    BEFORE UPDATE ON public.product_master
    FOR EACH ROW EXECUTE FUNCTION public.daily_report_set_updated_at();

DROP TRIGGER IF EXISTS self_pay_master_set_updated_at ON public.self_pay_master;
CREATE TRIGGER self_pay_master_set_updated_at
    BEFORE UPDATE ON public.self_pay_master
    FOR EACH ROW EXECUTE FUNCTION public.daily_report_set_updated_at();

-- ============================================================
-- RLS 適用 (全 14 テーブル)
-- ============================================================
DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'daily_report',
        'daily_report_patients',
        'daily_report_misc_income',
        'daily_report_self_pay',
        'daily_report_income',
        'daily_report_payments',
        'daily_report_uncollected',
        'daily_report_overcollected',
        'daily_report_entertainment',
        'product_master',
        'self_pay_master',
        'income_source_master',
        'payee_master',
        'clinic_payment_settings'
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

-- ============================================================
-- Phase C-1 全体設計やり直し (FKI-DEV-ROOT-CURE-FIRST-01):
-- 親子 clinic_id 同一性 trigger 付与 (8 child tables、全 CREATE TABLE 完了後)
-- ============================================================
-- Codex Pass 1 修正: trigger 付与位置を migration 末尾へ移動
-- (前位置では daily_report_misc_income 以降の table 未作成で relation-not-found エラー)
DO $$
DECLARE
    t text;
    child_tables text[] := ARRAY[
        'daily_report_patients',
        'daily_report_misc_income',
        'daily_report_self_pay',
        'daily_report_income',
        'daily_report_payments',
        'daily_report_uncollected',
        'daily_report_overcollected',
        'daily_report_entertainment'
    ];
BEGIN
    FOREACH t IN ARRAY child_tables LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I_clinic_match_check ON public.%I', t, t);
        -- Gemini Pass 1 修正: WHEN 句で clinic_id/daily_report_id 変化時のみ発火 (DB オーバーヘッド削減)
        EXECUTE format($f$
            CREATE TRIGGER %I_clinic_match_check
                BEFORE INSERT OR UPDATE OF clinic_id, daily_report_id ON public.%I
                FOR EACH ROW EXECUTE FUNCTION public.t_check_daily_report_clinic_match()
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
--         'clinic_payment_settings','payee_master','income_source_master','self_pay_master','product_master',
--         'daily_report_entertainment','daily_report_overcollected','daily_report_uncollected',
--         'daily_report_payments','daily_report_income','daily_report_self_pay','daily_report_misc_income',
--         'daily_report_patients','daily_report'
--     ];
-- BEGIN
--     FOREACH t IN ARRAY tables LOOP
--         EXECUTE format('DROP POLICY IF EXISTS %I_service_full ON public.%I', t, t);
--         EXECUTE format('DROP POLICY IF EXISTS %I_4layer_clinic ON public.%I', t, t);
--         EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY', t);
--     END LOOP;
-- END $$;
-- DROP TRIGGER IF EXISTS self_pay_master_set_updated_at ON public.self_pay_master;
-- DROP TRIGGER IF EXISTS product_master_set_updated_at ON public.product_master;
-- DROP TRIGGER IF EXISTS clinic_payment_settings_set_updated_at ON public.clinic_payment_settings;
-- DROP TRIGGER IF EXISTS daily_report_patients_set_updated_at ON public.daily_report_patients;
-- DROP TRIGGER IF EXISTS daily_report_set_updated_at ON public.daily_report;
-- DROP FUNCTION IF EXISTS public.daily_report_set_updated_at();
-- DROP TABLE IF EXISTS public.clinic_payment_settings CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_entertainment CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_overcollected CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_uncollected CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_payments CASCADE;
-- DROP TABLE IF EXISTS public.payee_master CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_income CASCADE;
-- DROP TABLE IF EXISTS public.income_source_master CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_self_pay CASCADE;
-- DROP TABLE IF EXISTS public.self_pay_master CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_misc_income CASCADE;
-- DROP TABLE IF EXISTS public.product_master CASCADE;
-- DROP TABLE IF EXISTS public.daily_report_patients CASCADE;
-- DROP TABLE IF EXISTS public.daily_report CASCADE;
-- COMMIT;
