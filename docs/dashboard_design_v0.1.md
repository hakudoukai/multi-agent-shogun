# DentalBI Dashboard 自動化 + project 管理 設計書 v0.1 (= cmd_020)

**Status**: 信長 v0.1 起草、黒田 9 観点 + 10 lens audit 待ち、4 人合議 round 1
**Author**: 信長 (= MC shogun)
**Round 1 review 待ち**: 黒田 (= MC gunshi codex audit) + 家康 (= SC shogun) + 本多 (= SC karo) + 直政 (= SC gunshi codex 加合議)
**陛下御差配 2026-05-11**: 「DentalBI 全体 + 蜘蛛の糸連携 + 大中小項目 drill-down 進行状態 dashboard、黒田相談 + 信長主導」

---

## 1. Executive Summary

cmd_004 二大戦線は DentalBI 全体の **第 2-3 層 + phaseC 延伸**、ただし蜘蛛の糸 (= DD-020 法令 6 本目 + 8,000+ records 法令層) で全層連結。**局所視点でなく全体俯瞰 + 階層 drill-down + 蜘蛛の糸連携 + 自動更新 dashboard** を装備、5-10 年運用想定の根本治療品質。

## 2. 6 Layer 階層設計 (= 大項目 → 中項目 → 小項目 drill-down)

### Layer A. 構想層 (= DD-054 5 階層 + 10 柱)

| 大項目 | 中項目 | 小項目 |
|---|---|---|
| **第 0 層 憲法** | DD-010/037/048/054/061 | 各 DD version + 最終更新 |
| **第 1 層 診療コア** | 2 号用紙カルテ (= 原点 DD-036) + DD-034/038/043/044/035/009/025 | 各 DD impl status |
| **第 2 層 周辺診療** | 予約 (= phaseB) + 画像管理 + 問診 + 申し送り + CRM + リコール + 日計表 (DD-042) + 自費見積 (DD-045) | 機能別 status |
| **第 3 層 患者接点 (= 会計待ちゼロ)** | 患者アプリ PWA + AI チャット + 領収書 + SMS + 治療計画 + カード決済 + 高速会計 | 7 機能 |
| **第 4 層 AI 統合** | 蜘蛛の糸 + AI 副院長 + 画像 AI + 7 エンジン | 機能別 |
| **第 5 層 事業推進** | AI 副社長 + 研究会会費制 | 機能別 |

**10 柱**: 画像 AI / 歯の状態 DB / 治療計画ナビ / 患者アプリ + AI チャット / AI 副院長 / 処置セット / リアルタイム会計 / 蜘蛛の糸 / AI 副院長+AI 事務長 / AI 副社長

### Layer B. Phase 層 (= development_progress 50+ phase)

| 大項目 | 中項目 | 小項目 |
|---|---|---|
| **完了 Phase** | phase1-6 / phaseB / C / D | 各 phase week + pc + commit_hash |
| **進行中 Phase** | phase_a_id_unification / phase_b_karte_loader | task 一覧 |
| **未着手 Phase** | P2-engine 蜘蛛の糸 (169 件) / POST-deploy (= 朝礼/CTI/外部API/書式Lv3/材料/人事/全院展開) | 個別 task |

### Layer C. 機能層 (= cmd_004 二大戦線 dossier v1.1)

| 大項目 | 中項目 | 小項目 |
|---|---|---|
| **会計待ちゼロ作戦** | ① QR / ② 領収書 / ③ パスポート / ④ DB 連動 / ⑤ AI チャット / ⑥ specialty_mode / ⑦ 同意 | 各機能 cycle + audit + shogun_verified |
| **小児恐竜王国** | passport + ゲーム + 敵 100 体 + push + 儀式 + ceremony | DD-126 Phase A-F + 残件 |
| **申し送りエンジン** | 4 人合議 design + Stage 1/2/3 | round + cycle + impl |
| **第一段階 PDF 方式** | フォルダ監視 + 抽出 + 三方向処理 | 個別 module |

### Layer D. 頭脳層 (= 蜘蛛の糸 + 法令蓄積)

