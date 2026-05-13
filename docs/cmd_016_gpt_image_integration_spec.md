# cmd_016 OpenAI gpt-image-2 + Google gemini-3.1-flash-image-preview dual model integration (= 小児恐竜王国 100 体敵キャラ画像生成 path、2026/05/13 dual model SOTA + 多様性)

- task_id: subtask_cmd016_phase2_dual_model_extension_gpt_image_2_and_gemini_3_1_flash
- parent_cmd: cmd_016「OpenAI + Google dual model image integration (= 小児恐竜王国 100 体敵キャラ画像生成 path)」
- parent_directive: msg_20260513_114137_d97dfc4b (= 信長殿 task_directive dual model)
- supersedes_history: v1 spec (= 旧モデル ID 単体、b22914c、詳細は §16 reflection retain note) → v2 model 補正 (= gpt-image-2 単体、6f62fa7) → 本 v4 (= dual model 拡張)
- bloom_level: L4 (= grouped dual model 設計 + abstraction + routing + cost)
- author: ashigaru5 (蒲生氏郷 persona、子飼い若手、文武両道、教養派)
- 起案日: 2026-05-13
- base_commit: 6f62fa7 (= 前 cycle commit、cmd_016 phase2 v3)
- 範囲: **Phase 2 spec design + abstraction + sketch + skeleton only**。実 API call / 実画像生成 / 実 Supabase upload / 実 DentalBI schema migration / 実 cost 課金 は **Phase 3 (= 別 step、両 API key 取得後信長殿明示承認下)**。
- 連動資産:
  - `scripts/openai_image_client.py` (= 既装着、本 cycle で ImageProvider abstraction 化)
  - `scripts/gemini_image_client.py` (= **本 cycle 新規**、ImageProvider 実装)
  - `tests/test_cmd016_dual_model_skeleton.py` (= 既 `test_cmd016_gpt_image_skeleton.py` から `git mv` rename、dual model 拡張、SKIP=0 厳守)
  - `docs/cmd004_dinosaur_100enemies_spec.md` (= 100 体生成 plan 連動)
  - `queue/reports/ashigaru4_pending_implementation_9_inventory_report.yaml` (= DentalBI integration point 候補)
  - `scripts/sync_to_supabase.sh` (= 既装着 sync utility、Phase 3 で連動 candidate)

---

## 0. Anti-Duplication: 参照済み正本 / 不参照

| # | 正本 | 所在 | 利用方法 |
|---|------|------|----------|
| A | `~/.openai_venv/` (= openai 2.36.0 install 完遂) | MainPC venv | Phase 3 OpenAI client wrapper の実行環境 |
| B | `scripts/sync_to_supabase.sh` | repo 内既装着 | Phase 3 で Supabase Storage upload と連動 candidate |
| C | `docs/cmd004_*_spec.md` (= dinosaur_100enemies 等) | repo 内既装着 | 本 spec の section 構成 pattern 範本 + 100 体生成 plan 連動 |
| D | `queue/reports/ashigaru4_pending_implementation_9_inventory_report.yaml` (= 9 件 inventory) | repo 内既装着 | DentalBI integration point 候補 SoT |
| E | OpenAI 公式 docs (= `https://developers.openai.com/api/docs/models/gpt-image-2`) | 外部 SaaS | gpt-image-2 モデル ID + parameters + rate limit SoT |
| F | Google AI 公式 docs (= `https://ai.google.dev/gemini-api/docs/image-generation` + `/models`) | 外部 SaaS | gemini-3.1-flash-image-preview モデル ID + 14 枚 reference + 4K + Thinking 制御 SoT |

