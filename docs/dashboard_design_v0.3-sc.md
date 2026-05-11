# DentalBI Dashboard 自動化 + project 管理 設計書 v0.3-sc (= cmd_020、SC 視点強化 + 4 人合議 round 2 集約)

**Status**: 家康 v0.3 起草 (= SC 視点)、兄上 v0.3 起草と並列、round 3 合議想定
**Author**: 家康 (= SC shogun)
**Round 3 review 待ち**: 兄上 (= 信長 MC shogun v0.3 統合) + 本多 + 直政 + 黒田
**変更点 vs v0.2**: 直政 audit 5 懸念解消 + 拙者 review 改善 5 件反映 + Q11-Q15 全回答 + SC 視点 4 項追加 + AC18 新規

---

## 0. 変更履歴

| Version | 日時 | 主要変更 |
|---|---|---|
| v0.1 | 2026-05-11 19:25 | 信長 初版起草、6 Layer + AC 10 + 開放問 10 |
| v0.2 | 2026-05-11 19:40 | 黒田 7 修正点反映 + 信長 8 補強 |
| **v0.3-sc** | **2026-05-11 22:10** | **家康 SC 視点起草: 直政 5 懸念解消 + 拙者 5 改善 + Q11-Q15 回答 + SC 視点 4 項 + AC18** |

## 1. v0.2 base retain

§1-§7 構造は v0.2 から retain。本 v0.3-sc は v0.2 上に懸念解消 + 改善 patch を重ね、v0.4 統合時に兄上 MC 版と merge 想定。

## 2. 直政 audit 5 懸念解消 (= naomasa_council_dashboard_v02_round2)

### 2.1 §3.5 dashboard writer 規範変更の適用順序 (= 懸念 #1 解消)

**新規 適用順序 5 段**:
1. **周知 phase** (= migration day-0): karo + gunshi + ashigaru 全員に「dashboard.md 直接編集禁、state source (= queue/reports/) 書込のみ」 inbox broadcast、ack 受領
2. **既 dashboard.md backup** (= day-0): `cp dashboard.md dashboard.md.legacy_<timestamp>`、git commit、不可逆 backup
3. **generator 初回実行** (= day-0): `regenerate_dashboard.py` 実行、新 dashboard.md 生成、既版との diff 確認、結果 yaml 記録
4. **parallel monitoring 1 週間** (= day-1〜7): 各 cycle で karo + gunshi の手動編集検出 (= git log + author check)、即 detect で当該 agent に再周知
5. **cutover verify** (= day-7): 1 週間 0 件手動編集 verify、dashboard.md.legacy archive、generator 単独 writer 確定

**順序破棄 fallback**: 段 1 周知 ack 不在 / 段 3 diff 異常時 → cutover 中止、原状復帰 (= dashboard.md.legacy reset)、root cause 解明後再着手

### 2.2 §3.1 REST + anon + RLS table 別 policy 詳細 (= 懸念 #2 解消)

**RLS policy 表** (= table 別、anon 読権限定義):

| Table | anon SELECT 権限 | filter 条件 | 理由 |
|---|---|---|---|
| `development_progress` | ✅ allow | (none) | 開発進捗 public、PII なし |
| `legal_sources` | ✅ allow | `is_public=true` | 公開法令のみ、内部メモ除外 |
| `legal_source_linkages` | ✅ allow | (none) | linking metadata のみ、source 本体は別 RLS |
| `inspection_checklists` | ✅ allow | (none) | 検査 template、PII なし |
| `inspection_findings` | 🟡 limited | `severity != 'critical'` | critical findings は service_role のみ |
| `procedure_codes_audit` | ✅ allow | (none) | 公開 audit、PII なし |
| `project_documents` | 🟡 limited | `is_internal=false` | 内部 design doc 除外 |
| `design_decisions` | ✅ allow | (none) | 公開 DD のみ |
| `form_templates` | ✅ allow | (none) | form metadata、PII なし |

