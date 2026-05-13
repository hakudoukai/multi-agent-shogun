# Dashboard Status Classification Logic (= cmd_020 補助 stream A 正本)

**Status**: ashigaru7 起案 v0.1、subtask_cmd020_dashboard_status_classification_logic
**Parent design**: `docs/dashboard_design_v0.2.md §3.6` (= progress 算出式 + 色分け 4 段階 原本) + `queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml` (= 3 分類 semantic 原本) + `queue/reports/naomasa_unverified_audit_batch1_20260512.yaml` (= audited-blocked 12 件 verdict 原本)
**Scope**: 本 doc は **dashboard status classification logic 正本** = task-state axis × progress-percent axis の 2 軸 直交関係 + 3 分類 (implementation_required / monitor / manifest_pending) visual 信号色 + pass_with_concerns visual rule + audited-blocked 12 件 status 整合 table。既 `scripts/regenerate_dashboard.py` constants + functions を改変せず、参照 anchor として位置付ける canonical doc。
**Repo**: multi-agent-shogun-newbuild (= hakudokai-dev は本 task 範囲外)
**MC 統合**: MC 側 generator (= `scripts/regenerate_dashboard.py`) への classification field 追加可否は本 doc 起案後の別 task で 4 人合議。本 doc は SC docs 起案のみ。

---

## 1. 設計原典 anchor (= source-of-truth)

| anchor | source | 用途 |
|---|---|---|
| `docs/dashboard_design_v0.2.md` §3.6 | 本 repo (= 信長起草 + 黒田 audit 反映) | progress 算出式 + 色分け 4 段階 原本 (= green/yellow/orange/red) |
| `docs/dashboard_design_v0.2.md` §3.5 | 本 repo | generator 単独 writer 規範、本 doc 利用側 |
| `scripts/regenerate_dashboard.py` `PROGRESS_COLOR_TIERS` | 本 repo (= L182-187) | progress %-based tier mapping (= 既装備) |
| `scripts/regenerate_dashboard.py` `STATUS_STAGE_PCT` | 本 repo (= L116-129) | status string → progress % mapping (= 既装備) |
| `scripts/regenerate_dashboard.py` `progress_color_tier()` | 本 repo (= L544-549) | tier lookup function (= 既装備) |
| `scripts/regenerate_dashboard.py` `LAYER_CHILDREN` | 本 repo (= L194-510) | 6 Layer 子項目 mapping、12 件 audited-blocked id 登録元 |
| `queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml` | 本 repo | 3 分類 semantic (= supabase_not_started_14 + w11_in_progress_2 + w9_batch7_1) 原本 |
| `queue/reports/naomasa_unverified_audit_batch1_20260512.yaml` | 本 repo | audited-blocked 12 件 audit verdict 原本 |

---

## 2. 2 軸 直交モデル (= task-state axis × progress-percent axis)

dashboard 内の status 表示は **直交する 2 軸** で構成される。本 doc では両軸を明確化し、既装備 (= progress %-based tier) と本 doc 起案 (= task-state classification) の関係性を canonical 化する。

### 2.1 Axis A: progress-percent axis (= 既装備)

`PROGRESS_COLOR_TIERS` で定義される **進捗 % → tier** 4 段階 mapping。

| min_pct | emoji | label | css_class |
|---|---|---|---|
| 80.0+ | 🟢 green | verified | `tier-green` |
| 50.0-79.9 | 🟡 yellow | in_flight | `tier-yellow` |
| 25.0-49.9 | 🟠 orange | early | `tier-orange` |
| 0-24.9 | 🔴 red | stalled | `tier-red` |

= `docs/dashboard_design_v0.2.md §3.6` 色分け 4 段階 retain、`scripts/regenerate_dashboard.py PROGRESS_COLOR_TIERS` で既装備、本 doc では参照 anchor only、改変しない。

### 2.2 Axis B: task-state axis (= 本 doc 起案 3 分類)

`naomasa_sc_audit_phase2_status_green_path` で同定された **task lifecycle state → 分類** 3 段階 mapping。Axis A とは直交、status / verdict / commit / shogun_verify 等の machine evidence から決定される。

| classification | visual signal | trigger condition | 該当する状況 |
|---|---|---|---|
| **implementation_required** | 🔴 red | status=not_started + commit empty + shogun_verify_entry_exists=false | 実装 backlog、設計 + 実装 + test + audit を要する。audit alone では緑化不能。 |
| **monitor** | 🟡 yellow with trigger | status=in_progress + commit empty + completion trigger 設定済 | 進行中、completion trigger (= external_status becomes completed + commit_hash non-empty) 設定で監視。trigger 発火後即 post-completion audit 流入。 |
| **manifest_pending** | 🟠 orange with W9 ref | source_exists=false (= W9 manifest 等の source artifact 欠落) + shogun_verify_entry_exists=true | source 系 artifact (= W9 manifest 等) が SC repo 内不在、機械 audit 不能。manifest 公開 / push を要する。 |

