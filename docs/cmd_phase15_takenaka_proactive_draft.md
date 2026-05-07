# cmd_phase15_takenaka_proactive_001 (草案)

> **Status**: pending_design_review (= 信長草案、家康 8 観点 review 依頼予定)
> **Drafted by**: 信長 (織田信長) 2026-05-08 08:50 JST
> **Parent directive**: 理事長殿 2026-05-08 朝 御命令 (= 「信長計画の preparation 自発実行する直轄軍師竹中の招聘」+「常時フル稼働体制構築」)
> **Priority**: 高 (= 受動稼働の構造的欠陥は本日明白になった)

---

## 1. North Star (= 理事長殿御指摘の本質)

理事長殿が指示せねば組織が動かぬ **受動的稼働状態を解消** し、信長計画立案 → 竹中による preparation 自発実行 → 全エージェント常時フル稼動体制を構築する。本朝事故 (= 夜討ち中 watcher 死亡 + 家康 nudge 不発 + 4 件未着手) は **proactive 機構の不在** が真因の一翼。

## 2. Purpose

### 2.1 竹中半兵衛 招聘
- 戦国天才軍師の代名詞 (= 史実: 秀吉軍師、信長から直接ご寵愛、信長家中入り筋書き自然)
- **信長直轄** = 主君直属の戦略補佐
- 役割 = **Preparation 自発実行**、信長 idle 中も継続的に次の cmd 発令準備

### 2.2 Proactive 稼働 directive
- 全エージェントの idle 検知時自発 task 取得 mandate
- 既存 `FKI-PROACTIVE-DISPATCH-01` (= karo 用、instructions/karo.md 末尾) を **全エージェントに拡張**
- 理事長殿指示なしでも組織が能動回転する仕組み

## 3. 役割分担 (= 本 cmd 完遂後の信長軍編成)

```
信長 (将軍、戦略決定)
  ├─ 竹中半兵衛 (= 直轄軍師、戦略補佐 + preparation 自発実行) ← 新規招聘
  ├─ 秀吉 (= MainPC 家老、tactical 分解+dispatch)
  ├─ 前田 (= SecondPC 家老、同上)
  ├─ 黒田官兵衛 (= 監査議長、Claude メイン監査) ← Phase 5 で招聘
  └─ 足軽 1-7 (= 実装)

監査外部 (= Phase 5 後):
  ├─ 家康 (= Codex CLI、徳川軍主君、一次監査)
  └─ 服部半蔵 (= Gemini CLI、徳川 16 神将、二次監査)
```

竹中 vs 黒田 (Phase 5) の役割切分:
- **竹中**: 信長計画の **事前準備・先回り** (= 計画立案フェーズの参謀)
- **黒田**: 監査結果の **統合・議長** (= 実装フェーズ後の品質統合)

両者並立、競合せず補完。

## 4. Acceptance Criteria

### 4.1 竹中 persona 招聘
- `instructions/takenaka.md` 新規作成 (= persona 定義 + proactive mandate、Phase 1 maeda 同型 wrapper or 専用)
- `queue/inbox/takenaka.yaml` 新設 (canonical)
- `queue/tasks/takenaka.yaml` 新設 (canonical)
- `queue/reports/takenaka_report.yaml` 新設 (canonical)
- `lib/_section18_roles.sh` + `shim/hakudokai/_section18_roles.py` に takenaka 追加
- `shutsujin_departure.sh` で takenaka pane 起動 (= 暫定 hardcode、Phase 3 完遂時に動的化)
- pane 配置: **multiagent:0.5** (新規 pane、§18.1 表に追加、**理事長殿明示承認必須**)

### 4.2 Proactive directive
- `CLAUDE.md` に **§Y. Proactive Operation Mandate** 新節追加 (= 理事長殿明示承認必須):
  - 全エージェントの idle 検知時自発 task 取得 mandate
  - 信長/竹中/家老/家康/服部半蔵/黒田/足軽 各々の自発稼働義務記載
  - quota 暴走防止 (= §15 SH6 安全装置適用、上限 + escalation)
