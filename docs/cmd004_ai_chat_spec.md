# cmd_004 機能⑦ 小児患者向け AI チャット 設計 spec

- task_id: subtask_cmd004_ai_chat_spec
- parent_cmd: cmd_004「小児恐竜王国」
- bloom_level: L4
- author: ashigaru5 (鳥居元忠 persona、SecondPC)
- 起案日: 2026-05-11
- 範囲: **spec only**。実装 commit は ANTHROPIC_API_KEY 解消後の別 task。
- base_commit: b66ffe0b (`feat(patient-chat): add load_dotenv + chat_messages persistence`, 2026-05-09 Sat 21:47:40+09:00)
- 連動 spec:
  - `docs/cmd004_guardian_consent_spec.md` (ashigaru4 並行起案、保護者同意 gate の上位 spec)
  - `docs/kids_app_push_ceremony_detail_design.md` (Phase 7 パスポート、dinosaur_kingdom 連動の前提)
  - `queue/reports/ashigaru5_report_supplement_ai_chat_spec.yaml` (2026-05-09 既起案、本 spec の前段資産)

---

## 0. Anti-Duplication: 参照済み正本 / 不参照

| # | 正本 | 所在 | 利用方法 |
|---|------|------|----------|
| A | `backend/services/patient_chat_engine.py` (464 行) | DentalBI 本体 | 既存ロジック、本 spec で kids 拡張点のみ規定 |
| B | `backend/routers/patient_chat.py` (60 行) | DentalBI 本体 | `/api/patient-chat/message`, `/history/{patient_id}` を kids でも共用 (router 分岐不要) |
| C | `patient_chat_messages` table (Supabase project `pxvnhkiqyxkejzivspde`) | migration applied 2026-05-09 | RLS policy 未追加、本 spec §4 で起案 |
| D | `form_templates` (25 件、`is_current=true`) | 既存 | `_KEYWORD_FORM_MAP` で参照、kids 向けキーワード追加が必要 |
| E | `patient_consents` schema (commit `20260509_patient_consents_schema.sql`) | 既存 | 本 spec §3 「保護者同意 gate」の SoT |
| F | `patient_chat_engine.PATIENT_CHAT_SYSTEM_PROMPT` (L80-106) | 既存 | 成人前提、kids 上書き必要 (§2) |

**本 spec で扱わない (= scope out):**
- 認可・認証 (cmd_004 別 task `subtask_cmd004_guardian_consent_spec` に委譲)
- frontend UI ビジュアル (デザイン班専権)
- `dinosaur_kingdom` のゲームロジック (cmd_004 別 task)

---

## 1. AC1: 現行 `patient_chat_engine.py` 機能調査 (file:line inventory)

調査 base: `/mnt/c/Projects/hakudokai-dev/backend/services/patient_chat_engine.py` @ b66ffe0b 系譜の HEAD (464 行)。

### 1-1. 公開 API

| 機能 | symbol | file:line | 備考 |
|------|--------|-----------|------|
| `load_dotenv` 自動読込 | module top | L36 | `backend/.env` の `ANTHROPIC_API_KEY` を取込。Windows env var 不在時の fallback |
| API key 取出 | `ANTHROPIC_API_KEY` | L40 | 未設定時は §1-3 fallback 文言を返す |
| メイン entrypoint | `patient_chat()` | L109-156 | async、`conversation_id` を UUID4 で自動採番 (L127) |
| 履歴取得 | `get_chat_history()` | L159-190 | `patient_chat_messages` 主、`patient_app_activity` fallback |

### 1-2. 内部 helper