| 大項目 | 中項目 | 小項目 |
|---|---|---|
| **法令 source** | `legal_sources` (1,600) | 療担規則 / 厚労省 / 緑本 / 赤本 |
| **法令 linkage** | `legal_source_linkages` (3,235) + `legal_cross_checks` (896) | 個別 linkage |
| **個別指導** | `inspection_checklists` (2,495) + `inspection_findings` (621) + `instruction_checklist_items` (16) | self-check + 指摘 |
| **マスター** | `facility_standards_master` (65) + `drug_master` (28) + `procedure_codes_audit` (250) + `master_update_sources` (3) | 個別 master |

### Layer E. 運用層 (= 拙者 system 稼働状態)

| 大項目 | 中項目 | 小項目 |
|---|---|---|
| **MC** | shogun + karo + ashigaru 7 体 + gunshi 黒田 | 各 pane status + model + uptime |
| **SC** | shogun + karo + ashigaru 7 体 + gunshi 直政 | 各 pane status + ratelimit % |
| **systemd unit** | auto-git-sync / shogun-self-check / ttyd-shogun / shogun-tunnel / openclaw-gateway | active / failed / disabled |
| **規範 entity** | memory MCP 19 entities + relations | 個別 entity |

### Layer F. 規範層 (= memory MCP)

| 大項目 | 中項目 | 小項目 |
|---|---|---|
| **principle (= 最上位)** | mistake_prevention / radical_solution | 観察 |
| **rule** | F007 / audit_exclusive / model_selection / pre_audit / ratelimit_mgmt 等 14 件 | 観察 |
| **procedure / mechanism / constraint / agent / recovery_path / project_priority** | 残 entity | 観察 |

## 3. Data Source (= Single Source of Truth)

| Source | Layer 対応 | access |
|---|---|---|
| **Supabase**: `project_documents` / `development_progress` / `design_decisions` / `form_templates` / `legal_sources` / `inspection_*` / `procedure_codes_audit` / `master_*` | A + B + C + D | `mcp__claude_ai_Supabase__execute_sql` |
| **Local**: `queue/tasks/*.yaml` / `queue/reports/*.yaml` / `queue/shogun_to_karo.yaml` / `git log` / `dashboard.md` | B + C + E | local file read |
| **memory MCP**: 19 entities + relations | F | `mcp__memory__read_graph` |
| **tmux + ps + systemctl**: agent + service 状態 | E | bash |

= **既存基盤を 100% 流用**、新 data source 追加なし (= 根本治療下 既存活用最大化)。

## 4. UI 設計 (= 階層 drill-down)

### 4.1 主要 view (= 3 form)

| Form | 用途 | tech |
|---|---|---|
| **dashboard.md** (= text + table) | git tracked 静的 view | jinja2 template render |
| **dashboard.html** (= 静的 HTML) | ブラウザ視認 + drill-down accordion / tabs | Tailwind CSS + Alpine.js (= 軽量) |
| **mermaid diagram** (= 階層 tree + relations) | 視覚的 structure 把握 | mermaid markdown 埋込 |

### 4.2 階層 drill-down UI (= HTML view)

```
[Layer A 構想層: 65% ▼]
  └ [第 0 層 憲法: 100% ▼]
       ├ DD-054 統合構想 v1.1 ✅
       ├ DD-061 実用優先憲法 v2.4 ✅
       └ DD-048 デジタル理事長 ✅
  └ [第 1 層 診療コア: 80% ▼]
       ├ 2 号用紙カルテ DD-036 ✅
       ├ カルテ入力 UI DD-038 🟡
       └ Quartetto 連携 DD-044 🟡

[Layer B Phase 層: 70% ▼]
  └ [完了 phase: phase1-6/B/C/D ✅ (8 件)]
  └ [進行中: phase_a/b_id_unification (2 件)]
  └ [未着手: P2 蜘蛛の糸 169 件 + POST-deploy 多]

[Layer C 機能層: 50% ▼]
  └ [会計待ちゼロ作戦: 40% ▼]
       ├ ① QR チェックイン 🔴
       ├ ② 領収書 🟡
       ├ ③ パスポート 🟡
       ├ ④ DB 連動 🟡
       ├ ⑤ AI チャット 🔴
       ├ ⑥ specialty_mode ✅
       └ ⑦ 同意 🔴
  └ [小児恐竜王国: 60% ▼]
       ├ passport ✅
       ├ ゲームロジック 🟡
       ├ 敵 100 体 🟡
       ├ push 通知 🟡
       └ 儀式演出 🔴

[Layer D 頭脳層: 8,000+ records ▼]
  └ legal_sources: 1,600 records ✅
  └ legal_linkages: 3,235 records ✅
  └ inspection_checklists: 2,495 records ✅
  └ inspection_findings: 621 records ✅
  └ procedure_codes_audit: 250 records ✅

[Layer E 運用層: 16/20 体 active ▼]
  └ MC: 10 体 (shogun+karo+ashigaru7+gunshi)
  └ SC: 6 体 (= ratelimit 95% で 4 体停止後)

[Layer F 規範層: 19 entities ▼]
  └ principle: 2 (= mistake_prevention + radical_solution)
  └ rule: 11
  └ 他: 6
```