**実装**: `supabase/migrations/<timestamp>_dashboard_rls.sql` で各 table の anon policy 設定、generator は anon key で REST GET、PII 含 row は自動除外。

### 2.3 §3.2 query budget <100KB/cycle 計算根拠 (= 懸念 #3 解消)

**diff fetch 効果計算**:

| Table | full size | 想定変更頻度 | diff fetch size | 月 query (15min × 96 cycle/day × 30 day) |
|---|---|---|---|---|
| `legal_sources` (500KB) | 1,600 row × ~300B/row | 5 行/day | ~1.5KB/cycle | ~4.3MB/月 |
| `legal_source_linkages` (1MB) | 3,235 row × ~300B/row | 20 行/day | ~6KB/cycle | ~17MB/月 |
| `inspection_checklists` (中) | 2,495 row | 10 行/day | ~3KB/cycle | ~8.6MB/月 |
| `project_documents` (中) | 60+ row、metadata only | 2 行/day | ~600B/cycle | ~1.7MB/月 |
| 他 5 table (full fetch) | 各 <1KB | full each cycle | ~5KB/cycle | ~14MB/月 |
| **累計** | - | - | **~16KB/cycle** | **~46MB/月** |

**結論**: <100KB/cycle 達成 (= 平均 16KB/cycle)、月 46MB は Supabase 無料 tier 余裕 (= 月 50GB egress 制限の <0.1%)、課金 risk 0。

**ETag + updated_at 併用** (= 拙者改善案): ETag mismatch + updated_at filter で更に diff 縮小、上記表は conservative estimate。

### 2.4 §3.6 progress blocked precedence 定義 (= 懸念 #4 + 拙者改善 統合)

**precedence rule** (= top-down):
1. status=blocked OR (cycle=7 AND escalation_required=true) → **0% (red 🔴)**
2. status=in_progress AND escalation_required=true → **25% (orange)** (= 進捗あれども stuck 降格)
3. shogun_verified=true AND completion_gate=open AND evidence_state=complete → **100% (green ✅)**
4. status=done AND verdict=pass AND audited_done=true → **100% (green ✅)**
5. status=done AND verdict=pass AND shogun_verified=false → **75% (yellow)** (= verify 待ち、Q14 回答整合)
6. status=done AND verdict=pass_with_concerns → **75% (yellow)**
7. status=in_progress → **50% (yellow)**
8. status=assigned AND task_id present → **25% (orange)**
9. status=not_started → **0% (red 🔴)**

**色分け 4 段階**:
- 🟢 green: 100%
- 🟡 yellow: 50-99%
- 🟠 orange: 25-49%
- 🔴 red: 0-24% or blocked

### 2.5 AC18 escalation alert verify 追加 (= 懸念 #5 解消、拙者提案整合)

**AC18**:
- 両 PC HEAD 不一致 detect 時、alert 発火 verify (= 例: dashboard 上部に「⚠️ HEAD divergent: SC=xxx MC=yyy」 banner 表示)
- 月 Supabase query cost >10MB 接近時、alert 発火 (= dashboard footer に「⚠️ query budget 80% 接近」)
- cycle=7 escalation_required=true 全件で alert 発火 (= 該当 leaf node に 🚨 icon + 兄上/陛下に inbox 通知)
- alert 仕組み自体の test (= 既知 trigger 条件を artificial inject、alert 発火確認、weekly self-check)

## 3. Q11-Q15 全回答 (= 拙者 review + v0.3 確定)

### Q11. mermaid 自動更新方法

**採用**: text-based markdown 埋込

generator が dashboard.md 生成時に mermaid block (= ``` ```mermaid ... ``` ```) を inline 埋込、ブラウザ側で mermaid.js が render。pre-rendered SVG cache は HTML load 高速化目的なら別 phase で検討 (= Stage 4+ optional)、初期は markdown 埋込で simple。

### Q12. weight 設定

**採用**: A=3 / B=2 / C=1 加重平均

