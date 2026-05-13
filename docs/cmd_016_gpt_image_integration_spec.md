# cmd_016 OpenAI gpt-image-1.5 integration Phase 2 spec design

- task_id: subtask_cmd016_gpt_image_2_integration_phase2_spec_design
- parent_cmd: cmd_016「OpenAI gpt-image-1.5 integration (= 小児恐竜王国 100 体敵キャラ画像生成 path)」
- parent_directive: msg_20260513_094017_48ec9256 + msg_20260513_094655_c2f4705c
- bloom_level: L4 (= grouped 7 観点 spec)
- author: ashigaru5 (蒲生氏郷 persona、子飼い若手、文武両道、教養派)
- 起案日: 2026-05-13
- base_commit: 79f96e7 (= 起案時 HEAD、確認は git log で随時)
- 範囲: **Phase 2 spec design only**。実 API call / 実画像生成 / 実 Supabase upload / 実 DentalBI schema migration / 実 cost 課金 は **Phase 3 (= 別 step、API key 取得後起案後のみ)**。
- 連動資産:
  - `docs/cmd004_ai_chat_spec.md` (= 既装着 spec pattern 範本)
  - `docs/cmd004_dinosaur_100enemies_spec.md` (= 100 体生成 plan 連動)
  - `queue/reports/ashigaru4_pending_implementation_9_inventory_report.yaml` (= DentalBI integration point 候補 9 件 inventory)
  - `scripts/extract_dentalbi_form_inventory.py` (= DentalBI form inventory script、実在)
  - `scripts/sync_to_supabase.sh` (= 既装着 sync utility、Phase 3 で連動 candidate)

---

## 0. Anti-Duplication: 参照済み正本 / 不参照

