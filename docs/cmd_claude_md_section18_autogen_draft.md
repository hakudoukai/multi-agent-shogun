# cmd_claude_md_section18_autogen_001 (草案 — Phase 3-4 分離受け皿)

> **Status**: pending_design_review (= 信長 v2 起案 2026-05-08 09:35、家康 Q3 助言を受けた Phase 3-4 分離別 cmd)
> **Drafted by**: 信長 (織田信長) 2026-05-08 09:35 JST
> **Parent**: cmd_phase3_shutsujin_dynamic_pane_001 (= Phase 3-4 分離元)
> **Pre-conditions**: Phase 3 本流 (= 3-1, 3-2, 3-3, 3-5, 3-6) 完遂 + 理事長殿明示承認 (§19.5)
> **Priority**: 後続 (= Phase 3 完遂後に発令、緊急性低)

---

## 1. North Star

CLAUDE.md §18.1 pane 配置表を **registry から auto-generate** することで、4-5 箇所の独立記述 drift を恒久消滅させる。**理事長殿の人手 doc 編集を阻害せず**、AUTOGEN BEGIN/END マーカーで auto-gen 区間と理事長殿専権区間を分離。

## 2. Purpose

Phase 3-4 を Phase 3 本流から分離した独立 cmd:
- (1) AUTOGEN BEGIN/END マーカー導入 (= §19.5 理事長殿明示承認下)
- (2) `scripts/codegen/regen_pane_table.sh` 新規作成
- (3) regen 副作用防止 (= hash 比較 + diff 検出 + git restore rollback)
- (4) CI gate (= AUTOGEN 区間外破壊検知)

## 3. なぜ別 cmd 化 (= 家康 v2 Q3 強推奨)

| 理由 | 詳細 |
|------|------|
| §19.5 制約 | 理事長殿明示承認が必須、Phase 3 本流とは別の承認 ticket |
| auto-gen 機構の独立複雑性 | regen 副作用 + 競合 lock + CI gate、scope 大 |
| Phase 3 本流の独立性 | 3-1〜3-3 + 3-5 + 3-6 で dynamic pane resolution は完結、auto-gen は separable |
| 慎重段階導入 | 本 cmd は Phase 3 完遂 + 1 週間運用観察後、registry 安定状態で着手 |

## 4. Acceptance Criteria

- CLAUDE.md §18.1 表に `<!-- AUTOGEN BEGIN: pane_table -->` / `<!-- AUTOGEN END: pane_table -->` マーカー導入
- マーカー区間内 = registry 由来 auto-gen、区間外 = 理事長殿専権手動編集
- `scripts/codegen/regen_pane_table.sh` 新規:
  - registry → §18.1 表 markdown 生成
  - 区間外 hash 比較 + diff 検出 + 異常時 abort (= 家康 R11)
  - git restore による rollback フロー
- CI gate: PR 時 AUTOGEN 区間整合性検証
- regen 競合防止: `flock` または `~/.openclaw/regen_in_progress` フラグ
- 三者監査 PASS (= Phase 5 完遂後は新体系)
- skill commit は理事長殿明示承認後 (§19.5)

## 5. Risk

| # | risk | 対策 |
|---|------|------|
| R1 | AUTOGEN 区間外破壊 (= 家康 R11) | hash 比較 + diff 検出 + abort + git restore |
| R2 | 複数 AUTOGEN block の境界混乱 | マーカー名前空間厳格化 (= `pane_table` 等の suffix 必須) |
| R3 | regen 中の理事長殿手動編集衝突 | flock + フラグ + 編集中の自動 abort |
| R4 | CI gate 不在で人手検証スキップ | GitHub Actions または pre-commit hook で必須化 |

## 6. Pre-conditions

- ✅ Phase 0 (= incident log f5534b0)
- ⏳ Phase 1 完遂
- ⏳ Phase 2 完遂
- ⏳ Phase 3 本流 (3-1, 3-2, 3-3, 3-5, 3-6) 完遂 + 1 週間運用観察
- ⏳ 理事長殿明示承認 (§19.5)

## 7. 命令文 (= 家老秀吉宛、Pre-conditions 充足後発令)

```
家老秀吉、本 cmd を ashigaru1 or ashigaru2 に発令。
Phase 3 完遂後の registry 安定状態で着手、CLAUDE.md auto-gen を慎重実装。

担当推奨: ashigaru1 (= Phase 3 完遂時点で余裕)
三者監査: 家康 + Codex/Gemini (= 移行期は現体系、Phase 5 完遂後は新体系)

PDCA max=5、CI gate と regen 動作確認を慎重に。
```

## 8. Related Resources

- docs/cmd_phase3_shutsujin_dynamic_pane_draft.md (= 親 cmd、本 cmd 分離元)
- docs/incident_logs/2026-05-08_pane_mapping_drift.md (= Phase 0 base)
- 家康 4 草案 8 観点 review msg_20260508_091318_2e956812 (= Q3 別 cmd 化助言)
- queue/pane_registry.yaml (= Phase 1+2+3 で確立、本 cmd で auto-gen 元)

## 9. §19 mandate 順守

- skill 新規生成禁止 (= Anti-Duplication)
- CLAUDE.md 改訂 = §19.5 「理事長殿承認なしで CLAUDE.md を編集する」禁止 → **明示承認必須**
- regen による auto-gen 区間更新 = §19.5 の「自動化下での明示承認」境界線、**初回 commit のみ理事長殿承認、その後は CI gate で代替** とする運用提案

---

*草案完: 信長 (織田信長) — 2026-05-08 09:35 JST、家康 Phase 3 review Q3 「3-4 別 cmd 分離強推奨」を受けた即時 v2 起案*