陛下御差配「会計待ちゼロ + 小児恐竜王国 = 生命線 (= 優先度 A)」整合、A 高重みで全体 progress に大きく寄与。weight 未指定なら 1 (= 既存)。

実装: leaf node に `priority: A|B|C` field、parent node の progress 算出時 `weight = {A:3, B:2, C:1}.get(priority, 1)` で加重平均。

### Q13. ttyd 認証 token 共有

**採用**: **個別** (= MC/SC 別 token)

両 PC 同一 token は漏洩時の blast radius 増。MC/SC で別 token、`config/ttyd_auth.env` を git ignored で各 PC 独自管理 (= 既装備整合、漏洩 detection 容易)。

### Q14. progress fallback (shogun_verified=false かつ status=done)

**採用**: **75% (yellow)**

verdict=pass_with_concerns と同等、家康 4 項 verify 未完で残 25%、verify 完遂で 100% 化。50% (= in_progress と同色 yellow) は done 達成感欠落、75% で「done だが verify 待ち」明示が UX 良。本 v0.3 §2.4 precedence rule #5 反映済。

### Q15. dashboard 自身の memory MCP entity 化

**採用**: ✅ cmd_020 完遂後

entity 名: `dashboard_self_renewable` (= mechanism)
observations:
- AC1-18 全件 PASS evidence (= 各 AC の verify commit hash + timestamp)
- v1.0 確定 commit hash
- 両 PC retain 確認 (= MC/SC 同 entity name + 同 observations)
- generator + viewer 動作確認 commit hash

両 PC retain で memory MCP shared knowledge graph に追加、cmd_020 audit trail 永続化。

## 4. SC 視点強化 4 項 (= 拙者 review SC 視点 2 + 追加 2)

### 4.1 香椎照葉実証 leaf 表示 (= SC 視点 #1)

dashboard Layer C 機能層内、leaf node として「香椎照葉実証 phase」を配置、25 form 全件アクセス検証 task 進捗 (= clinic_id=5) を可視化。実装→現場検証→運用の chain を「実装」 leaf と「実証」 leaf で分離表示、運用 readiness 別途 track。

実装: `development_progress` table に `validation_phase=kashiiteruha` の entries、generator で Layer C 内に dedicated section 生成。

### 4.2 25 form 展開可能性 (= SC 視点 #2)

申し送りエンジン UI pattern (= トンカツ・ハマカツ多階層タップ) が成功した場合、25 form 全体への template 化展開を Layer A 構想層に future state として表示。Stage 2 で template 化 task 起案可、Layer A drill-down で「現状: 1 form (申し送り) / 将来: 25 form」明示。

### 4.3 HEAD sync 強化 (= SC 視点 #3、AC16 細分化)

両 PC HEAD 一致 verify を auto-git-sync.timer 5min cycle に加え、**dashboard.md hash 一致**も別途 verify。不一致時 (= 例: 本日 21:01 auto_git_sync ESCALATION の divergent 状態) は dashboard 上部に「⚠️ HEAD divergent」 banner、AC18 alert 発火条件第 1 項として扱う。

実装: generator が両 PC HEAD 取得 (= MC へ ssh で git rev-parse HEAD or Supabase 経由メタデータ table) + dashboard.md SHA256 計算、不一致 detect で alert。

### 4.4 commit 重複検出 logic 装備 (= 拙者 21:01 escalation 教訓)

本日 SC + MC が同 deliverable (= alternative_inventory + AC0 inventory) を独立 commit + push で divergent 発生 (= msg_210107)。根本治療: pre-commit hook で MC との commit message + diff 重複 check、duplicate detect 時 commit 中止 + warning。

実装: `scripts/hooks/pre-commit-dup-check.sh` 起案、両 PC 配備、`.git/hooks/pre-commit` から call。Stage 6 検証 phase で実装、Stage 5 systemd 装備時の事前 check 系列。

## 5. Acceptance Criteria (= v0.2 17 + AC18 新規 = 18 件)

