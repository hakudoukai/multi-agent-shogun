# Dashboard Layer B Phase 層 render component (= cmd_020 sub-section)

**Status**: ashigaru2 起案 v0.1、subtask_cmd020_dashboard_layer_b_phase_render
**Parent design**: `docs/dashboard_design_v0.1.md §2 Layer B` (= 主 source、Phase 層 3 区分 原本) + `docs/dashboard_design_v0.2.md §3.6` (= progress 算出式 + 色分け 4 段階 原本) + `docs/dashboard_design_v0.2.md §4.1` (= drill-down mockup)
**Scope**: 本 doc は **Layer B Phase 層単独 sub-section markdown render component**。Layer A は `docs/dashboard_layer_a_kousou.md` (= ashigaru1 起案) 既存、Layer C-F は別 task。
**Repo**: multi-agent-shogun-newbuild (= hakudokai-dev は本 task 範囲外)
**MC 統合**: MC `regenerate_dashboard.py` 等 generator artifact 本 SC repo 内不在 (= `find` 0 件)。本 doc は SC docs 起案のみ、SoT 統合 interface (= 家康 + 秀吉合議 + MC SoT 統合 path) は後段別 task。
**live data**: Supabase `development_progress` table への live fetch は本 task 範囲外 (= delivery_cond #4 整合)。本 doc は **schema + anchor 提示のみ**、live data render は後段 generator 責任。

---

## 1. 設計原典 anchor (= source-of-truth)

| anchor | source | 用途 |
|---|---|---|
| `docs/dashboard_design_v0.1.md` §2 Layer B | 本 repo (= 信長起草 2026-05-11) | Phase 層 3 区分 (= 完了 / 進行中 / 未着手) 原本 |
| `docs/dashboard_design_v0.2.md` §3.6 | 本 repo (= 黒田 audit #5 反映) | `progress_pct` 算出式 + weight + 色分け 4 段階 原本 |
| `docs/dashboard_design_v0.2.md` §4.1 | 本 repo (= 拙者 (黒田) 補強 mockup) | HTML drill-down mockup (= Layer B Phase 層 70% 例) |
| Supabase `development_progress` table | 外部 (= 50+ records、Supabase fetch 想定) | 本体 live data source (= 後段 generator 責任) |

---

## 2. Phase 層 3 区分 (= v0.1 §2 Layer B retain、phase A-E + W4-W17 anchor)

Layer B Phase 層は development_progress 50+ records を「完了 / 進行中 / 未着手」の 3 区分で grouping する。各 record の leaf `progress_pct` は §3 算出式で機械判定する。

### 2.1 Phase 層 3 区分 table

| 大項目 | 中項目 | 小項目 (= record level) |
|---|---|---|
| **完了 Phase** | phase1-6 / phaseB / phaseC / phaseD | 各 phase の week + pc + commit_hash |
| **進行中 Phase** | phase_a_id_unification / phase_b_karte_loader | task 一覧 + status + assignee |
| **未着手 Phase** | P2-engine 蜘蛛の糸 (169 件) / POST-deploy (= 朝礼 / CTI / 外部 API / 書式 Lv3 / 材料 / 人事 / 全院展開) | 個別 task anchor |

= **本 table は `docs/dashboard_design_v0.1.md §2 Layer B` を Layer B sub-section として再 render したもの**。

### 2.2 phase A / B / C / D / E 命名対応 anchor

development_progress table 内 phase 群は実装 history 上 `phase A`, `phase B`, `phase C`, `phase D`, `phase E` の 5 群に大別される。本 sub-section は **anchor 提示のみ**、本体 record 一覧は live data render (= 後段 generator) 担当。

| phase 群 | 主要 anchor | 主要 record (= v0.1 §2 Layer B retain) | 担当 ashigaru anchor |
|---|---|---|---|
| **phase A** | phase_a_id_unification 系 | ID 統一 phase (= 進行中) | 後段 generator が live fetch |
| **phase B** | phaseB 予約ソフト + phase_b_karte_loader | W4-W5 完了 (= 予約ソフト) + karte loader 進行中 | 後段 generator が live fetch |
| **phase C** | phaseC 患者アプリ 延伸 | W6 + cmd_004 hardening 進行中 | 後段 generator が live fetch |
| **phase D** | phaseD 完了 phase 群 | 過去完了 phase records | 後段 generator が live fetch |
| **phase E** | P2-engine 蜘蛛の糸 + POST-deploy 系 | 未着手 phase records | 後段 generator が live fetch |

= 本 anchor 提示は **schema only**、live data fetch + ashigaru 担当 inventory は後段 generator 責任 (= delivery_cond #4 整合、live data 未取得時 sample/schema 扱い)。

### 2.3 cmd_004 W4-W17 phase window anchor (= cmd_004 二大戦線 hardening)

cmd_004 二大戦線 (= 会計待ちゼロ / 小児恐竜王国 / 申し送りエンジン / 第一段階 PDF) は development_progress 内で **W4-W17** の week 範囲に集中する。本 sub-section は phase window anchor 提示のみ、本体 record 一覧は Layer C 機能層担当 sub-section。

| W phase anchor | 主要内容 | 連携 Layer |
|---|---|---|
| **W4** | phaseB 予約ソフト 完了 (= cmd_004 hardening 起点) | Layer C 会計待ちゼロ |
| **W5** | 予約ソフト + cmd_004 周辺機能 完了 | Layer C 周辺機能 |
| **W6** | phaseC 患者アプリ 延伸 開始 (= cmd_004 hardening 主戦場) | Layer C 患者アプリ + 小児恐竜王国 |
| **W7-W12** | cmd_004 ceremony_event API + tier_up celebration + engagement_analytics + access_control hardening 等 連続 phase | Layer C 小児恐竜王国 + 申し送りエンジン |
| **W13-W17** | cmd_004 hardening 完遂 phase (= 5-10 年運用想定 根本治療品質) | Layer C 全域 + Layer D 蜘蛛の糸接続 |

= **W4 から W17 までの phase window は cmd_004 二大戦線 hardening 期間**、本 Layer B sub-section は window anchor のみ、record 本体は Layer C 担当。

---

## 3. progress 算出式 (= v0.2 §3.6 retain、機械判定)

各 leaf phase の `progress_pct` は以下の機械判定式で算出する。親 node の `progress_pct` は子の加重平均で算出する。

### 3.1 progress_pct 算出式 (= v0.2 §3.6 完全 retain)

```
progress_pct(node) = (
  sum(weight(子) × progress_pct(子)) / sum(weight(子))
) for 親 node

progress_pct(leaf) =
  100  if shogun_verified=true AND completion_gate=open AND evidence_state=complete
  100  if status=done AND verdict=pass AND audited_done=true
   75  if status=done AND verdict=pass_with_concerns
   50  if status=in_progress
   25  if status=assigned AND task_id present
    0  if status=not_started OR blocked
```

**weight**: 機能 / phase に陛下御差配 priority (= A 生命線=3、B 必須=2、C 先送り=1)、未指定なら 1。

### 3.2 progress_pct field 配置 (= development_progress table 想定 schema)

各 record (= leaf phase) は以下 field を持つ想定 (= live data render 時 generator が Supabase fetch):

| field | 用途 | source |
|---|---|---|
| `phase_id` | record 主 key (= phase_a_id_unification 等) | development_progress.phase_id |
| `status` | not_started / assigned / in_progress / done / blocked | development_progress.status |
| `verdict` | pass / pass_with_concerns / fail / pending | gunshi audit report |
| `progress_pct` | §3.1 算出式の結果 (= 0/25/50/75/100 のいずれか) | 機械判定 |
| `commit_hash` | leaf 完了時の git SHA | ashigaru commit |
| `担当 ashigaru` | record owner (= ashigaru1-7 等) | task YAML assigned_to |
| `shogun_verified` | true / false | shogun_verified gate |
| `completion_gate` | open / blocked | gate state |
| `evidence_state` | complete / partial / missing | audit evidence |

= **本 sub-section は schema anchor のみ**、live data render は後段 generator が `development_progress` table から fetch して埋込。

---

## 4. 色分け 4 段階 (= v0.2 §3.6 retain、4 levels)

progress_pct 値に応じて以下 4 段階の色分けを適用する (= v0.2 §3.6 完全 retain):

| 色 | mark | progress_pct 範囲 | 意味 |
|---|---|---|---|
| **green** | ✅ | 100% | 完遂 (= shogun_verified=true OR done+pass+audited) |
| **yellow** | 🟡 | 50-99% | 進行中 (= 50% in_progress OR 75% pass_with_concerns) |
| **orange** | (色名) | 25-49% | assigned 段階 (= task_id present、未着手作業前) |
| **red** | 🔴 | 0-24% or blocked | 未着手 OR blocked |

= **4 段階 (green / yellow / orange / red)** の色分けは leaf phase + 親 node 両方に適用、HTML render 時 `<progress>` element + CSS class で機械描画 (= v0.2 §4.1 mockup 参照)。

---

## 5. development_progress table reference anchor (= Supabase access 想定)

本 Layer B sub-section の **本体 live data source** は Supabase `development_progress` table。本 doc は anchor + schema 提示のみ、live fetch は後段 generator 担当。

### 5.1 development_progress table reference anchor

- **table 名**: `development_progress`
- **record 数**: 50+ (= v0.2 §3.2 query budget retain、軽 <1KB、full fetch 毎回 OK)
- **access 経路**: `mcp__claude_ai_Supabase__execute_sql` (= v0.2 §3.1)
- **fetch 想定 SQL**: `SELECT phase_id, status, verdict, progress_pct, commit_hash, assigned_to, shogun_verified, completion_gate, evidence_state FROM development_progress ORDER BY phase_id;`
- **本 sub-section の責任**: anchor + schema 提示のみ
- **後段 generator の責任**: live fetch + Layer B sub-section 内 record 一覧 render

### 5.2 live data 未取得時の扱い (= delivery_cond #4 整合)

live data 未取得時は **sample / schema 扱い** (= delivery_cond #4)、live data 取得済 claim 禁。本 doc 起案時点 (= 2026-05-12) は live fetch 未実施、schema + anchor のみ retain。

---

## 6. cross-layer reference anchor

本 Layer B sub-section から他 Layer への接続 anchor は以下:

- **Layer A 構想層** (= `docs/dashboard_layer_a_kousou.md` 既起案): 5 階層 + 10 柱 + 蜘蛛の糸 anchor、本 Layer B はその実装 phase 層
- **Layer C 機能層** (= 別 sub-section): cmd_004 二大戦線 W4-W17 record 本体は Layer C 担当、本 Layer B は phase window anchor のみ
- **Layer D 頭脳層** (= 別 sub-section): 蜘蛛の糸 8,000+ records 本体は Layer D 担当、本 Layer B は P2-engine 蜘蛛の糸 (169 件) anchor のみ
- **Layer E 運用層** (= 別 sub-section): ashigaru 稼働状態 + commit_hash → 担当 ashigaru の link 先
- **Layer F 規範層** (= 別 sub-section): F007 push 履歴 + 規範 entity reference

= 本 sub-section は **Phase 層 anchor + schema only**、本体は各 Layer 担当 sub-section に委譲する (= 単一責任、self-contained)。

---

## 7. 既知の限界 + 後段別 task

| 限界 | 対応 |
|---|---|
| `development_progress` table live fetch | 本 sub-section は anchor + schema のみ、live data render は後段 generator 別 task (= delivery_cond #4 整合) |
| MC `regenerate_dashboard.py` 等 generator artifact 本 SC repo 不在 (= commit 72f1c0d は MC 側) | 家康 + 秀吉合議結果着後 別 task で SoT 統合 verify、本 doc は anchor のみ (= delivery_cond #2 整合) |
| phase A-E 命名と development_progress 実 record の対応 | 後段 generator が live fetch 時 phase prefix grouping、本 doc は anchor のみ |
| cmd_004 W4-W17 record 本体 | Layer C 機能層担当 sub-section に委譲、本 Layer B は phase window anchor のみ |
| progress_pct 算出 fallback (= shogun_verified=false かつ status=done) | v0.2 §3.6 open question Q14、本 sub-section は式 retain のみ、fallback ruling は別 task |

---

## 8. 起案完了基準 (= 本 sub-section AC alignment)

- `phase A` / `phase B` / `phase C` / `phase D` / `phase E` の 5 群 anchor 存在 (= §2.2)
- `progress_pct` field + 算出式 syntax 存在 (= §3.1 + §3.2)
- `development_progress` table reference anchor 存在 (= §5.1)
- 色分け 4 段階 `green` / `yellow` / `orange` / `red` 全件 reference 存在 (= §4)
- `W4` 〜 `W17` phase window anchor 存在 (= §2.3)

= 上記 5 anchor を含む単独 markdown であり、`scripts/test/test_dashboard_layer_b_static_contract.py` で機械検証する。

---

*起案: ashigaru2、2026-05-12T11:25、parent design v0.1 §2 Layer B 主 source + v0.2 §3.6 progress 算出式 + §4.1 drill-down mockup retain*
