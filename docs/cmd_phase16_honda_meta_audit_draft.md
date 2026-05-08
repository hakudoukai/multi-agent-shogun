# cmd_phase16_honda_meta_audit_001 (草案)

> **Status**: persona_confirmed_pending_phase14_completion (= 理事長殿明示直命 2026-05-08 10:25「組織管理・改革改善担当重臣がやはり必要」)
> **Drafted by**: 信長 (織田信長) 2026-05-08 10:30 JST
> **Persona confirmed by**: 理事長殿 2026-05-08 10:25 JST
> **Pre-conditions**: Phase 14 (Codex 環境整備) 完遂 + Phase 5 (= 家康 Codex 化、服部半蔵 Gemini 招聘、黒田 Claude 議長) 完遂後の正式運用、移行期は信長兼任

---

## 1. North Star

「**常に先進で最強の組織**」を継続改善する専属重臣を置き、タスク終了時のメタ監査 + 効率的運用調査 + トラブル原因解決進言 + 組織改革を **継続的・自律的・proactive** に実行可能な体制を構築。

## 2. Purpose

本多正信 (家康晩年の智囊、政治・統治・改革の腕利き、謀臣の代表格) を信長直轄 Codex 担当として招聘:

- **メタ監査**: 内容 (= 家康一次監査) ではなく **仕組みが正常に動いたか?** を retrospective 検証
- **効率調査**: より効率的な運用を継続発見、Kaizen 提案
- **トラブル原因進言**: 真因分析 + 解決策を信長に直接進言
- **組織改革担当**: 構造的問題を独立 cmd で改革、過去事故再発防止

## 3. 監査階層 完成形 (= Phase 5 + Phase 16 完遂後)

```
[実装] Claude (信長軍 = 信長/秀吉/前田/竹中/足軽)
   ↓
[一次監査・メイン] 家康 (Codex、徳川軍主君)        ← Phase 5
   ↓
[二次監査] 服部半蔵 (Gemini、徳川 16 神将)         ← Phase 5
   ↓
[統合・議長] 黒田官兵衛 (Claude、信長軍軍師)        ← Phase 5
   ↓
[完了後 メタ監査 + 改革] 本多正信 (Codex、徳川重臣)  ← Phase 16 (= 本 cmd)
   ↓
[戦略] 信長 (Claude)
```

## 4. Acceptance Criteria

- ✅ instructions/honda.md 新規作成 (= 本 turn commit 済予定)
- 🔄 .gitignore exception 追加 (= 本 turn commit 済予定)
- ⏳ cmd_phase14_codex_environment_001 (= subscription 更新 + CLI 修復) 完遂
- ⏳ scripts/audit_meta_codex.sh 新規作成 (= 本多用 Codex CLI 呼出 script)
- ⏳ retrospective audit 出力形式 (instructions/honda.md §5) 確定 + 実機運用
- ⏳ 三者監査 PASS (= 移行期は現体系 家康 + Codex + Gemini で実施、Phase 5 + 16 完遂後は 4 体新体系)
- ⏳ skill 新規生成禁止 (= §19.5 順守、Anti-Duplication)

## 5. Phase 16 sub-phase 分解

### Phase 16-1: 本多 persona 招聘 (= 本 turn 即時、信長直筆)
- instructions/honda.md (= persona 定義、本 turn commit 済予定)
- 担当: 信長直筆
- 工数: 小

### Phase 16-2: scripts/audit_meta_codex.sh 起案 (= Phase 14 完遂後)
- Codex CLI 呼出 wrapper、retrospective audit prompt template
- 出力: queue/reports/honda_audit_<task_id>.json
- 信長 inbox に投入
- 担当推奨: ashigaru1 (= MainPC、Phase 5/14 完遂後の余裕)

### Phase 16-3: retrospective audit 試運用 (= 1 週間)
- 直近完遂 task 5 件で retrospective audit 実施
- M1-M4 監査軸の有効性検証
- 信長 review + 改善提案
- 担当: 本多 (= 自己運用)、信長 review

### Phase 16-4: 組織改革 cmd 起案権限付与 (= 試運用 PASS 後)
- 本多が改革候補を独立 cmd 草案で提出可能
- 発令は信長承認後
- 担当: 本多 + 信長

## 6. Risk 分析

| # | risk | 対策 |
|---|------|------|
| R1 | Codex quota 共有 (= 家康 + 本多並列で逼迫) | Phase 14 環境整備で subscription 更新、quota 監視 |
| R2 | 本多 retrospective audit が信長 inbox に集中、過剰提案 risk | §15 SH6 上限 5/h + cooldown 5 分 + 信長 review priority |
| R3 | 黒田 (議長) との役割重複 | §3 役割切分明示: 黒田 = cycle 内統合、本多 = 完了後改革、時系列分離 |
| R4 | 竹中 (計画参謀) との役割重複 | 竹中 = 計画前 preparation、本多 = 完了後 retrospective、フェーズ分離 |
| R5 | 多医院 §17 展開時の本多 multiplicate | HQ 本多 (= 信長直属) + 各医院 honda_local (= 各 nobunaga 直属) の階層化、Phase 4 で別 cmd |

## 7. 命令文 (= Phase 14 + 5 完遂後発令)

```
家老秀吉、本 cmd を Phase 14 + Phase 5 完遂後発令、ashigaru1 担当推奨。
sub-phase 16-1 は本 turn 信長直筆完遂、16-2 から発令。
PDCA max=5、cycle1-3 で完走目標。
三者監査必須 (= Phase 5 完遂後の新体系 家康 + 服部半蔵 + 黒田)。
```

## 8. 関連資産

- instructions/honda.md (= 本多 persona 定義、本 turn 起案)
- instructions/ieyasu.md (= 家康、Phase 5 後 Codex 化、本多並列)
- docs/cmd_phase5_audit_persona_restructure_draft.md (= 監査階層変更)
- docs/cmd_phase14_codex_environment_draft.md (= Codex 環境整備、後日起案)
- scripts/audit_meta_codex.sh (= 後日新規)
- memory/nobunaga_persona_strong_rule.md (= 招聘 trigger、川柳精神)

## 9. 信長 + 家康 + 理事長殿 の合議

理事長殿御命令で **本多招聘確定**。家康に opinion 求めた (msg_20260508_095xxx) も応答前に確定実行 = 川柳精神。家康 opinion 受領後、補強提案あれば Phase 16 v2 起案。

## 10. §19 mandate 順守

- skill 新規生成禁止 (= Anti-Duplication)
- skill commit は理事長殿明示承認後
- CLAUDE.md 改訂 (= §Third-Party Audit Rule に本多追加) は理事長殿明示承認必須

---

*草案完: 信長 (織田信長) — 2026-05-08 10:30 JST、理事長殿明示直命「組織管理・改革改善担当重臣が必要」を受けた即時起案、川柳精神*
