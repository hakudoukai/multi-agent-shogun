# cmd_phase3_shutsujin_dynamic_pane_001 (草案)

> **Status**: pending_design_review (= 信長草案、家康 8 観点 review 依頼予定)
> **Drafted by**: 信長 (織田信長) 2026-05-08 08:40 JST
> **Parent**: docs/incident_logs/2026-05-08_pane_mapping_drift.md (= Phase 0、家康推奨 Phase 0-4 段階の Phase 3)
> **Pre-conditions**: Phase 1 + Phase 2 完遂 (= registry 雛形 + watchdog 動的読込実装済)

---

## 1. North Star

**Pane mapping の persistent SSoT (= queue/pane_registry.yaml) を auto-generate 化、CLAUDE.md §18.1 表 を auto-gen 区間化** することで、人手 doc と script hardcode の二重管理を構造的に消滅。pane mapping drift の根絶を完遂する。

## 2. Purpose

(1) `shutsujin_departure.sh` + `shutsujin_departure_secondpc.sh` で pane 起動時に **`tmux set -p @agent_id <name>` 確実実施** + **`queue/pane_registry.yaml` auto-generate**  
(2) `watcher / watchdog / scripts` を `tmux list-panes -F '#{@agent_id}:#{session}:#{window}.#{pane}'` 動的解決ベースに移行 (= runtime SSoT 確立)  
(3) `CLAUDE.md §18.1` 表に `<!-- AUTOGEN BEGIN/END -->` マーカー導入、registry から auto-gen (= 家康 risk 5、auto-gen blast radius 制御)  
(4) `tmux pane renumber` 追従検証 (= 家康 risk 6)  
(5) `lib/_section18_roles.sh` + `shim/hakudokai/_section18_roles.py` の hardcode 撤廃、registry 経由統一  
(6) 多医院 §17 への移行準備 (= Phase 4 連動 base、clinic_id 名前空間化下準備)

## 3. Acceptance Criteria

- `shutsujin_departure.sh` が pane 起動毎に:
  - `tmux set -p -t <pane> @agent_id <name>` 確実実施
  - `queue/pane_registry.yaml` を atomic update (= flock + symlink-safe os.replace、commit dd706ad pattern 適用)
  - registry のスキーマ versioning (= `version: 1`) 含む
- `shutsujin_departure_secondpc.sh` 同型で SecondPC 配置を registry に追記 (= cross-PC bridge 経由で MainPC registry に sync)
- `queue/pane_registry.yaml` schema:
  ```yaml
  version: 1
  generated_at: "2026-05-08T..."
  generated_by: "shutsujin_departure.sh"
  panes:
    nobunaga:
      session: shogun
      window: 0
      pane: 0
      pc: main_pc
      cli: claude
      role: shogun
    hideyoshi:
      session: multiagent
      window: 0
      pane: 0
      pc: main_pc
      cli: claude
      role: karo
    # 以下省略
  aliases:
    karo: hideyoshi
    gunshi: ieyasu
    shogun: nobunaga
  ```
- `watcher / watchdog / scripts` 動的解決:
  - `inbox_watcher.sh` が agent_id 引数を受領後、registry or tmux env で pane 解決
  - 不在 pane → fail-fast (= 虚空 nudge 防止、本朝事故再発 zero)
- `lib/_section18_roles.sh` の hardcode 撤廃 → registry 読込ベース、`section18_resolve_alias` 等の resolver は registry 参照
- `shim/hakudokai/_section18_roles.py` 同型 (= Python 側 resolver、yaml.safe_load + cache)
- `CLAUDE.md §18.1` 表 auto-gen 区間化:
  - `<!-- AUTOGEN BEGIN: pane_table -->` 〜 `<!-- AUTOGEN END: pane_table -->` マーカー
  - 区間内 = registry から auto-gen (= scripts/codegen/regen_pane_table.sh 等)
  - 区間外 = 理事長殿専権編集
- `tmux pane renumber` 追従検証:
  - test fixture: pane を kill → respawn で番号変動 → registry 自動更新 → watcher 動的追従
  - manual integration test (= Phase 1 拡張 audit skill で自動検出可)
- `~/.openclaw/registry_updating` フラグ尊重 (= 家康 risk 4、Phase 2 連動)
- 三者監査 PASS (= 移行期間中は現体系で実施、Phase 5 完遂後は新体制で)
- skill 関連実装は理事長殿明示承認後 (§19.5)

## 4. 改修対象 + 連動