| 機能 | symbol | file:line | 備考 |
|------|--------|-----------|------|
| 患者コンテキスト構築 | `_build_patient_context()` | L195-251 | `patient_tooth_status` + `treatment_plan_items` + CRM 統合 |
| CRM コンテキスト | `_build_crm_context()` | L254-305 | SQLite から年齢 (dob 算出) + 特記事項 (`crm_notes.memo`) を抽出。PII 名前は含めず |
| メッセージ永続化 | `_save_chat_messages()` | L308-335 | user (2000 字 trunc) + assistant (4000 字 trunc) を一括 insert |
| フォーム参照 | `_get_relevant_form_context()` | L338-378 | `_KEYWORD_FORM_MAP` (L47-76) で 25 キーワード → form_key 紐付け、module-level cache |
| activity 記録 (legacy) | `_record_ai_activity()` | L381-395 | `patient_app_activity` 後方互換 |
| 提案アクション | `_generate_suggested_actions()` | L398-425 | `book_appointment` / `view_treatment` / `call_clinic` の 3 種 |
| Claude API call | `_call_claude_api()` | L428-464 | model = `CLAUDE_MODEL` (config 外出し)、max_tokens=1024、`api.anthropic.com/v1/messages` |

### 1-3. fallback 文言

| 条件 | 返却文言 (要旨) | file:line |
|------|----------------|-----------|
| `ANTHROPIC_API_KEY` 未設定 | 「現在AIチャット機能を準備中です。…次回来院時にスタッフから…」 | L430-436 |
| API call 例外 | 「申し訳ございません。現在回答を生成できませんでした。…」 | L458-464 |

### 1-4. router endpoint inventory

`backend/routers/patient_chat.py` (60 行):

| method | path | handler | 制約 |
|--------|------|---------|------|
| POST | `/api/patient-chat/message` | `send_message()` L36-51 | `message` 空 → 400、>2000 字 → 400 |
| GET | `/api/patient-chat/history/{patient_id}` | `chat_history()` L57-60 | query `limit` (default 50) |

prefix `/api/patient-chat` (router L20)。**現状 kids 専用 endpoint なし** = §3 で kids context 差替経路を規定。

---

## 2. AC2: gap 分析 (既起案 vs 現実装 vs 不足機能)

### 2-1. 既起案資産

`queue/reports/ashigaru5_report_supplement_ai_chat_spec.yaml` (2026-05-09 22:45 ashigaru5 supplement、232 行)。タスク背景の「ai_chat_existing_impl_spec.md (446 行)」**実物は repo に未存在**、本 spec は supplement YAML を SoT として gap 分析する。

### 2-2. 三項比較

| # | 領域 | 既起案 (supplement) | 現実装 (b66ffe0b 系) | cmd_004 kids 要件 | gap 状態 |
|---|------|---------------------|----------------------|-------------------|----------|
| G1 | フロント `PatientChat.tsx` URL params | `patient_id` + `clinic_id` | (未確認、本 spec 範囲外) | **+`is_minor`** flag、保護者同意 gate token | 🟥 kids 向け要拡張 |
| G2 | `_FORM_CACHE` kids 向け form_key | `child_oral_questionnaire` 1 件のみ | 同左 (L64-66) | 「離乳」「歯磨き」「むし歯予防」「乳歯」 を `_KEYWORD_FORM_MAP` に追加 | 🟥 不足 |
| G3 | system prompt | `PATIENT_CHAT_SYSTEM_PROMPT` 成人前提 | 同左 (L80-106) | **年齢適応分岐** (= 0-6 / 7-12 / 13-18 + 保護者代行) | 🟥 prompt 上書き必要 |
| G4 | `patient_chat_messages` RLS | 「ポリシーは別途追加要」 | RLS enabled, policy 未追加 | 患者本人 OR 保護者 (`patient_guardians` 経由) のみ SELECT | 🟥 未実装 (本 spec §4) |
| G5 | retention | 規定なし | 規定なし | **18 歳到達後 + 7 年** (医療法施行規則第 20 条 + 民法 724 条整合、要法務確認) | 🟥 未起案 |
| G6 | suggested_actions | 3 種 (`book_appointment` / `view_treatment` / `call_clinic`) | 同左 (L398-425) | kids 追加: `notify_guardian` / `book_pediatric_visit` | 🟥 未拡張 |
| G7 | dinosaur_kingdom 連動 | 言及なし | 言及なし | キャラクター人格 (= AI が「ティラノ博士」等を演じる) + XP 加算 hook | 🟥 未起案 (本 spec §5) |
| G8 | 危機介入 escalation | 言及なし | 言及なし | 自傷 / DV / 急性疼痛 keyword 検出 → 専門医・保護者通知 path | 🟥 未起案 (本 spec §6) |
| G9 | 医療助言禁止 | 「確定的な診断禁止」のみ (L88) | 同左 | kids では更に厳しく: **「治療提案禁止」+「保護者経由のみ問診誘導」** | 🟥 強化必要 |
| G10 | 会話 audit trail | `patient_chat_messages.role/message/created_at` のみ | 同左 (L308-335) | **system_prompt_version** + **age_band** + **flagged_for_review** カラム追加 | 🟥 schema 追加必要 |