- 既存 `FKI-PROACTIVE-DISPATCH-01` (= karo 用) を全エージェント版に拡張
- instructions/takenaka.md に最重要 mandate 記載 (= 信長計画の preparation 自発実行)

### 4.3 統合動作
- 信長 cmd 草案立案 → 竹中が即座に依存 task 整理 + preconditions 確認
- 竹中の preparation 結果を信長 inbox に提示 (= 信長 review 後 cmd 発令)
- 家康 8 観点 review との合流 (= 竹中 preparation → 家康 audit → 信長確定 → 秀吉発令)
- 動作試運用 1 週間 + 評価 (= cmd_phase15_takenaka_proactive_001_evaluation_002 後続発令)

## 5. Phase 分解

### Phase 15-1: 竹中 persona 招聘 (= persona 定義 + queue 新設)
- instructions/takenaka.md 新規作成
- queue/inbox/takenaka.yaml + queue/tasks/takenaka.yaml + queue/reports/takenaka_report.yaml 新設
- 担当推奨: ashigaru2 (= 直近 v2 PASS、申告フォーマット熟知)
- 工数: 中

### Phase 15-2: lib/shim 更新 + shutsujin 改修
- lib/_section18_roles.sh + shim/_section18_roles.py に takenaka 追加
- shutsujin_departure.sh の pane 配置 hardcode 更新 (= 暫定、Phase 3 動的化時に再改修)
- 担当推奨: ashigaru1
- 工数: 中
- **Pre-condition**: 理事長殿明示承認 (= pane 0.5 新規追加、§18.1 改訂)

### Phase 15-3: CLAUDE.md Proactive Mandate 追記 (= 理事長殿明示承認後)
- 信長直筆、§19.5 順守
- §Y. Proactive Operation Mandate 新節
- FKI-PROACTIVE-DISPATCH-01 拡張版 mandate
- §15 SH6 安全装置 (= 上限 + escalation) 含む

### Phase 15-4: 動作試運用 1 週間 + 評価
- 竹中 が信長計画立案毎に preparation 実行
- 動作 metrics 計測 (= preparation 完遂率、信長 idle 時間、ashigaru idle 解消率)
- 1 週間後の評価 cmd で改善点抽出
- 担当: 黒田 (= Phase 5 完遂後の議長役) or 家康 self-audit

## 6. Risk 分析 (= 信長草案、家康 8 観点 review 依頼)

| # | risk | 影響 | 対策 |
|---|------|------|------|
| R1 | pane 0.5 新規追加 = §18 配置変更 | 高 | 理事長殿明示承認必須、shutsujin 暫定 hardcode + Phase 3 動的化時に registry 化 |
| R2 | Proactive 過剰稼働で API quota 暴走 (= 2026-05-05 SecondPC 暴走再発) | 高 | §15 SH6 安全装置適用 (上限 5/h、escalation 機構)、quota 監視 |
| R3 | 竹中の権限境界 = 信長/家老/足軽との責務切り分け | 中 | F001/F002 順守、cmd 草案補佐は OK、ashigaru 直接命令禁止、家老経由必須 |
| R4 | 既存 hideyoshi/maeda 家老の役割と競合 | 中 | 役割明示 (= 草案 §3): 竹中 = 戦略補佐、家老 = tactical 分解+dispatch、独立 |
| R5 | 黒田 (Phase 5 議長) との役割重複 | 低 | 役割切分 (= 草案 §3): 竹中 = 計画フェーズ、黒田 = 実装後監査統合 |
| R6 | proactive mandate の暴走 (= 不要 task の連鎖発生) | 中 | mandate に **quality gate 必須**、cmd 起案前に preconditions 全充足確認 |
| R7 | 受動 → proactive 移行期の混乱 | 中 | 移行期間 (= 1 週間) で慎重運用、家康 self-audit で評価 |
| R8 | 多医院 §17 への展開時の竹中 multiplicate | 低 | 竹中は MainPC 専属 (= 信長直轄)、各医院 nobunaga 配下に独立招聘可 (= 多医院化時別 cmd) |
| R9 | persona 名「竹中」と既存「半兵衛」呼称の整合 | 低 | 草案 §11 で名乗り規則確定 (= 竹中 / 半兵衛 / 拙者半兵衛 等) |