| ファイル | 改修内容 |
|---------|---------|
| `shutsujin_departure.sh` | pane 起動 + tmux env 設定 + registry 書込 |
| `shutsujin_departure_secondpc.sh` | SecondPC 同型 + cross-PC sync |
| `scripts/inbox_watcher.sh` | pane 引数を agent_id のみに簡略化、動的解決 |
| `shim/hakudokai/hakudokai_watchdog.sh` | (= Phase 2 で済) registry 読込側、本 cmd で動的更新追従 |
| `shim/hakudokai/hakudokai_start_watchers.sh` | INBOX_AGENTS hardcode 撤廃、registry 経由 |
| `lib/_section18_roles.sh` | hardcode resolver → registry 読込 resolver |
| `shim/hakudokai/_section18_roles.py` | 同上 (Python) |
| `CLAUDE.md §18.1` | auto-gen 区間マーカー導入 (理事長殿明示承認) |
| `scripts/codegen/regen_pane_table.sh` (新規) | registry → CLAUDE.md §18.1 表 生成 script |
| `scripts/checks/pane_identity.sh` | (= Phase 1 で拡張) 4-way audit が registry 経由統一 |

## 5. Risk 分析 (= 信長草案、家康 8 観点 review 依頼)

| # | risk | 影響 | 対策 |
|---|------|------|------|
| R1 | shutsujin 改修中の pane 全停止 | 高 | 改修は **追加機能** として段階導入、既存 hardcode は段階的廃止。改修完了前は dual-write (= 旧 hardcode + 新 registry 両方) |
| R2 | registry auto-gen 中の watcher 干渉 | 中 | flock + `~/.openclaw/registry_updating` フラグ尊重 (= Phase 2 watchdog 連動) |
| R3 | pane renumber 追従の test fixture 限定 | 中 | manual + automated test 両立、Phase 1 拡張 audit skill が継続検出 |
| R4 | CLAUDE.md auto-gen blast radius (= 家康 risk 5) | 高 | `<!-- AUTOGEN BEGIN/END -->` マーカー厳格、区間外編集 = 理事長殿専権、auto-gen 衝突は CI 検出 |
| R5 | 多医院展開時の clinic_id 名前空間 (= 家康 risk 3) | 中 | registry schema に `pc:` field、clinic_id 接頭辞は Phase 4 で導入 |
| R6 | lib/_section18_roles.sh と registry の二重管理過渡期 | 中 | Phase 3 完遂後 hardcode 完全撤廃、過渡期は registry 主・hardcode 副 (fallback) |
| R7 | SecondPC shutsujin の cross-PC 配置同期 | 中 | Supabase pc_handshake 経由で MainPC registry に sync、conflict は MainPC 主 |
| R8 | symlink alias 保護 (= 過去事故再発防止) | 低 | dd706ad fix 適用、scripts/checks/inbox_alias_integrity.sh 監視 |
| R9 | shutsujin の pkill 利用 (D006 違反) | 高 | 信長/家老/足軽からは pkill 禁止 (= D006)。shutsujin は infrastructure 層、Lord 起動時のみ pkill 許容 (= 既存運用通り) |

## 6. Phase 3 sub-phase 分解

### Phase 3-1: registry schema 確定 + 雛形 auto-gen (低 risk)
- queue/pane_registry.yaml schema 確定 (= §3 上記スキーマ)
- shutsujin_departure.sh に registry 書込ロジック追加 (= dual-write、既存 hardcode 並行)
- atomic write + flock + symlink 保護 (commit dd706ad pattern)
- 担当推奨: ashigaru1

### Phase 3-2: watcher / lib / shim の registry 経由読込 (= dual-read 期間)
- inbox_watcher.sh を agent_id 引数のみに簡略化、registry → tmux env の優先順位
- lib/_section18_roles.sh + shim/_section18_roles.py の resolver を registry 経由に
- 既存 hardcode は fallback で残置 (= 段階移行)
- 担当推奨: ashigaru2

### Phase 3-3: tmux pane renumber 追従検証 + manual test
- pane kill → respawn で renumber 発生
- registry 自動更新 + watcher 動的追従
- Phase 1 audit skill が drift 即時検出
- 担当推奨: ashigaru3

### Phase 3-4: CLAUDE.md §18.1 auto-gen 区間化 (= 理事長殿明示承認後)
- AUTOGEN BEGIN/END マーカー導入
- scripts/codegen/regen_pane_table.sh 新規作成
- 区間内表 = registry → 自動生成
- 担当: 信長直筆 (理事長殿明示承認後 commit)

### Phase 3-5: hardcode 完全撤廃 (= 移行期間終了)
- lib/_section18_roles.sh + shim/_section18_roles.py の旧 hardcode 削除
- shutsujin の dual-write を新 registry 単一書込に
- 担当推奨: ashigaru1

### Phase 3-6: SecondPC shutsujin 同型改修 (= cross-PC 同期)
- shutsujin_departure_secondpc.sh 改修
- Supabase pc_handshake 経由で MainPC registry sync
- 担当: 前田 (= SecondPC 家老、自走、Phase 5-1 完遂後の余裕で実施推奨)