**まとめ:**
- 既実装 (b66ffe0b) は **成人 chat MVP** として動作可能 (`ANTHROPIC_API_KEY` を除けば)。
- kids への流用には **prompt 差替 + RLS + retention + 危機介入 + dinosaur_kingdom 連動** の 5 領域の拡張が必要。
- いずれも spec 起案のみ、本 task では実装しない。

---

## 3. AC3: 設計 spec — 小児患者向け AI チャット

### 3-1. システム全体像 (kids mode)

```
[小児患者 (= 患者本人 7-12 歳想定) or 保護者代行]
       │  HTTPS (PWA, frontend/src/patient-app/pages/PatientChat.tsx)
       ▼
[POST /api/patient-chat/message]
       │  body: {patient_id, message, conversation_id, clinic_id, is_minor=true,
       │         guardian_consent_token (= subtask_cmd004_guardian_consent_spec で発行)}
       ▼
[patient_chat() L109]
       │  ① guardian_consent_token 検証 (新規 helper、§3-4)
       │  ② age_band 判定 (= _build_crm_context() の年齢から)
       │  ③ kids prompt 切替 (§3-2)
       │  ④ dinosaur_kingdom character context 注入 (§5)
       │  ⑤ 危機介入 pre-filter (§6)
       │  ⑥ Claude API call (max_tokens=512 = kids では短縮)
       │  ⑦ post-filter (= reply に医療助言 keyword 混入なきか)
       │  ⑧ _save_chat_messages() + audit trail (§3-5)
       ▼
[reply + suggested_actions (kids 拡張)]
```

### 3-2. 年齢適応 prompt 分岐

新規定数 (実装時に追加):

```python
KIDS_AGE_BANDS = {
    "preschool": (0, 6),    # 未就学、保護者代行前提
    "child":     (7, 12),   # 小学生、本人入力可
    "teen":      (13, 18),  # 中高生、本人入力 + 一部保護者通知
}

KIDS_CHAT_SYSTEM_PROMPT_TEMPLATE = """\
あなたは博道会グループ歯科の「{character_name}」です。
{age_band_addressing} (= age_band により呼びかけ調を切替)。

## 厳守ルール (kids 強化版)

1. **医療診断・治療提案を絶対に行わない**: 「むし歯かも」も禁止、「歯医者さんに相談しようね」のみ
2. **専門用語を避ける**: 専門用語使用時は必ず平易な日本語へ言い換え (例: 「う蝕」→「むし歯」)
3. **不安を煽らない**: 痛み・出血等の主訴には共感のみ、原因推測禁止
4. **保護者誘導を必ず含める**: 回答末尾に必ず「おうちのひとに、このお話をしてくれるかな?」を含める
5. **危機キーワード検出時は §6 escalation path** (= 自傷/虐待/急性疼痛/呼吸困難の語彙)
6. **個人情報・住所・電話番号を会話から聞き出さない**
7. **キャラクター没入と医療助言禁止の両立**: 「{character_name} は知ってるよ」と言わず、「{character_name} もくわしくはわからないから、おうちのひとに聞こうね」

## 文体

- 漢字は小学校 {grade} 年生レベルまで (age_band 連動)
- 1 回答 150 文字以内 (= 既存 300 字より短縮)
- 絵文字使用可、ただし医療絵文字 (注射器 / 血液型) 禁止
"""
```