### 2.3 2 軸 直交性 (= 重複ではなく独立)

- **Axis A** は **数値 (= progress %)** → tier、計算順序 = `compute_child_machine_state(child) → pct → progress_color_tier(pct) → tier dict`。
- **Axis B** は **記号 (= state label)** → classification、計算順序 = task YAML / Supabase row machine evidence → 3 分類のいずれか / N/A。
- **直交性**: 1 つの child は両軸の値を持つ。例: `C-V21-W9TENSU` は Axis A で `pct=0.0 → red tier`、Axis B で `implementation_required` (= 偶然両軸とも red、但し意味は別)。
- **重複回避規範**: Axis B は Axis A の代替ではなく **補完**。dashboard render では両軸を併記する事を推奨 (= progress bar 色 + classification badge)、片方のみ表示は禁止しない。

---

## 3. pass_with_concerns visual rule (= green ではなく yellow conditional 表示)

### 3.1 既装備の確認

`scripts/regenerate_dashboard.py` の **verdict_based_score_mapping** (= L2042-2070) で pass_with_concerns は **score=75** に紐付く。Axis A の `PROGRESS_COLOR_TIERS` を経由すると `75 ≥ 50 → yellow` で yellow tier に解決される (= 既装備、参照 anchor only)。

```python
# scripts/regenerate_dashboard.py L2042-2070 (= 引用、改変なし)
# c) verdict.startswith('pass_with')             -> 75
elif task.verdict.startswith("pass_with"):
    score = 75.0
```

= **pass_with_concerns → 75 → yellow** が機械的に成立。

### 3.2 規範化: pass_with_concerns ≠ green

本 doc では **pass_with_concerns は green として render してはならない** 規範を明文化する。理由:

1. `pass_with_concerns` は **concerns (= 懸念事項) 残置** を含意し、shogun_verified=true の clean pass とは性質が異なる。
2. clean pass (= verdict=pass + shogun_verified=true) → 100 → green (= 完全緑化) と区別すべき。
3. `dashboard_design_v0.2.md §3.6` の green tier (= 100%) には到達せず、yellow tier (= 50-99%) に留まる事が機械的に保証される (= 75 < 80 のため green tier 入域不能)。

### 3.3 yellow conditional 表示 condition

pass_with_concerns 子項目を yellow tier で render する際は以下 condition を遵守:

| condition | 内容 |
|---|---|
| **A** | `concerns_note` field を必ず併記 (= 懸念事項を user に開示) |
| **B** | shogun_verified=true との **後段 escalation path** を明示 (= concerns 解消 → clean pass → 100 → green への path) |
| **C** | yellow tier 内でも `tier-yellow` css_class で render、emoji=🟡 固定 (= ad-hoc な ⚠️ 等 fallback 禁) |

### 3.4 反例 (= 違反 pattern)

| 違反 | 内容 | 訂正 |
|---|---|---|
| ❌ | `pass_with_concerns` を 🟢 green で render | 🟡 yellow conditional 表示 + concerns_note 併記 |
| ❌ | concerns_note 無しで yellow render | concerns_note を audit report から transcribe |
| ❌ | `pass_with_concerns` を 100% として加重平均に計上 | 75% で加重平均 (= 既装備の verdict_based_score_mapping 整合) |

---

## 4. audited-blocked 12 件 status 整合 verify table

`queue/reports/naomasa_unverified_audit_batch1_20260512.yaml` (= 2026-05-12 audit 原本) で audit 済の 12 件全件を本 table に列挙し、本 doc の Axis B classification と整合確認する。本 12 件は **全件緑化不能** (= overall_completion_gate=blocked) の状態で、本 doc の 3 分類で説明できる事を機械検証する。

### 4.1 12 件全件 anchor table