### 4.3 色分け + progress bar
- 完了 ✅ = green
- 進行 🟡 = yellow
- 未着手 🔴 = red
- 蜘蛛の糸 connect 線 = blue (= mermaid)

## 5. Tech Stack

| 層 | tool | 既存/新規 |
|---|---|---|
| **generator** | Python 3.12 + jinja2 + PyYAML | 既環境 |
| **diagram** | mermaid (= markdown 埋込、render は viewer 側) | 既環境 |
| **viewer** | dashboard-viewer.py 既存 + ブラウザ + Tailwind CSS + Alpine.js | 既 + 新 (= CDN 経由、install 不要) |
| **配信** | ttyd 経由 web (= 既装備 ttyd-shogun) + cross-PC tunnel | 既装備 |
| **timer** | systemd user timer 15 min (= auto-git-sync と並列) | 既 pattern 流用 |
| **store** | Supabase + git tracked + memory MCP (= 既基盤) | 既 |

= **新規 install 0 件、新 daemon 0 件**、既基盤 100% 流用 (= 根本治療下 Anti-duplication 最大化)。

## 6. 自動更新 mechanism

```
scripts/regenerate_dashboard.py (= 新規):
  Step 1: Supabase query (= mcp__claude_ai_Supabase__execute_sql 経由 not、直接 PostgreSQL connection + service role key、または既 source_code_cache pattern 流用)
  Step 2: local file read (= queue/tasks + queue/reports + git log)
  Step 3: memory MCP read_graph (= mcp__memory__read_graph wrap、CLI に再実装 or REST)
  Step 4: tmux/ps/systemctl 状態 read
  Step 5: jinja2 template render → dashboard.md + dashboard.html + mermaid svg
  Step 6: ttyd-shogun 経由 web 配信化 (= 既 active service 流用)

~/.config/systemd/user/dashboard-update.timer:
  OnUnitActiveSec=15min + Persistent=true + 両 PC 対称
```

## 7. 階層 drill-down 実装方針

| Layer | render form | drill-down 機構 |
|---|---|---|
| dashboard.md (= text) | jinja2 template、`<details>` HTML tag 埋込 | markdown viewer (= GitHub / VS Code) の HTML 解釈で展開 |
| dashboard.html (= ブラウザ) | Alpine.js x-show + accordion + tabs | click event で section 展開 |
| mermaid (= 図) | flowchart + subgraph | 階層 tree + relations 可視化 |

実装は段階的:
- Stage 2: dashboard.md 基本 view (= text + table) 完成
- Stage 3: dashboard.html drill-down 追加
- Stage 4: mermaid diagram 統合
- Stage 5: timer 自動更新 + 両 PC 配備

## 8. Implementation Stream (= 6 stage、cmd_020)