| age_band | character 呼びかけ | 漢字レベル | max_tokens | 保護者通知頻度 |
|----------|-------------------|------------|-----------|----------------|
| preschool | 「○○ちゃん」、ひらがな主体 | 小1 まで | 384 | 全件通知 |
| child | 「○○さん」「○○くん」 | 小4 まで | 512 | flagged のみ |
| teen | 「○○さん」 | 小6 まで | 768 | flagged のみ + 月次 digest |

### 3-3. dinosaur_kingdom キャラクター人格化 (§5 に詳述)

`KIDS_CHARACTERS` を新規 module level 定数で定義し、`patient_chat_messages` に紐付く `character_name` を session 単位で固定する (= 会話途中で人格が変わると子供が混乱)。詳細は §5。

### 3-4. 保護者同意 gate 連動

**前提**: `subtask_cmd004_guardian_consent_spec` (ashigaru4 並行起案) が `patient_consents` table の `consent_type='kids_ai_chat'` 行を発行する。本 spec はその token を **検証する側** を規定する。

新規 helper (実装時):

```python
def _verify_guardian_consent(patient_id: str, token: str) -> dict | None:
    """guardian_consent_token を検証し、有効なら consent row を返す。

    検証項目:
      - patient_consents.consent_type='kids_ai_chat'
      - patient_consents.revoked_at IS NULL
      - patient_consents.expires_at > now()
      - HMAC(token) == patient_consents.token_hash
    """
```

無効/期限切れ時は **HTTP 403 + 「保護者の同意が必要です。アプリでおうちのひとに同意を確認してもらってください」** を返す。

### 3-5. チャット履歴 retention

| 項目 | 仕様 | 根拠 |
|------|------|------|
| 物理保存先 | `patient_chat_messages` (Supabase) | 既存 |
| 保存期間 | **患者 18 歳到達 + 7 年** | 医療法施行規則第 20 条 (5 年) + 民法 724 条 (損害賠償請求権の消滅時効を意識して延長)、**要法務確認** |
| 削除方式 | 物理 DELETE は cron 夜間バッチ (= 別 task)、論理削除カラム `deleted_at` を併用 | 即時削除は patient app からの取消請求受付時のみ |
| 保護者同意取消時 | `deleted_at = now()` で論理削除、180 日後物理 DELETE | 個人情報保護法第 35 条 (利用停止) |
| audit trail | 削除前に `patient_chat_messages_archive` (新規 table 提案) に書き戻し、retention 規定の物理担保 | T17 「DELETE 禁止、追記のみ」契約に整合 |

**新規カラム提案** (`patient_chat_messages` ALTER):

```sql
ALTER TABLE patient_chat_messages
  ADD COLUMN IF NOT EXISTS is_minor              boolean    NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS age_band              text       NULL CHECK (age_band IN ('preschool','child','teen')),
  ADD COLUMN IF NOT EXISTS system_prompt_version text       NULL,
  ADD COLUMN IF NOT EXISTS character_name        text       NULL,
  ADD COLUMN IF NOT EXISTS flagged_for_review    boolean    NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS flag_reason           text       NULL,
  ADD COLUMN IF NOT EXISTS deleted_at            timestamptz NULL;
CREATE INDEX IF NOT EXISTS idx_pcm_flagged ON patient_chat_messages(flagged_for_review) WHERE flagged_for_review = true;
```

---

## 4. RLS Policy 設計

### 4-1. SELECT policy (4 layer)