| # | 正本 | 所在 | 利用方法 |
|---|------|------|----------|
| A | `~/.openai_venv/` (= openai 2.36.0 install 完遂) | MainPC venv | Phase 3 client wrapper の実行環境 |
| B | `scripts/sync_to_supabase.sh` | repo 内既装着 | Phase 3 で Supabase Storage upload と連動 candidate |
| C | `docs/cmd004_*_spec.md` (= ai_chat / dinosaur_100enemies 等) | repo 内既装着 | 本 spec の section 構成 pattern 範本 |
| D | `queue/reports/ashigaru4_pending_implementation_9_inventory_report.yaml` (= 9 件 inventory) | repo 内既装着 | DentalBI integration point 候補 SoT |
| E | OpenAI 公式 docs (= https://developers.openai.com/api/docs/models/gpt-image-1.5) | 外部 SaaS | モデル ID + parameters + pricing SoT |

**Anti-duplication retract note (= 黒田 v2 guard #1 整合):**
- `context/dentalbi.md` = 不在 (= 2026-05-13 09:44 confirmed)、本 spec の context source として **入力扱い禁**。
- 代替 source = `queue/reports/ashigaru4_pending_implementation_9_inventory_report.yaml` + `scripts/extract_dentalbi_form_inventory.py` + repo 既装着 spec のみ。

**本 spec で扱わない (= scope out / Rule 11 boundary):**
- 実 OpenAI API call (= Phase 3 別 step、本 spec 全 chapter で禁)
- 実 Supabase Storage upload (= Phase 3 別 step)
- 実 DentalBI schema migration apply (= Phase 3 別 step、本 spec は sketch のみ)
- 実 cost 課金 (= API key wait + 信長殿明示承認下 Phase 3)
- frontend UI ビジュアル (= デザイン班専権)

---

## 1. 目的 + scope

### 1.1 目的
小児恐竜王国 100 体敵キャラ画像生成 + 患者 PWA illustration を **OpenAI gpt-image-1.5** で path 確立。5-10 年運用想定、cost 抑制 (= Auto Recharge OFF retain + threshold alert)、API key 漏洩防止、Rule 11 ashigaru 責務境界遵守。

### 1.2 scope (= bloom L4 grouped 7 観点)
A. spec markdown 起案 (= 本 doc)
B. prompt template 5 階級 parameter 化 + 100 体生成 plan
C. Supabase Storage bucket 設計
D. API client wrapper 設計 (= sketch only、mock/placeholder のみ)
E. DentalBI integration point 設計 (= schema migration sketch only)
F. cost 管理 logic (= monthly budget alert + Auto Recharge OFF retain)
G. pytest skeleton (= module test 設計、SKIP=0、API key 取得後 enable path)

### 1.3 scope out (= Rule 11 boundary、本 task で行わない)
- 実 OpenAI client object 生成 / 実 API call / 実画像生成
- 実 Supabase Storage upload / 実 bucket create
- 実 DentalBI schema migration apply / 実 record insert
- 実 cost 課金 / 実 API key 環境変数 set

---

## 2. 制約 + 公式 docs evidence (= 4 evidence retain 必達)

### 2.1 evidence #1 確認日
2026-05-13 (= 本 task 着手日)

### 2.2 evidence #2 公式 docs URL
- メイン: `https://developers.openai.com/api/docs/models/gpt-image-1.5` (= GA 確認)
- 補助: `https://developers.openai.com/api/docs/models/gpt-image-1` (= previous model 確認)
- pricing 参照: `https://openai.com/api/pricing/`
- 検索 hit (= search evidence): `https://platform.openai.com/docs/models/gpt-image-1.5` (= 公式 model page、auth 要)
- 注: `platform.openai.com` の docs は public WebFetch が 403、`developers.openai.com/api/docs/models/<id>` は public 閲覧可

### 2.3 evidence #3 gpt-image-1.5 primary 選定理由
- **GA (General Availability)** status (= 公式 model card)
- **latest flagship** (= 公式 model catalog で「main current image model」明示)
- **parameters 整合** = `model` + `prompt` + `n` + `size` (1024x1024 / 1024x1536 / 1536x1024) + `quality` (low / medium / high) 等、本 spec 100 体生成 use case と整合
- **pricing 妥当** = low $0.009-$0.013 / medium $0.034-$0.05 / high $0.133-$0.20 per image (= 公式 model card)
- **endpoint** = `/v1/images/generations` + `/v1/images/edits` (= 公式 model card)
- **5-10 年運用想定整合** = GA + latest = 中長期 deprecate risk 低 (= gpt-image-1 は deprecated 表記、参考)

### 2.4 evidence #4 fallback/pricing 根拠
- **gpt-image-1** (= previous model, deprecated):
  - low $0.011 / medium $0.042 / high $0.167 per image
  - 採用 condition: gpt-image-1.5 障害時の transient fallback 候補 (= Phase 3 で retry/error handling sketch に組み込み candidate)
- **gpt-image-1-mini** (= 50-70% cheaper):
  - low $0.005 / medium $0.011 / high $0.036 per image
  - 採用 condition: 高 volume / cost-sensitive batch (= 100 体 PoC で実 cost 検証後、batch2-N で考慮 candidate)
- **token-based 追加 cost** (= edit workflow + multi-image reference):
  - text token: input $5/M, cached input $1.25/M, output $10/M
  - image token: input $8/M, cached input $2/M, output $32/M
  - 本 spec PoC 5-10 体は **per-image fee dominant**、token cost は negligible 想定

### 2.5 その他制約
- **Auto Recharge OFF retain** (= 信長殿明示、課金暴走防止)
- **Organization Verification** = 陛下御願 web 側 step retain (= 最大 1 日 wait、Phase 2 spec 起案は並行 progress 可)
- **API key 漏洩防止** = env var `OPENAI_API_KEY` 経由のみ、コード literal hard-code 禁、log 出力禁
- **5-10 年運用想定** = radical_solution_during_development_rule 整合、根本治療品質

---

## 3. A scope: spec yaml 起案 (= 本 markdown 自体)

本 markdown 全体が A scope deliverable。yaml 混在禁 (= markdown one source、表記揺れ修正)。A-G 7 観点全件記載。

---

## 4. B scope: prompt template 5 階級 + 100 体生成 plan

### 4.1 5 階級 parameter 化
| rank | 和名 | age_tier 想定 | 雰囲気 |
|------|------|---------------|--------|
| tamago | 卵 | 3-5 歳 | 可愛い、丸い、笑顔 |
| hiyoko | 雛 | 5-7 歳 | 元気、軽やか、子供向け |
| bokensha | 冒険者 | 7-10 歳 | 探検、勇敢、装備あり |
| yusha | 勇者 | 10-12 歳 | 強い、決意、輝き |
| okoku_senshi | 王国戦士 | 12+ | 重装、王者、伝説 |

### 4.2 prompt parameter 共通
- `rank` (= 5 階級 enum)
- `age_tier` (= 上記対応)
- `element` (= 火 / 水 / 草 / 雷 / 氷 / 光 / 闇 等、6-8 種類)
- `atmosphere` (= 雰囲気 free text、safety_level integrated)
- `safety_level` (= 小児向け 必達、暴力 minimum、流血禁、武器表現 stylized only)

### 4.3 sample prompt 5 階級 × 1-2 種類 = 5-10 体 PoC seed
- **tamago × 火**: "A cute round dinosaur egg with small flame decorations, friendly smile, soft cartoon style, suitable for children aged 3-5, no violence, no blood, bright colors"
- **tamago × 水**: "A cute round dinosaur egg with water droplet patterns, gentle expression, soft cartoon style, suitable for children aged 3-5, no violence, calm blue tones"
- **hiyoko × 草**: "A small hatched baby dinosaur with leaf accessories, cheerful expression, lively cartoon style, suitable for children aged 5-7, no violence, fresh green colors"
- **bokensha × 雷**: "A young adventurer dinosaur with stylized lightning equipment, brave pose, adventure cartoon style, suitable for children aged 7-10, stylized weapons only, no blood"
- **yusha × 光**: "A heroic dinosaur warrior with glowing light aura, determined expression, stylized fantasy cartoon, suitable for children aged 10-12, stylized weapons, no graphic violence"
- **okoku_senshi × 闇**: "A legendary kingdom warrior dinosaur with stylized dark armor, majestic stance, fantasy cartoon style, suitable for children aged 12+, stylized weapons only, no blood, dramatic but child-safe"

### 4.4 100 体生成 plan
- **batch1**: 5-10 体 PoC (= 上記 sample seed) → QC gate (= ashigaru + 信長殿 verify)
- **batch2-N**: 残 90-95 体 (= QC pass 後、batch size = 10-20 体ずつ、cost log 検証しつつ)
- **QC gate 観点** = safety_level (= 小児向け、暴力/流血 minimum) + 5 階級分布 + element 分布 + cost / image (= 想定内か)

---

## 5. C scope: Supabase Storage bucket 設計

### 5.1 bucket 設計案
- **bucket name 候補**: `dino-enemies` (= 100 体敵キャラ専用) / `patient-illustrations` (= PWA illustration 汎用)
- **path convention**: `{bucket}/{rank}/{element}/{seed-id}.png` (= 例: `dino-enemies/tamago/fire/seed-001.png`)
- **metadata 連動**: teriha_passport_engine record の image_url field と連動 (= 5.2 参照)
- **URL 生成**: 初期は `public read` (= 小児恐竜王国は公開素材性質) / 患者 PWA 連動素材は `signed URL` (= 個人情報含む場合)
- **size budget**: 各画像 ~1-2 MB retain (= gpt-image-1.5 1024x1024 png 想定)、100 体 = 100-200 MB retain

### 5.2 metadata schema sketch
- column: `image_url` (= text、Supabase Storage public URL)
- column: `prompt_seed_id` (= text、prompt template の seed identifier)
- column: `rank` + `element` + `safety_level` (= filter/group 用 metadata)
- column: `generated_at` (= timestamptz、QC 用)

### 5.3 scope out (= Phase 3)
- 実 bucket create / 実 upload / 実 RLS policy 設定 (= migration apply は Phase 3)

---

## 6. D scope: API client wrapper sketch

### 6.1 file: `scripts/openai_image_client.py`
- **本 Phase 2 で実 OpenAI client object 生成禁** (= 黒田 v2 guard #2 整合)
- skeleton = mock / placeholder のみ、`print` + `return placeholder` で構造のみ retain

### 6.2 入力
- `prompt: str` (= template-built prompt)
- `n: int = 1`
- `size: str = "1024x1024"` (= 1024x1536 / 1536x1024 切替可)
- `quality: str = "medium"` (= low/medium/high)
- `model: str = "gpt-image-1.5"` (= 公式実在 ID literal)

### 6.3 出力 (= Phase 3 実装後)
- image URL (= Supabase Storage upload 後) or binary (= temp)

### 6.4 env var 受領 path
- `OPENAI_API_KEY` (= .env 経由、placeholder only、log 禁、literal hard-code 禁)

### 6.5 retry/error handling sketch
- **rate limit** (= 429): exponential backoff retry (= sketch only、実装 Phase 3)
- **transient error** (= 5xx): max 3 retry (= sketch only)
- **permanent failure** (= 4xx 401/403): raise + alert log (= API key invalid / org verification 未完遂)
- **fallback** (= gpt-image-1 / gpt-image-1-mini): primary 持続障害時の candidate (= Phase 3 で設計判断)

### 6.6 cost log sketch
- 各 call の `model` + `size` + `quality` + `n` + 推定 cost (= 公式 pricing table lookup)
- 出力先: `queue/reports/openai_image_cost_log.yaml` or Supabase table (= Phase 3 確定)

---

## 7. E scope: DentalBI integration point 設計

### 7.1 連動先
- `teriha_passport_engine` の boss / 敵 record に `image_url` field 追加 candidate
- `passport_dino_battle_log` record との連動 (= 敵キャラ画像 retain)
- 既存 stub (= ashigaru4 inventory 9 件、C-V21 等 dino battle stubs) との互換性 retain

### 7.2 schema migration sketch (= Phase 3 別 step)
```sql
-- Phase 3 で apply、本 Phase 2 では sketch only
ALTER TABLE teriha_passport_engine
  ADD COLUMN IF NOT EXISTS image_url text,
  ADD COLUMN IF NOT EXISTS image_seed_id text,
  ADD COLUMN IF NOT EXISTS image_generated_at timestamptz;
```

### 7.3 scope out (= Phase 3)
- 実 migration apply / 実 record insert / 実 url 反映

---

## 8. F scope: cost 管理 logic

### 8.1 monthly budget alert
- threshold: **$5** (= warning) / **$10** (= halt review) / **$20** (= emergency stop + 信長殿通達)
- Auto Recharge **OFF** retain (= 信長殿明示、課金暴走防止)

### 8.2 累積 cost log
- 各 call の `推定 cost` を累積 (= cost log SoT)
- 1 日 / 7 日 / 30 日 aggregate query (= Phase 3 で SQL or yaml aggregate)

### 8.3 stop logic sketch
- threshold $20 超過時: client wrapper 内で `raise` + alert log + 信長殿通達 path (= Phase 3 で実装)

### 8.4 daily/monthly aggregate
- daily: `sum(cost) GROUP BY DATE(generated_at)`
- monthly: `sum(cost) GROUP BY DATE_TRUNC('month', generated_at)`

---

## 9. G scope: pytest skeleton

### 9.1 file: `tests/test_cmd016_gpt_image_skeleton.py`
- module test skeleton (= prompt template validation / client wrapper mock / cost log retain)
- **SKIP=0 厳守** (= 黒田規範整合、skip は容認禁)
- 本 Phase 2 では mock + placeholder のみ、API key 取得後 (= Phase 3) で mock → 実 call 切替 path 明示

### 9.2 test cases (= 本 Phase 2 skeleton)
1. `test_prompt_template_rank_enum` (= 5 階級 enum 検証)
2. `test_prompt_template_safety_keyword_retain` (= 暴力/流血 keyword 不在 verify)
3. `test_client_wrapper_signature` (= function signature spec 整合)
4. `test_client_wrapper_env_var_read` (= env var 受領 path 検証、API key literal hard-code 禁 verify)
5. `test_cost_log_schema` (= cost log entry schema 検証)

### 9.3 enable path (= Phase 3)
- mock → 実 call 切替 (= `unittest.mock` patch → 実 OpenAI client 切替)
- API key (= env var) 取得後の actual rate limit / error path verify

---

## 10. 手順 (= 本 Phase 2 task 全体)

1. AC0 既装備 inventory (= openai library 2.36.0 install + 既装着 spec pattern + Supabase Storage migration 既装着 + .env retain pattern + 公式 docs evidence retain) ✓ 完遂
2. spec markdown 起案 (= 本 doc、A-G 7 観点全件記載) ✓ 完遂
3. prompt template 5 階級 sample + 100 体 plan (= §4) ✓ 完遂
4. Supabase Storage bucket 設計案 (= §5) ✓ 完遂
5. API client wrapper sketch (= `scripts/openai_image_client.py` skeleton) → §6
6. cost 管理 logic + Auto Recharge OFF reminder + threshold alert (= §8) ✓ 完遂
7. pytest skeleton (= `tests/test_cmd016_gpt_image_skeleton.py`、SKIP=0) → §9
8. privacy gate (= HIGH=0 WARN accepted_warn、絶対 path leak 禁、API key never log)
9. F007 整合 commit (= author 適正、新規 spec + scripts + tests file modify)
10. push 前 Rule 12 整合 verify (= git fetch newbuild main + git log で divergent check)
11. gunshi audit_request + karo report_received 投函 (= shogun 直送禁、家老経由)

---

## 11. 2 guard 明示 (= 黒田 pre-audit v2 必達)

### 11.1 guard #1: context/dentalbi.md 不在
- `context/dentalbi.md` は **不在 confirmed** (= 2026-05-13 09:44 retract note 整合)
- 本 spec の input source として **読まない / 参照しない**
- 代替 source = `queue/reports/ashigaru4_pending_implementation_9_inventory_report.yaml` + `scripts/extract_dentalbi_form_inventory.py` + repo 既装着 spec のみ

### 11.2 guard #2: Phase 2 全禁 (= live API call + 関連実操作)
本 Phase 2 task で **以下全件禁**:
- OpenAI client object 生成 (= `openai.OpenAI(...)` instantiation も禁)
- live API call (= `images.generate(...)` / `images.edit(...)` 等)
- 画像生成 (= 実画像 byte の生成)
- Supabase upload (= 実 bucket upload)
- DentalBI schema migration apply (= 実 ALTER TABLE)
- cost 課金 (= 実 OpenAI 課金 trigger)

`scripts/openai_image_client.py` skeleton 内も `print` + `return placeholder` のみ、`openai.OpenAI(...)` 等の **instantiation も禁**。`tests/test_cmd016_gpt_image_skeleton.py` も mock + placeholder のみ。

---

## 12. Rule 11 ashigaru 責務境界遵守 evidence

| 行為 | Phase 2 (本 task) | Phase 3 (= 別 step、API key 取得後信長殿明示承認下) |
|------|-------------------|-----------------------------------------------------|
| spec markdown 起案 | ✓ 実施 | — |
| API client sketch (mock) | ✓ 実施 (= mock/placeholder only) | — |
| pytest skeleton (mock) | ✓ 実施 (= SKIP=0、mock only) | — |
| Supabase migration sketch | ✓ 実施 (= sketch only) | — |
| 実 OpenAI client 生成 | ✗ 禁 | ✓ 実施 candidate |
| 実 API call | ✗ 禁 | ✓ 実施 candidate |
| 実画像生成 | ✗ 禁 | ✓ 実施 candidate |
| 実 Supabase upload | ✗ 禁 | ✓ 実施 candidate |
| 実 schema migration apply | ✗ 禁 | ✓ 実施 candidate |
| 実 cost 課金 | ✗ 禁 | ✓ 実施 candidate |

---

## 13. API key leak 防止 evidence

- env var `OPENAI_API_KEY` 経由のみ受領
- code literal hard-code **禁**
- log 出力 **禁** (= retry/error log でも API key 文字列を含めない)
- 絶対 path leak **禁** (= placeholder `<DENTALBI_REPO_ROOT>` 等使用)
- skeleton + sketch 内も `OPENAI_API_KEY` literal を含む文字列出力なし

---

## 14. 5-10 年運用想定

- **モデル選定**: GA + latest flagship retain (= deprecate risk 低)
- **fallback path**: gpt-image-1 + gpt-image-1-mini retain (= primary 障害時の retry/error handling sketch)
- **cost 抑制**: Auto Recharge OFF retain + threshold alert ($5/$10/$20)
- **schema 拡張性**: `image_url` + `image_seed_id` + `image_generated_at` field 追加 (= 既 record 互換)
- **API key rotation path**: env var 経由、rotation 容易性 retain
- **5 階級 enum 拡張性**: tamago / hiyoko / bokensha / yusha / okoku_senshi、将来 rank 追加可

---

## 15. 終わりに

本 spec は **Phase 2 spec design only**。実 API call / 実画像生成 / 実 Supabase upload / 実 DentalBI migration / 実 cost 課金 は Phase 3 (= API key 取得後信長殿明示承認下別 step)。陛下御願 web 側 step 1-4 (= API key + credit + Auto Recharge OFF + Org Verification) 完遂 wait、その間 Phase 2 spec で path 確立。Rule 11 ashigaru 責務境界遵守、F002 + 高 cost risk 防止。