## 7. 命令文 (= 家老秀吉宛、Phase 1+2 完遂後発令)

```
家老秀吉、本 cmd を分解し以下 sub-phase で順次足軽に発令:

Phase 3-1: registry schema 雛形 + dual-write (ashigaru1、低 risk から)
Phase 3-2: watcher / lib / shim 動的読込 (ashigaru2、Phase 3-1 完遂後)
Phase 3-3: pane renumber 追従検証 (ashigaru3、Phase 3-1+2 完遂後)
Phase 3-4: CLAUDE.md §18.1 auto-gen (信長直筆、理事長殿明示承認後)
Phase 3-5: hardcode 完全撤廃 (ashigaru1、Phase 3-4 完遂後)
Phase 3-6: SecondPC shutsujin 同型 (前田、Phase 3-5 完遂後 or 並行可)

各 sub-phase 完遂後の動作確証必須 (= 三者監査 PASS、運用 1 日試運転後 close 判定)。
PDCA max=5、scope 大ゆえ 各 sub-phase 1-2 cycle 想定。
```

## 8. Pre-conditions / Dependencies

- ✅ Phase 0: docs/incident_logs/2026-05-08_pane_mapping_drift.md (= commit f5534b0)
- ⏳ Phase 1: cmd_phase1_pane_identity_4way_audit_001 (= queue/pane_registry.yaml 雛形作成済)
- ⏳ Phase 2: cmd_phase2_watchdog_registry_001 (= registry 読込側 watchdog 実装済)
- ⏳ Phase 3: 本 cmd
- ⏳ Phase 5: cmd_phase5_audit_persona_restructure_001 (= Phase 3-2 完遂後着手安全、ieyasu pane → kuroda 置換)
- 後続 Phase 4: 多医院 §17 連動 (= Phase 3 schema が clinic_id 名前空間 ready)

## 9. 並行運用注意 (= Phase 5 との関係)

Phase 5-2 (= ieyasu pane → kuroda 置換) は本 Phase 3-2 完遂後着手が安全:
- Phase 3-2 で watcher が registry 経由で動的解決 → ieyasu/kuroda 切替が透過的
- Phase 3-2 完遂前に Phase 5-2 を着手すると、shutsujin 改修と pane 配置変更が同時進行 → 混乱

家康 risk 6 (= pane renumber 追従) も Phase 3-3 で検証要、Phase 5-2 はその後着手。

## 10. Related Resources

- docs/incident_logs/2026-05-08_pane_mapping_drift.md (= Phase 0、信長案 + 家康審査)
- docs/cmd_phase2_watchdog_registry_draft.md (= 連動)
- docs/cmd_phase5_audit_persona_restructure_draft.md (= 連動)
- shutsujin_departure.sh + shutsujin_departure_secondpc.sh (= 改修対象)
- lib/_section18_roles.sh + shim/hakudokai/_section18_roles.py (= 改修対象)
- CLAUDE.md §18.1 (= auto-gen 区間化対象、理事長殿専権)
- queue/pane_registry.yaml (= Phase 1 で雛形、Phase 3 で auto-gen)
- 家康 8 観点審査回答: msg_20260508_075934_7cee9b09

## 11. 家康 8 観点 pre-review 依頼項目 (Q1-Q7)

- **Q1**: 本 cmd の 8 観点評価
- **Q2**: 草案記載 R1-R9 risk への補強・追加 risk
- **Q3**: Phase 3-1〜3-6 の sub-phase 順序妥当性
- **Q4**: registry schema (§3) の妥当性、追加 field 提案
- **Q5**: Phase 5-2 (ieyasu → kuroda) との並行運用 risk (= §9)
- **Q6**: CLAUDE.md auto-gen 区間化 implementation (= R4)、AUTOGEN マーカー位置の推奨
- **Q7**: SecondPC shutsujin (= 3-6) cross-PC sync の Supabase 経路 vs 別経路の比較

## 12. §19 mandate 順守

- skill 新規生成禁止 (= Anti-Duplication)
- shutsujin 改修自体は task で skill 範疇外
- 過去関連 skill (= skills/pane-identity-verify/) は Phase 1 で拡張済の前提

## 13. 信長 + 家康 + 理事長殿 の合議手順

```
[信長] 本草案起案 (本 turn)
    ↓
[家康] 8 観点 pre-review (= Phase 1 三者監査優先後の余裕)
    ↓
[信長] 草案 v2 (= 家康 opinion 反映)
    ↓
[Phase 1+2 完遂確認後]
    ↓
[信長] cmd 確定版 → 秀吉発令
    ↓
[秀吉] sub-phase 別 ashigaru dispatch
```

---

*草案完: 信長 (織田信長) — 2026-05-08 08:40 JST、Phase 1 着手中の並行起案 (Phase 2 + Phase 5 と同時起案、Phase 0-4 段階完備)*