| # | candidate_id | label (短縮) | inventory_status | classification | visual signal | audit verdict | source artifact 状態 |
|---|---|---|---|---|---|---|---|
| 1 | **C-15-A** | W9 Stage A foundation 9 件 | n/a (= manifest 欠落) | **manifest_pending** | 🟠 orange with W9 ref | fail (= evidence_state=missing) | `w9_design_tasks_169.yaml` 欠落 |
| 2 | **C-15-B2** | W9 batch2 ui_logic 28 | n/a | **manifest_pending** | 🟠 orange with W9 ref | fail (= missing) | manifest 欠落 |
| 3 | **C-15-B4** | W9 batch4 validation 18 | n/a | **manifest_pending** | 🟠 orange with W9 ref | fail (= missing) | manifest 欠落 |
| 4 | **C-15-B6** | W9 batch6 補綴系 19 | n/a | **manifest_pending** | 🟠 orange with W9 ref | fail (= missing) | manifest 欠落 |
| 5 | **C-V21-W9TENSU** | W9 全処置セット点数確認 | not_started | **implementation_required** | 🔴 red | fail | commit empty + shogun_verify entry absent |
| 6 | **C-V29-W11DDA** | W11 DD-054 Phase A ID 統一 | in_progress | **monitor** | 🟡 yellow with trigger | fail | commit empty、completion trigger 待ち |
| 7 | **C-V31-W11CHOREI** | W11 朝礼フル版 Phase1-4 | not_started | **implementation_required** | 🔴 red | fail | commit empty |
| 8 | **C-V34-W13VISIT** | W13 訪問 Phase4-7 | not_started | **implementation_required** | 🔴 red | fail | commit empty |
| 9 | **C-V36-W14PAY** | W14 ペイライト 実 API 接続 | not_started | **implementation_required** | 🔴 red | fail | commit empty |
| 10 | **C-V38-W14LINE** | W14 LINE 通知 + Web 予約実接続 | not_started | **implementation_required** | 🔴 red | fail | commit empty |
| 11 | **C-V41-W15DEP** | W15 D-2 デプロイ + Tailscale | not_started | **implementation_required** | 🔴 red | fail | commit empty |
| 12 | **C-V43-W16MAT** | W16 材料管理 | not_started | **implementation_required** | 🔴 red | fail | commit empty |

### 4.2 分類別 件数 整合

