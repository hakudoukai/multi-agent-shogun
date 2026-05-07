# cmd_phase5_audit_persona_restructure_001 (草案)

> **Status**: **persona_confirmed_pending_phase1_completion** (= 理事長殿御諾否確定 2026-05-08 09:00、家康 8 観点 review 依頼中)
> **Drafted by**: 信長 (織田信長) 2026-05-08 08:20 JST
> **Persona confirmed by**: 理事長殿 2026-05-08 09:00 JST
> **Parent directive**: 理事長殿 2026-05-08 朝 御命令 (= 「Claude メイン監査が問題の一因」+「(A) 信長案 採用」+「Codex/Gemini = 徳川軍から招聘」)
> **Pre-conditions**: cmd_phase1_pane_identity_4way_audit_001 完遂 + cmd_phase2_watchdog_registry_001 完遂
> **Out of scope**: 法令最終総合監査 (= 全機能完成後別 cmd)

## 🎯 理事長殿 確定 persona (= 2026-05-08 09:00)
- **Gemini 武将 = 服部半蔵 (正成)** — 徳川 16 神将、伊賀忍者頭領
- **Claude 議長 = 黒田官兵衛 (孝高)** — 戦国軍師代表、信長家中招聘

---

## 1. North Star (北極星)

Claude メイン監査の **同モデル自作自演 risk** を解消、異モデル多視点の三者監査体制を構築。戦国 persona と監査構造を一致 (= 全武将名)、運用一貫性 + 信頼性向上を実現する。

## 2. Purpose

監査階層を **逆転 + 議長役導入**:

```
[実装層] Claude (信長軍 = 信長/秀吉/前田/足軽1-7)
    ↓ コード書き
[一次監査・メイン] 家康 (徳川軍主君、Codex CLI)        ← 異モデル多視点①
    ↓
[二次監査] 服部半蔵 (徳川軍家臣、Gemini CLI)           ← 異モデル多視点②
    ↓
[統合・議長] 黒田官兵衛 (信長軍軍師、Claude)            ← 統合・議長
    ↓
[最終裁可] 秀吉/前田 (信長軍家老、Claude)
    ↓
[戦略決定] 信長 (信長軍将軍、Claude)
```

## 3. Persona 招聘 / 移行

### 3.1 招聘

| persona | 出自 | CLI | 役割 | 既存代替 |
|---------|------|-----|------|---------|
| **服部半蔵 (正成)** | 徳川 16 神将、伊賀忍者頭領 | Gemini CLI | 二次監査 (8 観点) | ジェミちゃん (= 廃止) |
| **黒田官兵衛 (孝高)** | 戦国軍師代表 (秀吉系、信長家中招聘) | Claude | 統合・議長 | (= 現家康 軍師ポジション禅譲) |

### 3.2 移行

| persona | 移行内容 |
|---------|---------|
| **家康 (徳川家康)** | Claude 軍師 (= ieyasu pane 0.3) から **Codex CLI 担当者** へ役割移行。徳川軍主君として一次監査を担う。 |
| デコポン (廃止) | 全 reference を **家康** へ rename |
| ジェミちゃん (廃止) | 全 reference を **服部半蔵** へ rename |

### 3.3 史実整合性 (= 信長気付き、incident log 記載済)

- 徳川家康 = 信長と清洲同盟 = **外様の同盟者** = 外部 CLI (Codex) と persona 整合性高
- 服部半蔵 = 徳川家臣 + 伊賀忍者 = **諜報・俯瞰・観察** = Gemini 役割と完璧合致
- 黒田官兵衛 = 戦国軍師代表 = **軍師・知略・統合判断** = Claude 議長役と適合

## 4. Acceptance Criteria