**Anti-duplication retract note (= 黒田 guard #1 整合):**
- `context/dentalbi.md` = 不在 (= 2026-05-13 09:44 confirmed)、本 spec の context source として **入力扱い禁**。
- 代替 source = `queue/reports/ashigaru4_pending_implementation_9_inventory_report.yaml` + `scripts/extract_dentalbi_form_inventory.py` + repo 既装着 spec のみ。

**本 spec で扱わない (= scope out / Rule 11 boundary):**
- 実 OpenAI / Google client object 生成 (= SDK 真実 client、live network 接続) — Phase 3 別 step
- 実 API call (= images.generate / generateContent live invocation) — Phase 3 別 step
- 実 Supabase Storage upload (= Phase 3 別 step)
- 実 DentalBI schema migration apply (= Phase 3 別 step、本 spec は sketch のみ)
- 実 cost 課金 (= 両 API key wait + 信長殿明示承認下 Phase 3)
- frontend UI ビジュアル (= デザイン班専権)

---

## 1. 目的 + scope + dual model 戦略

### 1.1 目的
小児恐竜王国 100 体敵キャラ画像生成 + 患者 PWA illustration を **OpenAI gpt-image-2 + Google gemini-3.1-flash-image-preview (Nano Banana 2) dual model** で path 確立。5-10 年運用想定、cost 抑制 (= Auto Recharge OFF retain + threshold alert)、API key 漏洩防止、Rule 11 ashigaru 責務境界遵守、ImageProvider abstraction で SDK 切替容易性 retain。

### 1.2 dual model 戦略 (= 信長殿 11:41 task_directive + 陛下御差配 11:50 整合)
- **gpt-image-2** (= OpenAI、release 2026/04/21、Performance Highest、Speed Medium、GA) → **キャラクター高品質**用途
- **gemini-3.1-flash-image-preview** (= Google Nano Banana 2 preview、Resolution 4K + reference image up to 14 + Thinking 制御) → **複雑 composition + 量産**用途
- **gemini-2.5-flash-image** (= Nano Banana stable、native image generation/editing) → **量産低 cost retain candidate** (= Phase 3 で cost 検証後)
- 用途別 routing logic で最適 model 自動選択、cost 最適化 + 多様性両立。

### 1.3 scope (= bloom L4 grouped dual model 設計 + abstraction + sketch + skeleton)
A. spec markdown 起案 (= 本 doc、dual model + abstraction + routing + cost)
B. ImageProvider abstraction layer 設計 (= interface 共通 method + PromptTemplate model 別最適化 + 用途別 routing logic + cost logger sketch)
C. `scripts/openai_image_client.py` (= ImageProvider 実装、mock/placeholder retain)
D. `scripts/gemini_image_client.py` (= 新規、ImageProvider 実装、mock/placeholder)
E. `tests/test_cmd016_dual_model_skeleton.py` (= 既 file `git mv` rename + dual model extension、SKIP=0 厳守)
F. cost 管理 logic (= monthly budget alert + Auto Recharge OFF retain + dual model cost 比較 plan)
G. DentalBI integration point sketch (= migration sketch only)

### 1.4 scope out (= Rule 11 boundary、本 task で行わない)
- SDK 真実 client object instantiation (= openai.OpenAI(api_key=...) / google.generativeai.GenerativeModel(...) 等 live network 接続)
- 実 API call / 実画像生成 / 実 Supabase upload / 実 schema migration apply / 実 cost 課金

---

## 2. 制約 + 公式 docs evidence (= 6+ evidence retain 必達、両 model SoT 三点照合)

### 2.1 evidence #1 確認日
2026-05-13 (= 本 cycle 着手日、両 model WebFetch 機械 verify 実施日)

### 2.2 evidence #2 OpenAI gpt-image-2 公式 docs

| 項目 | 値 | SoT |
|------|----|----|
| Model ID | `gpt-image-2` | 公式 model card |
| Release | 2026/04/21 (snapshot) | 公式 model card |
| Performance | Highest | 公式 model card |
| Speed | Medium | 公式 model card |
| Status | GA (default SOTA) | 公式 model catalog |
| Endpoint | `v1/images/generations` (= primary) + Chat Completions / Responses / Image edit etc. | 公式 model card |
| Input | Text + image | 公式 model card |
| Output | Image only | 公式 model card |
| **Rate limit** (= IPM 軸) | Tier 1: 5 IPM / Tier 2: 20 / Tier 3: 50 / Tier 4: 150 / **Tier 5: 250 IPM** | 公式 model card |
| Features NOT supported | Streaming / Function calling / Structured outputs / Fine-tuning / Predicted outputs | 公式 model card |
| **Pricing** | per-token 体系 + per-image lookup table (= 公式 pricing page / image generation calculator)、本 spec で per-image table は v1-v3 移植 retain、Phase 3 で 公式 calculator 機械 verify 必達 | 公式 pricing page |
| URL | `https://developers.openai.com/api/docs/models/gpt-image-2` | 公式 |

注: **rate limit (IPM) と pricing は別軸**、混同禁。pricing は per-token / per-image 別 field。

### 2.3 evidence #3 Google gemini-3.1-flash-image-preview 公式 docs

| 項目 | 値 | SoT |
|------|----|----|
| Model ID | `gemini-3.1-flash-image-preview` (= Nano Banana 2 preview) | 公式 |
| Status | Preview | 公式 |
| **Reference images** | **up to 14** (= 10 objects high-fidelity + 4 character images for consistency) ✅ **WebFetch 機械 verify confirmed 2026-05-13** | 公式 image-generation docs |
| Resolution | 512 (0.5K) / 1K / 2K / 4K | 公式 |
| Thinking 制御 | minimal / high + `includeThoughts` boolean | 公式 |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent` | 公式 |
| Pricing | per-token 体系 (= Google AI pricing page、Phase 3 で機械 verify 必達) | 公式 pricing page |
| Rate limit | 公式 rate-limits page 参照、Phase 3 で 機械 verify 必達 | 公式 rate-limits page |
| 強み | 4K + reference image 14 + Thinking + Google Search grounding + advanced text rendering | 公式 |
| URL | `https://ai.google.dev/gemini-api/docs/image-generation` + `/models` | 公式 |

### 2.4 evidence #4 selection 理由 (= gpt-image-2 primary character / gemini-3.1 complex composition)

- **gpt-image-2 primary character 用途**:
  - GA + Performance Highest = キャラクター高品質に最適
  - Latest flagship (= 2026/04/21 release、SOTA) = deprecate risk 低
  - Image edit endpoint 整合 (= キャラクター iteration 用)
- **gemini-3.1-flash-image-preview composition 用途**:
  - Reference image 14 (= 公式 verify ✅) = 既存キャラ + 背景 + props 組合せの複雑 composition 最適
  - 4K resolution = 高解像度 場面構成
  - Thinking 制御 = prompt 解釈精度向上
- **gemini-2.5-flash-image stable retain candidate (= Phase 3 cost 検証後)**:
  - State-of-the-art native image generation/editing
  - Stable status = preview 退避 path
  - 量産低 cost 候補

### 2.5 evidence #5 dual pricing SoT (= 黒田 v1 fail P0 fix #3 + v2 fail P0 fix #2 整合)

| Model | rate limit (IPM/TPM) | pricing scheme | per-image cost | per-token cost |
|-------|----------------------|----------------|----------------|----------------|
| gpt-image-2 | Tier 1=5 IPM / Tier 5=250 IPM (= 公式 verify ✅) | per-token + per-image (= 公式 calculator 体系) | Phase 3 公式 calculator 機械 verify 必達 (= 旧 v1.5 移植 table は撤退) | Phase 3 公式 verify 必達 |
| gemini-3.1-flash-image-preview | 公式 rate-limits page 参照 (= Phase 3 verify) | per-token 体系 (= Google AI) | per-image table 非公開、per-token から計算 | 公式 pricing page (= Phase 3 verify) |
| gemini-2.5-flash-image | 公式 rate-limits page 参照 | per-token 体系 (= retain candidate) | 同上 | 同上 |

**注 (= 黒田 v1 fail P0 fix #3 整合)**: 旧 v1 spec の前モデル per-image table (low/medium/high、詳細は §16 reflection retain note) は **gpt-image-2 GA で SoT 不一致**、Phase 3 で 公式 calculator から per-image cost を機械 verify するまで **per-image table retain せず**、本 spec では rate limit (IPM/TPM) のみ確定値。pricing は別 field。

### 2.6 evidence #6 dual API key 取得 plan (= 陛下御願 web 側 step retain)

- **OpenAI API key**: 陛下御願 web 側 (= platform.openai.com で API key 発行 + Auto Recharge OFF + Org Verification、最大 1 日 wait)
- **Google AI Studio API key**: 陛下御願 web 側 (= aistudio.google.com で API key 発行 + 課金設定確認)
- 両 key 取得後 = Phase 3 step 起案 candidate (= 信長殿明示承認下)
- 本 Phase 2 では env var placeholder のみ、live call 全禁

### 2.7 その他制約
- **Auto Recharge OFF retain** (= 信長殿明示、両 API key とも、課金暴走防止)
- **API key 漏洩防止** = env var `OPENAI_API_KEY` / `GOOGLE_AI_API_KEY` 経由のみ、コード literal hard-code 禁、log 出力禁
- **5-10 年運用想定** = radical_solution_during_development_rule 整合、根本治療品質
- **ImageProvider abstraction** = SDK / model 切替容易性 retain (= 将来 SOTA 切替時の蹴り出し path)

---

## 3. A scope: spec markdown 起案 (= 本 doc)

本 markdown 全体が A scope deliverable。yaml 混在禁 (= markdown one source)。A-G 全観点記載。dual model + abstraction + routing + cost 比較 plan 全件 retain。

---

## 4. B scope: ImageProvider abstraction layer 設計

### 4.1 interface 共通 method

```python
class ImageProvider(Protocol):
    """Abstract image generation provider — Phase 2 sketch only."""
    model_id: str
    provider_name: str

    def generate(self, prompt: str, options: dict) -> dict:
        """Return placeholder dict in Phase 2; Phase 3 returns real image metadata."""
        ...
```

**Phase 2 boundary**: abstraction interface 実装可 (= 必達)、SDK 真実 client object instantiation のみ禁 (= guard #2 整合)。local mock provider class は実装要。

### 4.2 PromptTemplate model 別最適化 sketch

| Model | prompt 形式 | 特殊指示 |
|-------|-------------|----------|
| gpt-image-2 | "<scene description>, <character details>, <style hints>, <safety constraints>" | 暴力 minimum / 流血禁 / cartoon style 明示 |
| gemini-3.1-flash-image-preview | "<reference image refs>: <composition prompt>, <thinking instruction>" | reference image 連動 + Thinking 制御 (minimal/high) |
| gemini-2.5-flash-image | "<editing instruction>" or "<generation prompt>" (= retain) | native editing flow |

PromptTemplate class は Phase 2 で signature + structure のみ、Phase 3 で SDK 実呼出と整合化。

### 4.3 用途別 routing logic

```python
def select_provider(use_case: str) -> str:
    if use_case == "character":       # キャラクター高品質
        return "gpt-image-2"
    if use_case == "composition":     # 複雑 composition (= reference image 多用)
        return "gemini-3.1-flash-image-preview"
    if use_case == "bulk_low_cost":   # 量産低 cost (= cost 検証後)
        return "gemini-2.5-flash-image"
    return "gpt-image-2"              # default
```

| use_case | model | 理由 |
|----------|-------|------|
| character | gpt-image-2 | Performance Highest、キャラクター高品質 |
| composition | gemini-3.1-flash-image-preview | reference 14 + 4K + Thinking |
| bulk_low_cost | gemini-2.5-flash-image | stable + native + cost 候補 |

### 4.4 cost logger sketch (= dual model 統合)

```python
class CostLogger:
    """Phase 2: in-memory accumulator with threshold alert.
    Phase 3: persist to queue/reports/openai_image_cost_log.yaml or Supabase table."""
    thresholds = {"warn": 5.0, "halt_review": 10.0, "emergency_stop": 20.0}
```

- 両 model の estimated cost を統合計上、月集計
- threshold alert (= $5 warn / $10 halt_review / $20 emergency_stop)
- Auto Recharge OFF retain (= 信長殿明示)

---

## 5. C scope: OpenAI client wrapper (= abstraction 化)

### 5.1 file: `scripts/openai_image_client.py`

- ImageProvider interface 実装 (= class `OpenAIImageProvider`)
- model_id = `"gpt-image-2"` (= 公式 verify ✅)
- **Phase 2 全禁 retain**: SDK 真実 client (= `openai.OpenAI(api_key=...)`) instantiation のみ禁、local mock provider class 実装可 (= 必達、guard #2 整合)
- skeleton = mock / placeholder のみ、`return placeholder` で構造 retain

### 5.2 入出力 (= Phase 2 sketch)
- 入力: `prompt: str` + `options: dict` (size / quality / n / seed_id)
- 出力 Phase 2: placeholder dict (= phase + model + estimated_cost_usd + image_url_placeholder)
- 出力 Phase 3: 実 image URL (= Supabase Storage upload 後) or binary

### 5.3 env var 受領 path
- `OPENAI_API_KEY` (= .env 経由、placeholder only、log 禁、literal hard-code 禁)

### 5.4 retry/error handling sketch (= Phase 3 実装)
- rate limit (429): exponential backoff retry
- transient error (5xx): max 3 retry
- permanent failure (4xx): raise + alert log

---

## 6. D scope: Gemini client wrapper (= 新規)

### 6.1 file: `scripts/gemini_image_client.py` (= 本 cycle 新規)

- ImageProvider interface 実装 (= class `GeminiImageProvider`)
- model_id = `"gemini-3.1-flash-image-preview"` (= 公式 verify ✅、Nano Banana 2)
- alt model: `gemini-2.5-flash-image` (= stable retain candidate)
- **Phase 2 全禁 retain**: SDK 真実 client (= `google.generativeai.GenerativeModel(...)` 等) instantiation のみ禁、local mock 実装可
- skeleton = mock / placeholder のみ

### 6.2 入出力 (= Phase 2 sketch)
- 入力: `prompt: str` + `options: dict` (resolution / reference_images / thinking_level / include_thoughts)
- 出力 Phase 2: placeholder dict (= phase + model + estimated_cost_usd + image_url_placeholder + thinking_metadata_placeholder)

### 6.3 env var 受領 path
- `GOOGLE_AI_API_KEY` or `GEMINI_API_KEY` (= .env 経由、placeholder only)

### 6.4 reference image handling sketch
- up to 14 (= 公式 verify ✅): 10 object + 4 character
- 構造 only、実 image byte 取扱 Phase 3

---

## 7. E scope: tests dual model extension

### 7.1 file: `tests/test_cmd016_dual_model_skeleton.py`

- 既 `tests/test_cmd016_gpt_image_skeleton.py` から **`git mv` rename** (= 履歴 link path retain、delete 禁、AC 整合)
- dual model 両対応化: openai + gemini provider 各 14+ tests
- **SKIP=0 厳守** (= 黒田規範整合、skip 容認禁)

### 7.2 test cases (= dual model + abstraction + routing)

OpenAI provider 側:
1. `test_openai_provider_model_id_is_gpt_image_2` (= model_id literal verify)
2. `test_openai_provider_no_sdk_instantiation` (= openai.OpenAI / AsyncOpenAI 不在)
3. `test_openai_provider_generate_returns_phase2_placeholder`
4. `test_openai_provider_rejects_unsupported_size/quality/model`
5. `test_openai_provider_env_var_read_placeholder_only`
6. `test_no_api_key_literal_in_source` (= sk- / Bearer 不在)

Gemini provider 側:
7. `test_gemini_provider_model_id_is_3_1_flash_image_preview`
8. `test_gemini_provider_no_sdk_instantiation` (= GenerativeModel 不在)
9. `test_gemini_provider_generate_returns_phase2_placeholder`
10. `test_gemini_provider_reference_image_max_14` (= 公式 verify retain)
11. `test_gemini_provider_thinking_levels_minimal_high`
12. `test_gemini_provider_env_var_read_placeholder_only`

Abstraction + routing + cost:
13. `test_image_provider_protocol_attrs` (= model_id + provider_name + generate signature)
14. `test_router_character_returns_openai`
15. `test_router_composition_returns_gemini_3_1`
16. `test_router_bulk_low_cost_returns_gemini_2_5`
17. `test_cost_logger_thresholds_5_10_20`
18. `test_cost_logger_accumulate_dual_model`

Cross-cutting (= v1-v3 retain):
19. `test_prompt_template_rank_enum`
20. `test_prompt_template_safety_keyword_retain`
21. `test_no_old_model_id_gpt_image_1_5_in_code` (= reflection note のみ retain、code body 内禁)

### 7.3 enable path (= Phase 3)
- mock → 実 SDK call 切替 (= `unittest.mock` patch → 実 OpenAI/Gemini SDK client 切替)
- 両 API key 取得後の actual rate limit / error path verify

---

## 8. F scope: cost 管理 logic

### 8.1 monthly budget alert (= dual model 統合)
- threshold: **$5** (= warn) / **$10** (= halt_review) / **$20** (= emergency_stop + 信長殿通達)
- Auto Recharge **OFF** retain (= 信長殿明示、両 API key、課金暴走防止)

### 8.2 累積 cost log (= dual model 統合)
- 各 call の `provider` + `model_id` + `prompt_token` + `image_token` + `推定 cost` を累積
- 1 日 / 7 日 / 30 日 aggregate query (= Phase 3 で SQL or yaml aggregate)
- dual model cost 比較 (= per-image cost / per-token cost、Phase 3 機械 verify 後 table 確定)

### 8.3 stop logic sketch
- threshold $20 超過時: provider 内で `raise` + alert log + 信長殿通達 path (= Phase 3)

---

## 9. G scope: DentalBI integration point sketch

### 9.1 連動先
- `teriha_passport_engine` の boss / 敵 record に `image_url` + `image_provider` + `image_model_id` field 追加 candidate
- `passport_dino_battle_log` record との連動

### 9.2 schema migration sketch (= Phase 3 別 step)
```sql
-- Phase 3 で apply、本 Phase 2 では sketch only
ALTER TABLE teriha_passport_engine
  ADD COLUMN IF NOT EXISTS image_url text,
  ADD COLUMN IF NOT EXISTS image_provider text,         -- = 'openai' / 'google'
  ADD COLUMN IF NOT EXISTS image_model_id text,         -- = 'gpt-image-2' / 'gemini-3.1-flash-image-preview' / 'gemini-2.5-flash-image'
  ADD COLUMN IF NOT EXISTS image_seed_id text,
  ADD COLUMN IF NOT EXISTS image_generated_at timestamptz;
```

### 9.3 scope out (= Phase 3)
- 実 migration apply / 実 record insert / 実 url 反映

---

## 10. 100 体生成 plan (= dual model 用途別 routing 適用)

### 10.1 batch 計画 (= dual model 配分案)
- **batch1**: 5-10 体 PoC = gpt-image-2 (= 5 階級 × 1-2 element、キャラクター品質基準確立)
- **batch2-5**: 30-40 体 = gpt-image-2 (= 主要キャラ高品質)
- **batch6-N**: 50-60 体 = gemini-3.1-flash-image-preview (= reference 14 で既存キャラ + 背景 + props 組合せ、複雑 composition)
- **量産検証 batch**: gemini-2.5-flash-image (= 低 cost retain candidate、Phase 3 cost 検証後)

### 10.2 5 階級 + element prompt template (= v1-v3 retain、dual model 共通)

| rank | 和名 | age_tier | 雰囲気 |
|------|------|----------|--------|
| tamago | 卵 | 3-5 歳 | 可愛い、丸い、笑顔 |
| hiyoko | 雛 | 5-7 歳 | 元気、軽やか |
| bokensha | 冒険者 | 7-10 歳 | 探検、勇敢 |
| yusha | 勇者 | 10-12 歳 | 強い、決意 |
| okoku_senshi | 王国戦士 | 12+ | 重装、王者 |

element: 火 / 水 / 草 / 雷 / 氷 / 光 / 闇 等 6-8 種。

### 10.3 QC gate 観点
- safety_level (= 小児向け、暴力/流血 minimum) + 5 階級分布 + element 分布 + dual model 用途別品質 + cost / image (= 想定内か)

---

## 11. Supabase Storage bucket 設計 (= dual model 統合)

- **bucket name**: `dino-enemies` (= 100 体敵キャラ専用) / `patient-illustrations` (= PWA illustration 汎用)
- **path convention**: `{bucket}/{provider}/{model_id}/{rank}/{element}/{seed-id}.png` (= 例: `dino-enemies/openai/gpt-image-2/tamago/fire/seed-001.png`)
- **metadata 連動**: `image_provider` + `image_model_id` 追加 (= §9.2)
- **size budget**: 各画像 ~1-2 MB、100 体 = 100-200 MB retain
- **scope out**: 実 bucket create / 実 upload (= Phase 3)

---

## 12. 2 guard 明示 (= 黒田規範整合、v2 update wording)

### 12.1 guard #1: context/dentalbi.md 不在
- `context/dentalbi.md` は **不在 confirmed** (= 2026-05-13 09:44 retract note 整合)
- 本 spec の input source として **読まない / 参照しない**

### 12.2 guard #2: Phase 2 全禁 + boundary 明確化 (= v2 update、AC 整合)

**Phase 2 で 禁 (= SDK 真実 client + live operation)**:
- SDK 真実 client object instantiation (= `openai.OpenAI(api_key=...)` / `google.generativeai.GenerativeModel(...)` / `genai.Client(...)` 等の live network 接続)
- live API call (= `images.generate(...)` / `generateContent(...)` 等)
- 画像生成 (= 実画像 byte の生成)
- Supabase upload (= 実 bucket upload)
- DentalBI schema migration apply (= 実 ALTER TABLE)
- cost 課金 (= 実 OpenAI / Google 課金 trigger)

**Phase 2 で 可 (= 必達)**:
- **local mock ImageProvider class** (= openai / gemini provider 各 class 定義、AC 整合)
- **placeholder stub function** (= generate / cost_log 等の signature retain)
- **abstraction interface 実装** (= Protocol / Base class 定義)
- mock + placeholder の return dict 構造

**注 (= 旧 Rule 11 wording の正)**: 旧 v1 spec の「object 生成全禁」wording は誤、本 AC を正として **SDK 真実 client only 禁、local mock provider class は実装要**。

---

## 13. Rule 11 ashigaru 責務境界遵守 evidence

| 行為 | Phase 2 (本 task) | Phase 3 (= 別 step、両 API key 取得後信長殿明示承認下) |
|------|-------------------|-----------------------------------------------------|
| spec markdown 起案 (= dual model) | ✓ 実施 | — |
| ImageProvider abstraction + 各 provider mock class | ✓ 実施 (= local mock のみ) | — |
| pytest skeleton (= dual model + abstraction + routing、SKIP=0) | ✓ 実施 (= mock only) | — |
| Supabase migration sketch (= dual model field) | ✓ 実施 (= sketch only) | — |
| SDK 真実 client (= openai.OpenAI / google.generativeai.GenerativeModel) | ✗ 禁 | ✓ 実施 candidate |
| 実 API call | ✗ 禁 | ✓ 実施 candidate |
| 実画像生成 | ✗ 禁 | ✓ 実施 candidate |
| 実 Supabase upload | ✗ 禁 | ✓ 実施 candidate |
| 実 schema migration apply | ✗ 禁 | ✓ 実施 candidate |
| 実 cost 課金 | ✗ 禁 | ✓ 実施 candidate |

---

## 14. API key leak 防止 evidence

- env var `OPENAI_API_KEY` + `GOOGLE_AI_API_KEY` 経由のみ受領
- code literal hard-code **禁**
- log 出力 **禁** (= retry/error log でも key 文字列を含めない)
- 絶対 path leak **禁** (= placeholder `<DENTALBI_REPO_ROOT>` 等使用)
- skeleton + sketch 内も `OPENAI_API_KEY` / `GOOGLE_AI_API_KEY` literal を含む文字列出力なし

---

## 15. 5-10 年運用想定

- **モデル選定**: gpt-image-2 GA + Performance Highest retain (= deprecate risk 低) + gemini-3.1-flash-image-preview (= preview ゆえ GA 昇格 path 監視) + gemini-2.5-flash-image stable retain candidate
- **abstraction layer**: ImageProvider Protocol で SDK / model 切替容易性 retain (= 将来 SOTA 切替時の蹴り出し path)
- **cost 抑制**: Auto Recharge OFF retain + threshold alert ($5/$10/$20) + dual model cost 比較 plan (= 用途別最適化)
- **schema 拡張性**: `image_provider` + `image_model_id` field 追加 (= 既 record 互換、provider 切替 trace 可)
- **API key rotation path**: env var 経由、両 key rotation 容易性 retain
- **5 階級 enum 拡張性**: tamago / hiyoko / bokensha / yusha / okoku_senshi、将来 rank 追加可

---

## 16. 連帯失策 retain reflection note (= 黒田 v1 fail P0 fix #1 整合、本能寺戒め integrity 維持)

**2026-05-13 dual model 戦略確定までの連続補正 path retain (= 拙者 + 信長殿 + 黒田 + ashigaru5 全員 SoT 三点照合不足 reflection)**:

1. **10:03 第 1 補正**: 旧モデル ID `gpt-image-1<半角ドット>5` literal で v1 spec 起案 (= 公式 catalog 未照合) → b22914c commit、shogun_verified=true 取得後 SoT 不一致発覚
2. **11:36 第 2 補正**: gpt-image-2 GA 確認 → 6f62fa7 (model 補正 cycle)
3. **11:50 第 3 補正**: 陛下御差配「gpt-image-2 と Nano Banana 2 を使用する事」 → dual model 戦略確定
4. **12:04 第 4 補正 (本 cycle)**: 信長殿 task_directive 経由 dual model 拡張、本 v4 spec 起案

**教訓 retain**:
- SoT 三点照合 strict 適用必達 (= Rule 11 拡張 v2 ⑰⑱⑲ 整合)
- 公式 docs WebFetch 機械 verify (= prompt 文中の claim を裏取り)
- 旧モデル ID literal は **本 reflection note 内のみ retain** (= `gpt-image-1<半角ドット>5`、コード/spec body 内全件 gpt-image-2 / gemini-3.1-flash-image-preview / gemini-2.5-flash-image のみ、grep `gpt-image-1.5` = 0 件 in code、retain note のみ in reflection section)
- 本能寺戒め integrity 維持 (= 連帯失策の透明性 retain)

---

## 17. 手順 (= 本 cycle task 全体)

1. AC0 既装備 inventory (= 3 file 現状 + 両 model 公式 docs WebFetch 機械 verify + 14 枚 claim verify + 前 cycle commit chain) ✓ 完遂
2. ImageProvider abstraction layer 設計 (= §4)
3. spec markdown 起案 (= 本 doc、dual model + abstraction + routing + cost) ✓ 完遂
4. `scripts/openai_image_client.py` abstraction 化 (= §5)
5. `scripts/gemini_image_client.py` 新規 (= §6)
6. `tests/test_cmd016_dual_model_skeleton.py` rename + extension (= §7、SKIP=0、git mv 履歴 link)
7. cost 管理 logic + Auto Recharge OFF reminder + threshold alert (= §8)
8. DentalBI integration sketch (= §9)
9. privacy gate (= HIGH=0 WARN accepted_warn、絶対 path leak 禁、API key never log)
10. F007 整合 commit (= author=ashigaru5 適正、git config local 既設定済)
11. push 前 Rule 12 整合 verify (= git fetch newbuild main + git log で divergent check)
12. gunshi audit_request + karo report_received 投函 (= shogun 直送禁、家老経由)

---

## 18. 終わりに

本 spec は **Phase 2 dual model spec design + abstraction + sketch + skeleton only**。実 API call / 実画像生成 / 実 Supabase upload / 実 DentalBI migration / 実 cost 課金 は Phase 3 (= 両 API key 取得後信長殿明示承認下別 step)。陛下御願 web 側 step 完遂 wait、その間 Phase 2 で dual model path 確立。Rule 11 ashigaru 責務境界遵守、F002 + 高 cost risk 防止。連帯失策 retain reflection で本能寺戒め integrity 維持、加賀百万石 self-fix model + Rule 6 freshness 教訓重ね適用。