| AC | 条件 |
|---|---|
| AC1-10 | v0.1 retain |
| AC11-17 | v0.2 retain (= 黒田反映、本 v0.3 §2-§4 で詳細化済) |
| **AC18 (new)** | escalation alert verify: HEAD 不一致 / 月 query cost >10MB 接近 / cycle=7 escalation 全件で alert 発火 + 仕組み自己 test (weekly self-check) |

## 6. v0.3-sc 反映 map (= 直政 audit 5 懸念 + 拙者 5 改善 + Q11-Q15 + SC 視点 4)

| 起源 | v0.3-sc section | 対応 |
|---|---|---|
| 直政 #1 §3.5 適用順序 | §2.1 | ✅ 5 段順序定義 + fallback |
| 直政 #2 §3.1 RLS policy | §2.2 | ✅ table 別 policy 表 + 実装 path |
| 直政 #3 §3.2 query budget 計算根拠 | §2.3 | ✅ table 別 diff fetch + 月計算 |
| 直政 #4 §3.6 blocked precedence | §2.4 | ✅ 9 段 precedence rule + 4 色 |
| 直政 #5 AC18 未追加 | §2.5 / §5 | ✅ AC18 定義 + 仕組み test |
| 拙者 #1 ETag + updated_at 併用 | §2.3 | ✅ conservative estimate 反映 |
| 拙者 #2 blocked 状態降格 | §2.4 rule #2 | ✅ in_progress + escalation → 25% |
| 拙者 #3 4 階層 collapsed default | (v0.2 §4.1 retain、運用判断) | 🟡 generator default 設定 |
| 拙者 #4 alpha test stage | (Stage 2-3 間追加要、Stage 配置検討) | 🟡 v0.4 統合時に Stage 2.5 追加検討 |
| 拙者 #5 git diff 自動 verify | §2.1 段 4 | ✅ parallel monitoring に組込 |
| Q11 mermaid 自動更新 | §3.Q11 | ✅ markdown 埋込 |
| Q12 weight | §3.Q12 | ✅ A=3/B=2/C=1 |
| Q13 ttyd token | §3.Q13 | ✅ 個別 |
| Q14 progress fallback | §3.Q14 / §2.4 rule #5 | ✅ 75% |
| Q15 self memory MCP entity | §3.Q15 | ✅ dashboard_self_renewable |
| SC 視点 #1 香椎照葉 leaf | §4.1 | ✅ Layer C 内配置 |
| SC 視点 #2 25 form 展開 | §4.2 | ✅ Layer A future state |
| SC 視点 #3 HEAD sync 強化 | §4.3 | ✅ AC18 alert 第 1 項 |
| SC 視点 #4 commit 重複検出 (= 拙者 21:01 教訓) | §4.4 | ✅ pre-commit hook Stage 6 |

## 7. v0.4 統合 protocol (= 兄上 MC v0.3 と SC v0.3-sc merge)

```
家康 v0.3-sc (= 本 doc) 起草 + push
  ↓ 並列
兄上 v0.3-mc 起草 + push (= 兄上前送「v0.3 起草 30-60 分後」)
  ↓
兄上 integrate v0.3-sc + v0.3-mc → v0.4 (= 兄上主導 merge)
  ↓
4 人 + 黒田 round 3 review (= v0.4)
  ↓
全員 verdict=pass → v1.0 確定 → MC ashigaru Stage 2 配信
```

期限: v0.3-sc 完遂 22:30 目安、v0.4 統合 23:00 目安、v1.0 確定 23:30〜00:00 目安。

## 8. 開放問 (= v0.3-sc 残)

v0.2 Q11-Q15 全解消、v0.3-sc 新規開放問なし。v0.4 統合時に兄上 v0.3-mc との merge conflict 解消で新規問発生する可能性あり。

---

*v0.3-sc 起草: 家康 (SC shogun)、2026-05-11T22:15、SC 視点 + 直政 audit 反映 + 拙者 review 確定*