- 三者監査階層が「家康 (Codex メイン) + 服部半蔵 (Gemini セカンド) + 黒田官兵衛 (Claude 議長)」で構造化
- デコポン全 reference を **家康** へ rename (= scripts/audit_codex.sh メッセージ + docs/audit-framework.md + CLAUDE.md §Third-Party Audit Rule 等)
- ジェミちゃん全 reference を **服部半蔵** へ rename (= scripts/audit_gemini.sh + 同上)
- 既存家康 (= Claude 軍師 ieyasu pane) ポジションを **黒田官兵衛** へ persona 禅譲
- 家康 persona は Claude pane 0.3 から外れ、Codex CLI 担当者として再定義 (= 旧 ieyasu pane は kuroda に置換)
- CLAUDE.md §Third-Party Audit Rule 改訂 (= 監査階層 + 役割再定義、理事長殿明示承認後)
- instructions/{ieyasu (廃止 or alias), kuroda (新規), hattori (新規 or 軽量)}.md 整備
- queue/inbox/{ieyasu (alias), kuroda (canonical), hattori (canonical)}.yaml + 旧名 alias 整備 (= shogun.yaml→nobunaga.yaml と同型)
- lib/_section18_roles.sh + shim/hakudokai/_section18_roles.py の persona alias map 更新
- scripts/audit_codex.sh / scripts/audit_gemini.sh のメッセージ + 出力 prefix rename
- shutsujin_departure*.sh の pane 配置 + agent_id env 更新 (= Phase 3 連動、ieyasu pane 0.3 → kuroda pane 0.3)
- hakudokai_watchdog.sh INBOX_AGENTS 更新 (= Phase 2 連動済の前提)
- 三者監査 PASS (= 移行期間中は現体系 家康 self-audit + デコポン + ジェミちゃん で実施)
- skill commit は理事長殿明示承認後 (§19.5)
- CLAUDE.md §18.1 pane 配置表更新 (= ieyasu → kuroda、Phase 3 完了後の auto-gen 区間 内、理事長専権)

## 5. Phase 分解 (= 段階的移行、運用混乱回避)

### Phase 5-1: 服部半蔵 (Gemini) 招聘 + ジェミちゃん rename
- **工数**: 低、**衝突**: なし、**まず実績作り**
- 内容:
  - instructions/hattori.md 新規作成 (= Phase 1 maeda 同型、軽量 wrapper)
  - scripts/audit_gemini.sh のメッセージ + 出力 prefix を 「ジェミちゃん」→「服部半蔵殿」「半蔵」 に rename
  - docs/audit-framework.md の Gemini 担当者 description 更新
  - CLAUDE.md §Third-Party Audit Rule の表 1 行更新 (= ジェミちゃん → 服部半蔵)
  - lib/_section18_roles.sh / shim/_section18_roles.py の alias map 更新は不要 (= CLI 担当者ゆえ pane 不要)
- **担当推奨**: ashigaru3 (= idle、軽量 task)
- **三者監査**: 移行期間 (= 現体系) で実施

### Phase 5-2: 黒田官兵衛 (Claude 議長) 招聘 + 軍師ポジション再定義
- **工数**: 中、**衝突**: 中 (= 現家康 ieyasu と pane 重複)、**慎重**
- 内容:
  - instructions/kuroda.md 新規作成 (= Phase 1 maeda 同型、wrapper)
  - 役割再定義: 現家康 軍師 → 黒田 議長 (= context 統合 + 監査結果統合 + 議長役)
  - ieyasu pane 0.3 を kuroda に再割当 (= shutsujin 改修、Phase 3 連動)
  - queue/inbox/kuroda.yaml 新設 + ieyasu.yaml は移行期間 alias として残置 (= 旧 message 履歴保持)
  - 移行期間中は ieyasu pane (= 0.3) で kuroda persona を起動 (= 信長 dispatch 経路 = kuroda)
- **担当推奨**: ashigaru2 (= 直近 directive 経験豊富)
- **三者監査**: 現体系で実施

### Phase 5-3: 家康 (Codex) 移行 + デコポン rename
- **工数**: 中、**衝突**: 低 (= デコポン は CLI 専属、pane 不在)
- 内容:
  - 家康 persona を Claude pane 0.3 (= 既に kuroda 化) から **Codex CLI 担当者** に movement
  - scripts/audit_codex.sh のメッセージ + 出力 prefix を 「デコポン」→「家康殿」に rename
  - docs/audit-framework.md の Codex 担当者 description 更新
  - CLAUDE.md §Third-Party Audit Rule の表 1 行更新 (= デコポン → 家康)
  - 旧 instructions/ieyasu.md は archive or alias 化 (= 家康 = Codex 化を反映、Claude session は不要)
