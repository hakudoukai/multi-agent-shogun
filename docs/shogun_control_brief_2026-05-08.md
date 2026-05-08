# 信長 control brief — 2026-05-08 reset 前 state 保全

> 用途: 信長 ERR-TOKEN-CRITICAL-001 (= 615k tokens) reset 前の state 全保全
> 復帰時: 新 session で本 brief + AGENTS.md + memory/MEMORY.md 読込で全復帰
> 理事長殿明示直命 16:30:「最後までやり通す以外にない。今後も確認不要」

## 1. 本日学習 (= memory 永続化済、必読)

| 永続化項目 | 内容 |
|----------|------|
| 信長強権 + 川柳精神 | 待たぬ・入れ換える・流派問わず使う |
| 信長強権境界 | 強権 ≠ self-execute、F001 順守、家老 dispatch 越権禁 |
| 家康代替 audit 永久禁止 | 家康の audit は家康のみ、代替不可 |
| 本末転倒厳禁訓示 | quota 95% は手段、価値創出が目的 |
| 大袈裟表現禁止 | 「本朝最大」「核心達成」等の誇大表現禁、事実報告のみ |
| Codex pane への send-keys 連発禁止 | Conversation interrupted 防止、1 prompt → sleep 5s → 確認 |
| Pro 確認義務徹底 | JWT decode で field 値直接確認、表面確認禁 |

## 2. 戦国軍議体制 (= 本日完成)

| 軍 | persona | 状態 |
|---|---------|------|
| 信長 | shogun:0.0 nobunaga (claude opus) | 戦略指揮、615k tokens、reset 予定 |
| 秀吉 (家老) | multiagent:0.0 hideyoshi (claude opus) | 740k tokens、reset 進行中 |
| 前田 (SecondPC 家老) | multiagent:0.0 maeda (claude) | /clear 完遂、復帰 Session Start 中 |
| 家康 (一次監査) | multiagent:0.3 ieyasu (codex Pro、永久権限) | audit 中 |
| 服部半蔵 (二次監査) | (未招聘、Phase 5 後) | — |
| 黒田官兵衛 (議長) | (未招聘、Phase 5 後) | — |
| 竹中半兵衛 (計画参謀) | multiagent:0.5 takenaka (claude) | 第 3 報完遂 idle |
| 本多正信 (智囊、組織改革) | multiagent:1.0 honda (codex Pro、永久権限) | 三案統合 v2 起案中 |
| 真田幸村 (改革実装) | multiagent:sanada.0 sanada (claude sonnet) | cmd_secondpc_state_reconciliation_001 着手 (16:19) |
| ashigaru1 | multiagent:0.1 (claude) | idle、cycle2 fix 待ち |
| ashigaru2 | multiagent:0.2 (claude) | 6 連続爆速完遂後 idle、家老 next 待ち |
| ashigaru3 | multiagent:0.4 (claude) | idle、cycle2 fix 待ち |
| ashigaru5/6/7 | SecondPC | /clear 完遂、家老前田 dispatch 待ち |

## 3. 進行中 cmd 群

### 改革 lane (= 本多 → 真田)
- **真田**: `cmd_secondpc_state_reconciliation_001` 進行中 (16:19 着手、18:00 期限)
- 真田 next pile: cmd_communication_resilience_pack_v2_001 (= 本多 三案統合 v2 完遂後)

### 通常 lane (= 秀吉 → ashigaru)
- ashigaru1: cmd_organizational_lessons_supabase_001 進行 + cycle2 fix (= 家康 FAIL 1)
- ashigaru2: 6 連続爆速完遂、next pile = 家康 cycle2 監査待ち
- ashigaru3: cycle2 fix (= 家康 FAIL 2、申告 path 違反)

### 設計 lane (= 本多)
- 本多 三案統合 v2 起案中 (= 信長 + 家康 + 本多)
- 出力 docs/honda_three_perspectives_unified_v2_2026-05-08.md
- 続いて cmd_communication_resilience_pack_v2_001 正式起案

### 監査 lane (= 家康)
- 永久権限 + audit 中
- ashigaru2 cycle2 監査 + 朝以降 unread 28+ 件処理

### 計画 lane (= 竹中)
- 第 3 報完遂 (= SecondPC 全停止真因確定)
- next: predictive intelligence 第 4 報、§2.4 mandate commit 待ち

## 4. 本日完遂 commit 主要 (= 23+ commits)

```
4dbac5b 本多 recommendations
c18d898 本多 phase16_3 retrospective
d7f14dd 本多 initial proposals
5877465 本多 audit_lane_status design
7f3e8da 大なた cmd_root_resolution
7c0ece0 Phase 5 codex personas (4 重防御)
c05aab0 §0 期待値 node|codex 修正
4e3a5c6 真田招聘
2141588 AGENTS.md Codex 能力拡張
444650b Pro 確認 mandatory
7777a9b misroute fix (maeda valid_secondpc 追加)
dd706ad inbox split-brain fix
c5ae3c4 本多 secondpc retrospective
2f4b960 cross-PC bridge type hardcode 修復
0535879 本多 phase16-4 second (TUI + validation flow)
addd03d 信長 communication_resilience proposal
8ae179e 家康 communication_breakdown audit
ad92603 本多 self_resilience design
7511d77 本多 communication_resilience proposal (tax + silence)
```

## 5. 報連相崩壊 三案

- 信長案: 8 件問題 + 個別 cmd マッピング (= addd03d)
- 家康案: 6 軸 FAIL + 4 中核 script (= ledger + reconcile + contract + interruption_guard) (= 8ae179e)
- 本多案: communication_tax + silence_state accounting (= 7511d77)
- 統合 v2: 本多起案中 (= cmd_communication_resilience_pack_v2_001)

## 6. 復帰時 next 5 step

1. AGENTS.md + memory/MEMORY.md + 本 brief 読込
2. 秀吉復帰確認 (= queue/inbox/hideyoshi.yaml + dashboard.md)
3. 真田 cmd_secondpc_state_reconciliation_001 進捗確認 (= 18:00 期限)
4. 本多 三案統合 v2 完遂確認 + cmd 正式化 → 真田 next dispatch
5. 家康 audit 進捗確認 (= ashigaru2 cycle2 + deferred 一掃)

## 7. 永久権限設定 (= 16:15 設定)

```
~/.codex/config.toml (両 PC)
[projects."/mnt/c/Users/User/projects/multi-agent-shogun"]
trust_level = "trusted"
approval_policy = "never"
sandbox_mode = "workspace-write"
```
家康 + 本多 codex permission prompt 抑制動作確認済 (= 16:15 家康 + 16:16 本多 報告着信)。

## 8. 残課題 (= cycle2 持越し候補、火曜 01:00 期限)

- 大なた sub-phase A/B/C/D/E/F/G/H/J (= cycle1 縮減提案、竹中第 3 報)
- 本多 Reform A-D (= cmd_control_plane_reset_admission 等、真田 dispatch path)
- Codex 4h /clear + 家康+本多 交代制 (= 翌朝 reset 後の 5h cap 予防)
- ashigaru cycle2 fix 連鎖 + cmd_passport_engine_consolidation 再発令

## 9. 期限管理

- 真田 cmd_secondpc_state_reconciliation_001: 本日 18:00
- 本多 三案統合 v2: 本日中
- 大なた cycle1 縮減版: 土曜 16:00
- 大なた cycle2 (= 残全件): 火曜 01:00

---

*信長 (織田信長) 2026-05-08 16:30 JST、reset 前 state 保全完遂*