| classification | count | task YAML 規範 文言 mapping |
|---|---|---|
| **manifest_pending** | 4 (= #1-#4) | "4 件 W9 pass_with_concerns/open_with_concerns" |
| **implementation_required** | 7 (= #5, #7-#12) | "8 件 fail/blocked" のうち 7 件 (= not_started 系) |
| **monitor** | 1 (= #6) | "8 件 fail/blocked" のうち 1 件 (= in_progress + empty commit) |
| **合計** | **12** | task YAML 明示 12 件と整合 |

= 4 + 7 + 1 = **12**、`naomasa_unverified_audit_batch1_20260512` 12 件 + task YAML 文言「8 件 fail/blocked + 4 件 W9」と整合。本 table は static test (= test_audited_blocked_12_items_listed) で 12 件 id existence assert + classification mapping assert する。

### 4.3 12 件全件 緑化 path (= green path、後段)

| classification | 緑化 path |
|---|---|
| **manifest_pending** | MC が `w9_design_tasks_169.yaml` を git-track + push → SC pull → Stage A/batches 1-6 内容抽出 → karo が ashigaru 配分 (= 実装 + test) → gunshi post-completion audit → shogun verify → green |
| **implementation_required** | karo 配分 → ashigaru 実装 (= 設計 + 実装 + test) → gunshi audit → shogun verify → completion_gate=open → audited_done → green |
| **monitor** | external_status=completed + commit_hash non-empty 検出 → karo 配分 (= post-completion audit) → gunshi audit (= 10-15 min) → shogun verify → green |

= 12 件全件、本 doc 起案後の **別 task chain** で逐次緑化進行。本 task scope は doc + test 起案のみ。

---

## 5. Layer C/D render との integration anchor

### 5.1 Layer C 機能層 classification anchor

`docs/dashboard_layer_c_function.md` (= ashigaru3 既起案) は **機能 anchor + 構造 + 接続 only** が責務。本 doc は Layer C と直交 (= status classification 軸は機能 anchor 軸とは別)。Layer C markdown に本 doc への小さな cross-layer reference anchor を追加する (= §6 末尾追記)、Layer C 内既 anchor 構造は維持。

Layer C 内 reference 配置:
- `docs/dashboard_layer_c_function.md` §6 cross-layer reference anchor 末尾に "Status classification logic (= `docs/dashboard_status_classification_logic.md`)" anchor を追加。

### 5.2 Layer D 頭脳層 classification anchor

`docs/dashboard_layer_d_zunou.md` (= ashigaru4 既起案) は **法令 8,000+ records + cross-layer 接続 anchor** が責務。Layer D 子項目 (= legal_sources / linkages 等) は audited-blocked 12 件に含まれない (= Supabase 全 record 緑、Layer D 自体の classification は **verified**)、但し 12 件のうち W9 系 4 件は Layer C 内 child だが、概念的には Layer D 蜘蛛の糸 (= 法令 W9) へ接続するため、Layer D 内に cross-layer reference anchor を追加する。

Layer D 内 reference 配置:
- `docs/dashboard_layer_d_zunou.md` §6 cross-layer reference anchor 末尾に "Status classification logic (= `docs/dashboard_status_classification_logic.md`)" anchor を追加。

### 5.3 並行 rendering path 起案禁

本 doc は既 `scripts/regenerate_dashboard.py` constants + functions を **改変せず、参照 anchor only** とする。Layer C/D markdown も既 anchor 構造 + 既 test contract を維持し、本 doc 内容は markdown 末尾の小さな cross-layer reference 1 行追加のみ。

= naomasa pre_audit msg_20260513_134905 concerns 整合: "Layer C/D render edits could conflict with existing LAYER_CHILDREN and progress aggregation. Require focused static tests against existing constants/functions rather than a new parallel rendering path."

---

## 6. cross-layer reference anchor

本 doc から他 Layer / artifact への接続 anchor は以下:

- **Axis A 既装備**: `scripts/regenerate_dashboard.py` L182-187 (= PROGRESS_COLOR_TIERS) + L544-549 (= progress_color_tier function) + L116-129 (= STATUS_STAGE_PCT) + L2042-2070 (= verdict_based_score_mapping)
- **Axis B 12 件 source**: `queue/reports/naomasa_unverified_audit_batch1_20260512.yaml` (= audit verdict 原本) + `queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml` (= 3 分類 semantic 原本)
- **Layer C 機能層**: `docs/dashboard_layer_c_function.md` §6 (= cross-layer reference 配置先)
- **Layer D 頭脳層**: `docs/dashboard_layer_d_zunou.md` §6 (= cross-layer reference 配置先)
- **Layer A 構想層**: `docs/dashboard_layer_a_kousou.md` (= 構造のみ、status classification 無関係、touch せず)
- **Layer B Phase 層**: `docs/dashboard_layer_b_phase.md` (= 既装備の Supabase development_progress 経由、本 doc は phase status 整合に間接接続)
- **dashboard.md**: 本 doc 範囲外 (= generator 単独 writer 規範 + delivery_conditions 4 件 #1 で直接編集禁)

---

## 7. 既知の限界 + 後段別 task

| 限界 | 対応 |
|---|---|
| MC 側 `scripts/regenerate_dashboard.py` への classification field 追加可否 | 本 doc 起案後の 4 人合議 + 別 task で判断、本 task scope は SC docs only |
| W9 manifest (`queue/manifests/w9_design_tasks_169.yaml`) 欠落の解消 | MC owner、本 doc は manifest_pending 4 件の status を canonical 化するのみ、manifest 公開は別 task |
| audited-blocked 12 件の緑化 | 各 classification 別の green path (= §4.3) を別 task chain で進行、本 task は doc 起案のみ |
| dashboard.html / dashboard.md 内 visual signal の実 render | 既装備 (= `progress_color_tier` + `progress_bar_html`) を活用、本 doc は classification 軸の意味付け正本 |
| `pass_with_concerns` 以外の verdict variant (= `pass_with_conditions`) | 既 verdict_based_score_mapping で pass_with_* prefix で同一扱い (= 75 score)、本 doc は概念的に pass_with_concerns で代表表現 |

---

## 8. 起案完了基準 (= 本 doc AC alignment)

- **§2 2 軸 直交モデル** section (= Axis A + Axis B + 直交性) 存在
- **§3 pass_with_concerns visual rule** (= green ではなく yellow conditional 表示 規範) 存在、`pass_with_concerns` 文字列 + `yellow` 文字列を双方含む
- **§4 audited-blocked 12 件 status 整合 verify table** 存在、12 件 id (= C-15-A, C-15-B2, C-15-B4, C-15-B6, C-V21-W9TENSU, C-V29-W11DDA, C-V31-W11CHOREI, C-V34-W13VISIT, C-V36-W14PAY, C-V38-W14LINE, C-V41-W15DEP, C-V43-W16MAT) 全件 anchor + 各 classification mapping
- **3 分類 anchor**: `implementation_required` / `monitor` / `manifest_pending` 文字列を本 doc 内に全件含む
- **visual signal anchor**: `red` / `yellow` / `orange` / `green` 4 段階を本 doc 内に全件含む (= Axis A 4 tier + Axis B 3 分類で共通 color 語彙)
- **既装備参照 anchor**: `PROGRESS_COLOR_TIERS` + `STATUS_STAGE_PCT` + `progress_color_tier` 既存 constant / function 文字列を本 doc 内に含む (= 改変せず参照 anchor only)

= 上記 6 anchor 群を含む単独 markdown であり、`scripts/test/test_subtask_cmd020_dashboard_status_classification_logic_static_contract.py` で機械検証する。

---

*起案: ashigaru7、2026-05-13T14:45、parent design v0.2 §3.6 + naomasa audit batch1 + sc_audit_phase2 source-of-truth、naomasa pre_audit concerns 整合 (= AC0 inventory + 並行 rendering path 禁 + focused static test on existing constants)*