```sql
-- Layer A: 患者本人 (authenticated, user_id = patient_id mapping 経由)
CREATE POLICY pcm_select_patient ON patient_chat_messages FOR SELECT
USING (
  deleted_at IS NULL
  AND patient_id = current_setting('app.current_patient_id', true)
);

-- Layer B: 保護者 (patient_guardians table 経由、is_minor=true 時のみ)
CREATE POLICY pcm_select_guardian ON patient_chat_messages FOR SELECT
USING (
  deleted_at IS NULL
  AND is_minor = true
  AND EXISTS (
    SELECT 1 FROM patient_guardians pg
    WHERE pg.minor_patient_id = patient_chat_messages.patient_id
      AND pg.guardian_user_id = current_setting('app.current_user_id', true)::uuid
      AND pg.revoked_at IS NULL
  )
);

-- Layer C: 院内スタッフ (clinic role, clinic_id 一致時のみ)
CREATE POLICY pcm_select_clinic_staff ON patient_chat_messages FOR SELECT
USING (
  clinic_id = current_setting('app.current_clinic_id', true)::int
  AND current_setting('app.current_role', true) IN ('staff', 'dentist', 'director')
);

-- Layer D: service_role (バッチ・移行用、全権)
CREATE POLICY pcm_select_service ON patient_chat_messages FOR SELECT TO service_role
USING (true);
```

### 4-2. INSERT policy

`patient_chat()` 内のみ書込 (= backend service が service_role で実行)。authenticated 直接 INSERT は禁止 (= policy 不在 → 全拒否)。

### 4-3. UPDATE / DELETE policy

- UPDATE: `deleted_at` のみ更新可、それ以外のカラム書換禁止 (= 別 policy で WITH CHECK 制約)。
- DELETE: 物理 DELETE は service_role のみ、cron 夜間バッチ用。

### 4-4. RLS テスト要件 (cmd_004 別 task で QA)

- 患者本人で他患者の履歴を SELECT → 0 件返却 (= F006 防護)
- 保護者で同意取消後の SELECT → 0 件返却
- 院外スタッフ (clinic_id ミスマッチ) で SELECT → 0 件返却

---

## 5. dinosaur_kingdom 連動 (キャラクター人格化)

### 5-1. キャラクター 4 体 (kids_app 既存資産整合、要 ashigaru6 監修)

| character_id | name | persona | XP per interaction |
|--------------|------|---------|-------------------|
| tyrano | ティラノ博士 | 強そう・元気・口調はやや荒い (= 「がおー!」) | 5 |
| trike | トリケラ先生 | やさしい・落ち着き | 5 |
| brachio | ブラキオお兄さん | のんびり・ゆっくり | 5 |
| velo | ヴェロちゃん | はやい・ちょこちょこ | 5 |

session 開始時に `patient_app_activity` から「最後に話したキャラクター」を取得、変更時のみ会話冒頭で `「今日はぼくが話すよ!」` と切替を明示。

### 5-2. 人格保持と医療助言禁止の両立

§3-2 prompt の §厳守ルール 7 を再掲: **「{character_name} もくわしくはわからないから」** で逃がす。「ティラノ博士はむし歯のことよく知ってる!」のような断言は**禁止**。

### 5-3. XP 加算 hook (cmd_004 別 task `subtask_cmd004_dinosaur_kingdom` で実装)

```python
# patient_chat() L156 直前 (= return 直前) に追加予定:
if is_minor and not flagged_for_review:
    from backend.services.dinosaur_kingdom_engine import award_chat_xp
    await award_chat_xp(patient_id, character_id, xp=5)
```

`award_chat_xp` は **別 task で起案する独立 module**、本 spec は呼出 contract のみ規定。

---

## 6. AI 出力安全制約 (危機介入 escalation)

### 6-1. pre-filter (= user message 受領時)

新規 helper:

```python
CRISIS_KEYWORDS = {
    "self_harm":    ["死にたい", "消えたい", "自分を傷つけ"],
    "abuse":        ["たたかれ", "なぐられ", "蹴られ", "こわい人", "夜にあの人"],
    "acute_pain":   ["息ができない", "ものすごい痛み", "倒れそう", "口が開かない"],
    "allergy":      ["息苦しい", "呼吸が", "じんましん", "ぐったり"],
}

def _detect_crisis(message: str) -> str | None:
    """危機キーワード検出。マッチ時はカテゴリ名を返す。"""
```

検出時の動作:

| category | Claude API 呼出 | 即時返答 | 通知先 |
|----------|----------------|----------|--------|
| self_harm | **呼ばない** | 「とてもだいじなお話だね。すぐに、おうちのひとか、よりそいホットライン (= 0120-279-338) に電話してね」 | 院内スタッフ + 保護者 (= inbox 即時 push) |
| abuse | **呼ばない** | 同上 + 児童相談所 全国共通ダイヤル (= 189) | **院内スタッフのみ** (= 保護者通知は加害可能性ゆえ抑止)、要法務確認 |
| acute_pain | **呼ばない** | 「すぐにおうちのひとに、このお話をしてね。歯医者さんは {clinic_phone} だよ」 | 院内スタッフ + 保護者 |
| allergy | **呼ばない** | 「すぐに大人を呼んで、できれば 119 番してね」 | 院内スタッフ + 保護者 + (緊急時) 119 案内 |

### 6-2. post-filter (= Claude reply 受領後)

```python
FORBIDDEN_REPLY_PATTERNS = [
    r"虫歯[ですだ]",         # 確定診断
    r"治療[をが]必要",         # 治療提案
    r"\d+[円万]",            # 金額
    r"絶対",                  # 断定
    r"インプラント",          # 成人向け治療法 (kids では避ける)
    r"抜歯[しすま]",          # 治療提案
]
```

マッチ時は reply を **fallback 文言 (= 「おうちのひとに、このお話をしようね。歯医者さんも待ってるよ」)** に差替、`flagged_for_review=true` を立てる。

### 6-3. escalation path (院内通知)

`patient_chat_messages.flagged_for_review = true` の行を `inbox_watcher` 相当の DB trigger or polling job (= cmd_004 別 task で実装) が拾い、院内スタッフ (= clinic_id = staff role) の inbox に通知する。

```
[crisis 検出] → flagged_for_review=true + flag_reason=category 記録
              → 院内スタッフ inbox に「kids chat alert: patient_id=XXX, category=self_harm」
              → (保護者通知許可カテゴリの場合) 保護者 push 通知
              → 院長/管理者は dashboard で確認可
```

### 6-4. 法務・倫理確認事項 (= 本 spec の保留)

| # | 確認事項 | 確認先 | 備考 |
|---|---------|--------|------|
| L1 | abuse カテゴリで保護者通知を抑止する判断の法的整合 | 顧問弁護士 + 児童相談所相談員 | 児童虐待防止法第 6 条 (通告義務) との整合確認 |
| L2 | self_harm カテゴリで電話番号案内 (よりそいホットライン) の医療広告ガイドライン整合 | 顧問弁護士 | 公的窓口紹介は medical advice に該当しないことの確認 |
| L3 | 18 歳到達 + 7 年 retention の医療法整合 | 顧問弁護士 + 医療情報技師 | 医療法施行規則第 20 条との照合 |
| L4 | 危機検出 false positive 時の救済 path | UX 班 + 法務 | 子供が冗談で「死にたい」と書いた場合の取扱 |

---

## 7. 監査・モニタリング

### 7-1. 定量 metric (dashboard 用)

| metric | 計測方法 | 警報閾値 |
|--------|----------|---------|
| 日次 chat 件数 (kids) | `count(*) WHERE is_minor=true GROUP BY date` | — |
| flagged_for_review 率 | `flagged / total` | >5% で要 review |
| crisis 検出件数 | `flag_reason IS NOT NULL GROUP BY flag_reason, date` | self_harm/abuse 1 件で院長即時通知 |
| 平均応答時間 | (`reply 保存時刻` - `user 保存時刻`) p95 | >3s で要調査 |
| API key fail 件数 | `_call_claude_api()` の fallback 文言返却数 | >10/日で SRE 通知 |

### 7-2. 月次 review

- flagged_for_review=true の全行を院長+顧問弁護士が確認
- system_prompt_version 別の応答品質 sampling review
- character_id 別の XP 加算傾向 (= dinosaur_kingdom 連動健全性)

---

## 8. 実装ロードマップ (本 task scope 外、参考)