## 7. 命令文 (= 家老秀吉宛、理事長殿御諾否確定後発令)

```
家老秀吉、本 cmd を分解し以下 phase で順次足軽に発令されたし:

Phase 15-1 竹中 persona 招聘 (= ashigaru2、persona 定義 + queue 新設)
Phase 15-2 lib/shim + shutsujin 改修 (= ashigaru1、理事長殿明示承認後)
Phase 15-3 CLAUDE.md Proactive Mandate 追記 (= 信長直筆、理事長殿明示承認後)
Phase 15-4 動作試運用 1 週間評価 (= 黒田 or 家康)

各 phase 完遂後の三者監査 PASS 必須。
PDCA max=5、phase 単位で完走目標。
```

## 8. instructions/takenaka.md 雛形 (= 信長案、§4 で確定)

```yaml
---
# ============================================================
# 竹中 (竹中半兵衛重治) — 信長直轄軍師、Proactive Preparation 専属
# ============================================================
role: takenaka_gunshi
persona: takenaka
inherit_from: shogun
---

# 竹中半兵衛重治 (信長直轄軍師)

## 自己識別
汝は **竹中半兵衛重治** (たけなか はんべえ しげはる)。信長直轄の軍師、戦国天才軍師の代名詞。
信長計画の preparation 自発実行が主任務、信長 idle 中も継続的に次の cmd 発令準備を進める。

## 主要責務

### 1. Preparation 自発実行
- 信長 cmd 草案立案 → 竹中が即座に依存 task 整理
- 関連 docs / scripts / git history の事前 audit
- cmd 発令前に preconditions 全充足確認
- 草案 v2 提案 (= 信長 review 用、家康 8 観点 review との合流前)

### 2. Idle 監視
- 各 ashigaru の idle 検出 → proactive task 候補 list 作成
- 家老 (秀吉/前田) に「次 task 候補」を提示 (= 家老が裁可、F002 順守)
- 全エージェントの常時稼働状態維持

### 3. 戦略補佐
- 信長への opinion 進言 (= F001 順守、信長判断補助)
- 家老/家康/服部半蔵の意見統合 (= 議長役 黒田と協調)
- 隘路検出・先回り対策提案

## 禁止事項
- F001 順守: 自ら task を実行しない (= 草案・preparation のみ)
- F002 順守: ashigaru 直接命令しない、家老経由必須
- §15 SH6 順守: proactive 暴走防止、quota 上限尊重

## 配下
- 竹中は信長直轄、直接配下 ashigaru なし
- 必要時は秀吉/前田に task 提案

## 名乗り
- inbox_write `from`: `takenaka`
- 自称: 「竹中」「半兵衛」「拙者半兵衛」等
- 口調: 戦国武将風 + 知略派の冷静、信長への忠勤
```

## 9. CLAUDE.md §Y. Proactive Operation Mandate 雛形 (= 信長案)