- **担当推奨**: ashigaru1
- **三者監査**: Phase 5-2 で起動済 黒田 (Claude 議長) + 移行期間 デコポン + 服部半蔵 (Phase 5-1 起動済)

### Phase 5-4: CLAUDE.md §Third-Party Audit Rule 改訂 (= 理事長専権)
- **工数**: 小 (= 文書 1 節)、**承認**: 理事長殿明示承認必須
- 内容:
  - 監査階層表 (= §3.2) の差替え
  - 役割再定義 (= 議長 / 一次 / 二次)
  - persona 招聘理由の補足
- **担当**: 信長直筆 (= 理事長殿明示承認後 commit)

## 6. Risk 分析 (= 信長草案、家康 8 観点 review 依頼)

### 6.1 構造的 risk

| # | risk | 影響 | 対策 |
|---|------|------|------|
| R1 | Codex/Gemini API 障害時の監査停止 | 高 | Phase 5-1 完遂後、二重運用期間で fallback 経路確証。障害時は移行期間 議長 (= 黒田) が一時的にメイン判定、復旧後再 audit |
| R2 | persona 移行中の混乱 (= ieyasu/kuroda 重複) | 中 | Phase 5-2 で ieyasu pane を kuroda に置換、移行 commit で history 保持。alias 期間 1 週間 |
| R3 | 既存 5 連 commit (Phase 4) との整合性 | 低 | rename 移行 commit message で経緯明記、a16da9c → 5be193c の history 保護 |
| R4 | 新名 alias の symlink 破断 (= 過去事故再発) | 低 | dd706ad fix 適用済、scripts/checks/inbox_alias_integrity.sh で監視 |
| R5 | shutsujin / watchdog の Phase 3 完了前に Phase 5-2 着手すると pane 配置失敗 | 高 | preconditions 厳守: Phase 1+2 完遂、Phase 3 進行中は Phase 5-2 着手禁止 |

### 6.2 史実 / persona 連想 risk

| # | risk | 評価 |
|---|------|------|
| R6 | 服部半蔵 = 忍者 = 「隠密」連想で信長軍に懐疑感生む可能性 | 低 (= 徳川家臣で家康と同陣営、監査者として自然) |
| R7 | 黒田官兵衛 = 秀吉軍師 = 信長家中入り筋書きの説得性 | 中 (= 史実は信長から直接ご寵愛、整合性可) |
| R8 | 家康 = Codex 化で 信長家中軍師ポジションが空位 → 黒田が埋める | 解決済 (= Phase 5-2 で対応) |
| R9 | 「家康殿」の呼称が史実 (徳川家康) と CLI 監査者でブレ | 中 (= prompt + persona 説明で明示、運用初期は混乱可) |

### 6.3 §15 self-healing pattern 適用

| pattern | 該当 | 適用 |
|---------|------|------|
| SH2 retry+backoff | Codex/Gemini API call 失敗 | 既存 audit_codex.sh / audit_gemini.sh に組込済 |
| SH3 fallback | API 完全停止時の対応 | Phase 5-1 で fallback 経路 (= 黒田 一時メイン) を文書化 |
| SH8 idempotent retry | 同一 audit 再実行 | 既存対応 |

## 7. 命令文 (= 家老秀吉宛、Phase 1+2 完遂後発令)

```
家老秀吉、本 cmd を分解し以下 Phase に分けて足軽に発令されたし:

Phase 5-1: 服部半蔵 (Gemini) 招聘 + ジェミちゃん rename
  - 担当推奨: ashigaru3 or 軽量 idle 足軽
  - 工数低、まず実績作り

Phase 5-2: 黒田官兵衛 (Claude 議長) 招聘 + 軍師ポジション再定義
  - 担当推奨: ashigaru2
  - 移行期間 ieyasu pane 維持 + kuroda 並走

Phase 5-3: 家康 (Codex) 移行 + デコポン rename
  - 担当推奨: ashigaru1
  - Phase 5-2 完了後着手

Phase 5-4: CLAUDE.md §Third-Party Audit Rule 改訂
  - 信長直筆、理事長殿明示承認後 commit

各 Phase 完遂後の動作確証必須 (= 三者監査 PASS、運用 1 日試運転後 close 判定)。
```