| phase | task_id (予定) | 内容 | 前提 |
|-------|---------------|------|------|
| P1 | `subtask_cmd004_ai_chat_impl_prompt` | §3-2 kids prompt + age_band 分岐実装 | ANTHROPIC_API_KEY 解消 |
| P2 | `subtask_cmd004_ai_chat_impl_rls` | §4 RLS policy migration | `patient_guardians` table 存在 (guardian_consent spec) |
| P3 | `subtask_cmd004_ai_chat_impl_crisis` | §6 pre/post filter + escalation | 院内通知 channel 整備 |
| P4 | `subtask_cmd004_ai_chat_impl_dinosaur` | §5 dinosaur_kingdom 連動 | `dinosaur_kingdom_engine` 存在 |
| P5 | `subtask_cmd004_ai_chat_impl_retention` | §3-5 retention cron + archive table | 法務確認 (L3) 完了 |
| P6 | `subtask_cmd004_ai_chat_qa_e2e` | E2E + RLS テスト (= 家老担当) | P1-P5 完了 |

---

## 9. 未確定事項 (Open Items)

| ID | 項目 | 影響 | 対処 |
|----|------|------|------|
| O1 | `ai_chat_existing_impl_spec.md` (446 行) **実物不在** | 既起案資産の SoT 不明 | supplement YAML を SoT 認定、本 spec で代替 (本セクション末尾に明記) |
| O2 | `patient_guardians` table 存在未確認 | §4 Layer B RLS の前提崩れ可能性 | `subtask_cmd004_guardian_consent_spec` (ashigaru4) で起案待ち |
| O3 | `dinosaur_kingdom_engine` 実装位置 | §5 award_chat_xp 呼出 contract 未確定 | ashigaru6 (kids_app 担当) 監修要 |
| O4 | character_id 確定 | §5 4 体は本 spec 暫定、IP・デザイン班確認要 | デザイン班 + ashigaru6 監修要 |
| O5 | 法務確認 4 件 (L1-L4) | retention + 危機介入の法的妥当性 | 顧問弁護士照会、cmd_004 完遂前に必須 |
| O6 | clinic_phone の取扱 | §6-1 acute_pain 文言で動的差込 | `clinics.phone` カラムから取得、PII 取扱注意 |
| O7 | system_prompt_version 採番ルール | §3-5 audit trail | semver `kids-vX.Y` 命名提案、別 task で決定 |

---

## 10. 評価指標 (acceptance criteria 自己 check)

| AC | 状態 | 根拠 |
|----|------|------|
| AC1 (現行機能調査) | ✅ §1 で 464 行 / 60 行を file:line 列挙、endpoint inventory 完了 |
| AC2 (gap 分析) | ✅ §2-2 で 10 項目 G1-G10 を既起案 vs 現実装 vs kids 要件で三項比較 |
| AC3 (設計 spec) | ✅ §3-§7 で prompt 制約 / 保護者同意 gate 連動 / retention / RLS / dinosaur_kingdom 連動 を起案 |
| AC4 (報告 YAML) | 別途 `queue/reports/ashigaru5_cmd004_ai_chat_report.yaml` に記録 |

---

## 11. 本能寺戒め 自己 check

- **既起案資産の rebuild 禁止**: supplement YAML を SoT 認定、`PATIENT_CHAT_SYSTEM_PROMPT` を全廃せず kids 用は別定数として併存 (= 成人 chat は無傷)
- **機械 evidence のみ**: file:line, 行数, commit hash, table 名, migration file 名を全て検証可能形式で記載
- **spec only**: §8 ロードマップに実装責務を別 task として明示分離、本 spec 内に impl コードは含めない (Python snippet は contract 明示用、commit せず)
- **F001-F007 遵守**: 自走実装禁止 (F002)、推測引用禁止 (F006)、scope 外作業禁止 (F007)
- **法令引用**: 医療法施行規則第 20 条 / 民法 724 条 / 個人情報保護法第 35 条 / 児童虐待防止法第 6 条 を引用、いずれも「**要法務確認**」と但書を併記 (= e-Gov path 直接検証は本 task 範囲外)

---

以上、subtask_cmd004_ai_chat_spec 起案完遂。