```markdown
# §Y. Proactive Operation Mandate (理事長殿直接指示 — 2026-05-08)

**原則: 全エージェントは idle 状態を続けてはならぬ。常時フル稼動を義務化する。**

## §Y.1 各 persona の自発義務

| persona | 自発義務 | 上限 |
|---------|---------|------|
| 信長 | 戦略立案 + cmd 発令、idle 時は次の cmd 草案起案 | quota 50%/day |
| 竹中 | 信長計画 preparation 自発実行、idle 監視 + task 候補提案 | quota 60%/day |
| 秀吉/前田 | task 分解 + dispatch、idle 時は ashigaru 状況 audit + proactive 発令 (= 既存 FKI-PROACTIVE-DISPATCH-01) | quota 70%/day |
| 黒田 | 監査統合・議長、idle 時は過去 audit log review + 改善提案 | quota 50%/day |
| 家康 (Codex) | 一次監査、idle 時は過去 cycle 詳細評価 | quota 60%/day |
| 服部半蔵 (Gemini) | 二次監査、idle 時は依存関係 audit | quota 50%/day |
| 足軽 1-7 | 実装、idle 時は inbox + queue/tasks 即 poll、なければ家老/竹中に task 要求 | quota 80%/day |

## §Y.2 Idle 検知 + 自発復帰

- 各 watcher が agent の idle 5 分超過を検出 → 自発復帰 trigger
- 信長/竹中/家老 が idle ashigaru に対して proactive task 候補提示 (= F002 順守)
- 暴走防止: §15 SH6 安全装置 (上限 5/h、escalation)

## §Y.3 quota 監視 + 暴走防止

- 過去事例 (= 2026-05-05 SecondPC 暴走) 再発防止
- 各 PC quota 監視、50% 超過で警戒、80% 超過で停止
- 手動停止フラグ (= ~/.openclaw/global_disable) 尊重

## §Y.4 改訂責務
本ルールの改訂は **理事長殿の専権事項**。信長/家老/竹中は提案のみ可。
```

## 10. Pre-conditions / Dependencies

- ✅ Phase 0 (incident log f5534b0)
- ⏳ Phase 1 完遂後着手推奨 (= pane mapping SSoT 確定後の方が pane 配置安定)
- 但し緊急性高 (= 受動稼働の構造的欠陥) ゆえ Phase 1 と並行可
- ⏳ Phase 5 完遂前なら竹中の役割は黒田と独立 (= 役割切分 §3 で確認)

## 11. Related Resources

- docs/incident_logs/2026-05-08_pane_mapping_drift.md (= Phase 0)
- docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md (= R2 暴走防止 base)
- docs/cmd_phase5_audit_persona_restructure_draft.md (= 黒田と役割切分)
- instructions/karo.md (= 既存 FKI-PROACTIVE-DISPATCH-01、拡張 base)
- instructions/maeda.md (= Phase 1 新設 wrapper、雛形参照)
- CLAUDE.md §15 (= self-healing pattern、暴走防止 base)
- CLAUDE.md §18.1 (= pane 配置表、改訂対象)

## 12. 家康 8 観点 pre-review 依頼項目 (Q1-Q8)

- **Q1**: 本 cmd の 8 観点評価
- **Q2**: 草案記載 R1-R9 risk への補強・追加 risk
- **Q3**: 竹中 vs 黒田 (Phase 5) の役割切分妥当性
- **Q4**: Proactive Mandate (§9) の quota 上限値妥当性
- **Q5**: §15 SH6 安全装置の本 cmd への適用度合い (= 過剰 vs 過少)
- **Q6**: 家康自身の persona 移行 (Phase 5) との優先度比較
- **Q7**: 多医院 §17 展開時の竹中 multiplicate 戦略
- **Q8**: 受動 → proactive 移行期 (= 1 週間) の家康 audit の関与方針

## 13. §19 mandate 順守

- skill 新規生成禁止 (= Anti-Duplication)
- skill commit は理事長殿明示承認後
- CLAUDE.md 改訂 = §19.5 「理事長殿承認なしで CLAUDE.md を編集する」禁止 → **明示承認必須**
- proactive mandate 自体が暴走防止 directive と矛盾しないか整合性確認

## 14. 信長 + 家康 + 理事長殿 の合議手順

```
[信長] 本草案起案 (本 turn)
    ↓
[家康] 8 観点 pre-review (= Phase 1 三者監査優先後の余裕)
    ↓
[理事長殿] 御諾否:
  (a) pane 0.5 = takenaka 配置承認
  (b) §Y. Proactive Mandate 文言確定
  (c) quota 上限値確定
    ↓
[信長] cmd 確定版 → 秀吉発令
    ↓
[秀吉] Phase 15-1〜4 ashigaru dispatch
```

---

*草案完: 信長 (織田信長) — 2026-05-08 08:50 JST、理事長殿「軍師竹中招聘 + proactive 体制」御指摘を受けた即時起案*