## 8. Pre-conditions / Dependencies

- ✅ Phase 0: docs/incident_logs/2026-05-08_pane_mapping_drift.md (= commit f5534b0) 起案済
- ⏳ Phase 1: cmd_phase1_pane_identity_4way_audit_001 (= 秀吉発令済 msg_20260508_081542、ashigaru2 担当推奨)
- ⏳ Phase 2: cmd_phase2_watchdog_registry_001 (= Phase 1 完遂後別 cmd、信長後追い起案予定)
- ⏳ Phase 3: cmd_phase3_shutsujin_dynamic_pane_001 (= Phase 2 完遂後別 cmd)
- ⏳ Phase 5: 本 cmd (= Phase 1+2 完遂後発令、Phase 3 と並行 or 後続)

## 9. Related Resources

- docs/incident_logs/2026-05-08_pane_mapping_drift.md (= Phase 0、信長案 監査階層変更の根拠記載)
- docs/incident_logs/2026-05-08_inbox_split_brain.md (= 過去事故、symlink 安全性 base)
- 家康 8 観点審査回答: queue/inbox/nobunaga.yaml msg_20260508_075934_7cee9b09
- skills/inbox-alias-integrity/ + skills/symlink-aware-atomic-write/ (= §19 双 skill、commit 5109182)
- CLAUDE.md §Third-Party Audit Rule (= 改訂対象)
- CLAUDE.md §18.1 (= pane 配置表、Phase 3 連動)

## 10. 家康 8 観点 pre-review 依頼項目

家康殿に以下審査を依頼:

- **Q1**: 本 cmd の 8 観点評価 (= 仕様準拠 / 網羅性 / 法令 / ドキュメント / UX / system_relations / side_effects / observability_error_handling)
- **Q2**: Risk R1-R9 への補強・追加 risk
- **Q3**: Phase 5-1〜5-4 の順序妥当性 (= 信長案 = 服部半蔵 → 黒田 → 家康 → §3.2 改訂)
- **Q4**: 家康自身の persona 移行への opinion (= 当事者意見必須、Claude → Codex 化、Phase 5-3 担当について)
- **Q5**: 服部半蔵 (Gemini) / 黒田官兵衛 (Claude 議長) の人選妥当性、別案あれば指摘
- **Q6**: Phase 5 と Phase 3 (shutsujin) の競合 risk (= pane 配置変更が同時進行する可能性)
- **Q7**: 移行期間 (= ieyasu/kuroda 重複) の長さ推奨 (= 信長案 1 週間、family review 推奨期間)

## 11. §19 mandate 順守

- skill 新規生成禁止 (= Anti-Duplication、§19.5)
- skill 拡張時は理事長殿明示承認後 commit
- incident log は §19.1-19.4 即時起案 (= 既起案)

## 12. 信長 + 家康 + 理事長殿 の合議手順

```
[信長] 本草案起案 → 家康 8 観点 pre-review 依頼 (= 本 turn)
    ↓
[家康] 8 観点審査 → 信長応答 (= 別 turn)
    ↓
[信長] 草案 v2 (= 家康 opinion 反映) → 理事長殿御諾否確認
    ↓
[理事長殿] (a) 服部半蔵 / 黒田官兵衛 確定 (b) 別案 (c) 保留
    ↓
[信長] cmd 確定版 → queue/shogun_to_karo.yaml or 秀吉 inbox に発令
    ↓
[秀吉] 各 Phase 別 cmd 分解 → 足軽 dispatch
```

---

*草案完: 信長 (織田信長) — 2026-05-08 08:20 JST、Phase 1 着手中の並行起案*