| Stage | 内容 | Bloom | model 選択 | 担当 |
|---|---|---|---|---|
| **1 設計** (= 本 doc) | v0.1 → 黒田 audit → 合議 → v1.0 | L1 | 拙者起草 + Codex audit | 信長 + 4 人合議 |
| **2 generator base** | `regenerate_dashboard.py` Supabase + local + memory MCP 統合、dashboard.md 生成 | L3 | ① Opus 初動 → Codex 監査 → Sonnet 修正 | ashigaru 1-2 体 (= MC) |
| **3 HTML view** | dashboard.html + Tailwind + Alpine.js drill-down + mermaid | L3 | ① Opus 初動 | MC ashigaru |
| **4 systemd 装備** | `dashboard-update.timer + service`、両 PC 配備 | L2 | ② 定型 | MC ashigaru、scp 経由 SC 配備 |
| **5 検証** | 24h 運用 + 階層 drill-down test + 自動更新 verify | L2 | ② 定型 | 直政 audit + 家康 shogun_verified |
| **6 統合** | 既 dashboard.md と置換、ttyd 経由 web view active | L1 | ② 定型 + 信長 final verify | 信長 + 家康 |

合議完遂目安: 3-6h (= 黒田 audit + 4 人合議 v0.1 → v1.0)
全実装目安: 1-3 日 (= 根本治療品質、テスト充足 + 法令完備 + UX 完璧)

## 9. Acceptance Criteria

| AC | 条件 |
|---|---|
| AC1 | 6 layer (= A-F) 全表示 |
| AC2 | 階層 drill-down (= 大→中→小) 動作 |
| AC3 | progress % 機械算出 + 色分け + bar |
| AC4 | 15 min 自動更新 (= systemd timer) |
| AC5 | 両 PC 配備 + HEAD 同期 + dashboard.html 同 content |
| AC6 | data source 100% 既基盤 (= 新 install / daemon 0) |
| AC7 | 蜘蛛の糸 8,000+ records 件数 + 最終更新 視認 |
| AC8 | cmd_004 二大戦線 + 申し送りエンジン B1 + 既 phase の連携が一画面で把握可 |
| AC9 | pytest tests/ で test_regenerate_dashboard.py 全 PASS、SKIP=0 |
| AC10 | 5-10 年運用想定 (= 構想拡大時 layer 追加可、Supabase 新 table 追加自動取り込み optional path) |

## 10. 拙者からの開放問 (= 黒田 + 3 人合議 review で答え要)

- **Q1 (= 4_logic)**: 6 layer 構成は妥当? 追加 / 統合 layer ある?
- **Q2 (= 8_UX)**: 階層 drill-down は HTML accordion + mermaid 併用が最適か、別 form (= SPA / TUI / etc.) 推奨ある?
- **Q3 (= 2_anti_dup)**: 既 dashboard.md (= karo 手動 update) との関係 (= 完全置換 / 並列 / 統合) どうすべき?
- **Q4 (= 5_schema)**: Supabase access 経路 (= MCP / 直 PostgreSQL / REST 経由 service_role) 推奨は?
- **Q5 (= 10_ecosystem)**: 蜘蛛の糸 view (= layer D) の表現方法 (= 件数 only / 内容 sample / 全件 listing) どこまで?
- **Q6 (= 7_law)**: dashboard.html を web 配信 (= ttyd 経由) で外部閲覧可能化、認証 (= token) 仕様は?
- **Q7 (= 6_test)**: 自動更新 (= 15 min) で Supabase 大量 query が課金 影響、threshold は?
- **Q8 (= 9_doc)**: dashboard 自身の使い方 doc は誰が書く (= 拙者 / ashigaru / karo)?
- **Q9 (= 1_func)**: 「予約ソフト」 統合表示の最適位置 (= phaseB / 第 2 層 / 別 dedicated section)?
- **Q10 (= 3_discipline)**: dashboard 自体の規範 (= 「shogun reads it, never writes」 retain?新規範要?)

## 11. 4 人合議 + 黒田 audit Protocol

```
v0.1 (= 信長起草) → 黒田 (= MC gunshi codex) 9 観点 + 10 lens audit
                  → 家康 (= SC shogun) review
                  → 本多 (= SC karo) review
                  → 直政 (= SC gunshi codex) cross-PC review (= 拙者 system 観点)
                  ↓
信長 integrate + version bump → v0.2
                  ↓
... 4 人 + 黒田 全員 verdict=pass まで loop ...
                  ↓
v1.0 確定 → 本多 + 秀吉 ashigaru 配信 (= Stage 2-6)
```

---

*round 1 v0.1 起草: 信長、2026-05-11T19:25*
