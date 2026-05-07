# cmd_phase2_watchdog_registry_001 (草案)

> **Status**: pending_design_review (= 信長草案、家康 8 観点 review 依頼予定)
> **Drafted by**: 信長 (織田信長) 2026-05-08 08:30 JST
> **Parent**: docs/incident_logs/2026-05-08_pane_mapping_drift.md (= Phase 0、家康推奨 Phase 0-4 段階の Phase 2)
> **Pre-conditions**: cmd_phase1_pane_identity_4way_audit_001 完遂 (= queue/pane_registry.yaml 雛形作成済)

---

## 1. North Star

`shim/hakudokai/hakudokai_watchdog.sh` が **旧名 (karo/gunshi) hardcode + 不在 pane (multiagent:0.8) 管理** ゆえ、本朝 pane mapping drift 事故 + 信長補完 watcher 死亡 (= ashigaru2/3/ieyasu 監視外) の二次要因。registry 動的読込化 + 新名対応で構造的に解消、watcher 群の死活監視を新体制に整合させる。

## 2. Purpose

(1) `INBOX_AGENTS` hardcode 撤廃 → `queue/pane_registry.yaml` 動的読込化  
(2) 旧名 (karo/gunshi/shogun) → 新名 (hideyoshi/ieyasu/nobunaga) 対応 + alias 互換維持  
(3) 不在 pane (multiagent:0.8) 廃止 → 実 pane に動的解決  
(4) ashigaru2 / ashigaru3 / maeda 監視対象追加  
(5) registry race 対策 = `flock` (= 家康 risk 1)  
(6) 手動停止フラグ尊重 (= 家康 risk 4、§15 SH6 安全装置)

## 3. Acceptance Criteria

- `shim/hakudokai/hakudokai_watchdog.sh` の `INBOX_AGENTS` hardcode 廃止 → `queue/pane_registry.yaml` 動的読込
- 旧名 alias 経由で karo→hideyoshi / gunshi→ieyasu / shogun→nobunaga の後方互換性維持 (= `lib/_section18_roles.sh` の resolver 利用)
- multiagent:0.8 への nudge 廃止 → registry 経由で実 pane (= ieyasu 0.3 等) 動的解決
- 監視対象追加: hideyoshi (0.0) / ashigaru1 (0.1) / ashigaru2 (0.2) / ieyasu (0.3、Phase 5-2 で kuroda 置換予定) / nobunaga (shogun:0.0) / ashigaru3 (= 非常時、登録のみ) / maeda (SecondPC、cross-PC bridge 経由)
- registry 読込時 `flock` 必須 (= race 対策、inbox_write.sh 同 pattern)
- `~/.openclaw/registry_updating` 存在時は restart 抑制 (= 家康 risk 4)
- §15 SH6 (self-restart) 危険パターン回避: **再起動上限 5/h** + escalation 機構 + 2026-05-05 SecondPC 暴走事件型 防止
- 信長補完 watcher (= 2026-05-08 朝起動の 6 体) のような **手動起動 watcher を kill しない** 保証 (= 既存 INBOX_AGENTS 以外の watcher は監視対象外で温存)
- 三者監査 PASS (= 移行期間中は現体系で実施、Phase 5 完遂後は新体制で)

## 4. 改修内容詳細

### 4.1 旧 hardcode (廃止対象)

```bash
INBOX_AGENTS="karo:multiagent:0.0 ashigaru1:multiagent:0.1 gunshi:multiagent:0.8 shogun:shogun:0.0"
```

### 4.2 新 動的読込 (= registry ベース)

```bash
# Pseudocode
load_inbox_agents() {
  local registry="${SCRIPT_DIR}/queue/pane_registry.yaml"
  if [ ! -f "$registry" ]; then
    echo "[watchdog] WARN: registry not found, falling back to last-known config" >&2
    return 1
  fi
  
  # flock with 5s timeout (= race 対策)
  exec 200<"$registry"
  flock -w 5 200 || { echo "[watchdog] WARN: registry lock timeout" >&2; return 1; }
  
  # YAML parse via Python
  INBOX_AGENTS=$(python3 -c "
import yaml
with open('$registry') as f:
    d = yaml.safe_load(f)
panes = d.get('panes', {})
out = []
for agent_id, pane in panes.items():
    out.append(f'{agent_id}:{pane}')
print(' '.join(out))
")
  exec 200<&-
  return 0
}
```

### 4.3 手動停止フラグ尊重 (= 家康 risk 4)

```bash
restart_watcher() {
  if [ -f "$HOME/.openclaw/registry_updating" ]; then
    log "[watchdog] SKIP restart: registry_updating flag set"
    return 1
  fi
  if [ -f "$HOME/.openclaw/global_disable" ] || [ -f "$HOME/.openclaw/disable_inbox_watcher" ]; then
    log "[watchdog] SKIP restart: manual stop flag set"
    return 1
  fi
  # Restart cap check (5/h)
  ...
}
```

### 4.4 信長補完 watcher 温存保証

新 INBOX_AGENTS リスト外の watcher (= 信長が緊急起動した補完 watcher) は **kill 対象外** とする。watchdog の責務 = 自身が立てた watcher の死活監視のみ。

実装: `pkill -f "inbox_watcher.sh ${agent}"` の対象を INBOX_AGENTS で列挙された agent_id 限定 (= 現状動作だが文書化、ashigaru2 の補完 watcher 等が誤 kill されない保証)。

## 5. Phase 連動関係

| Phase | 内容 | 本 cmd との関係 |
|-------|------|----------------|
| Phase 0 (= f5534b0) | incident log | 本 cmd の根拠 |
| Phase 1 | skills/pane-identity-verify/ 拡張 + registry 雛形 | **Phase 1 で registry 雛形作成済の前提**、本 cmd は registry 読込側実装 |
| **Phase 2 (= 本 cmd)** | watchdog 改修 = registry 読込化 | 〜 |
| Phase 3 | shutsujin 改修 = tmux env 動的解決 + registry 書込み | Phase 2 完遂後着手、書込側 registry 動的更新化 |
| Phase 5 | 監査階層変更 + persona renaming | Phase 2 + Phase 3 完遂前提、ieyasu pane (0.3) を kuroda に置換時 watchdog が新名追従 |

## 6. Risk 分析 (= 信長草案、家康 8 観点 review 依頼)

| # | risk | 対策 |
|---|------|------|
| R1 | registry YAML race (= 家康 risk 1) | flock 5s timeout、inbox_write.sh と同 pattern |
| R2 | 既存 watchdog rolling update | watchdog process は `kill` 不可 (D006)、再起動は理事長殿/手動許可下 |
| R3 | 旧名 alias 維持の後方互換 | lib/_section18_roles.sh resolver 経由で karo→hideyoshi 解決、新旧両 inbox path に書込/読込両立 |
| R4 | 監視対象追加で過剰監視 | INBOX_AGENTS は registry 反映、registry に記載のない agent は監視対象外 (= 信長補完 watcher 温存) |
| R5 | §15 SH6 自動再起動暴走 | 5/h 上限 + 同一 error 連続 3 回で escalation、2026-05-05 SecondPC 暴走防止 |
| R6 | watchdog 改修中の watcher 全死亡 | 改修は **追加機能** として段階導入、既存 INBOX_AGENTS hardcode は段階的廃止 |
| R7 | registry スキーマ変更で既存 watcher 互換崩れ | スキーマ versioning (= `version: 1` 等)、互換破壊時は自動 fallback |

## 7. 命令文 (= 家老秀吉宛)

```
家老秀吉、本 cmd を分解し ashigaru1 (= Phase 6 cycle2 push 確認後の余裕、または ashigaru3 軽量起動) に
発令されたし。Phase 1 完遂後 (= queue/pane_registry.yaml 雛形作成確認後) に着手。

主要工程:
- shim/hakudokai/hakudokai_watchdog.sh 改修 (= 本体)
- shim/hakudokai/hakudokai_start_watchers.sh の旧名 hardcode も連動更新 (= Boy Scout Rule §14)
- 改修テスト = registry 読込動作 + 旧名 alias 互換 + flock 動作 + 手動停止フラグ尊重 + 信長補完 watcher 温存

PDCA max=5、安全な rolling update のため改修ステップは段階的に区切り、各段階で動作確証必須。
```

## 8. Pre-conditions / Dependencies

- ✅ Phase 0: docs/incident_logs/2026-05-08_pane_mapping_drift.md (= commit f5534b0)
- ⏳ Phase 1: cmd_phase1_pane_identity_4way_audit_001 完遂 (= queue/pane_registry.yaml 雛形作成)
- ⏳ Phase 2: 本 cmd
- ⏳ Phase 3: 後続 cmd (= shutsujin 改修)、Phase 2 完遂後着手
- ⏳ Phase 5: 後続 cmd (= 監査階層 + persona renaming)、Phase 2+3 完遂後

## 9. Related Resources

- docs/incident_logs/2026-05-08_pane_mapping_drift.md (= Phase 0)
- docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md (= §15 SH6 暴走事件、再発防止参照)
- docs/cmd_phase5_audit_persona_restructure_draft.md (= Phase 5 草案)
- shim/hakudokai/hakudokai_watchdog.sh (= 改修対象)
- shim/hakudokai/hakudokai_start_watchers.sh (= 連動更新対象)
- lib/_section18_roles.sh (= 旧名 alias resolver、本 cmd で利用)
- queue/pane_registry.yaml (= Phase 1 で作成、本 cmd で読込)
- 家康 8 観点審査回答: msg_20260508_075934_7cee9b09 (= Phase 0-4 設計 base)

## 10. 家康 8 観点 pre-review 依頼 (Q1-Q5)

- **Q1**: 本 cmd の 8 観点評価
- **Q2**: 草案記載 R1-R7 risk への補強・追加 risk
- **Q3**: 改修順序 (= INBOX_AGENTS 段階的撤廃 vs 一気切替) の推奨
- **Q4**: §15 SH6 上限 (= 信長案 5/h) の妥当性
- **Q5**: Phase 5 (= ieyasu pane → kuroda 置換) との競合 risk

## 11. §19 mandate 順守

- skill 新規生成禁止 (= Anti-Duplication)
- watchdog 改修自体は task で skill 範疇外
- 暴走事件 (2026-05-05) との関連で `docs/incident_logs/` への 5 Why 追記検討

## 12. 信長 + 家康 + 理事長殿 の合議手順

```
[信長] 本草案起案 (本 turn)
    ↓
[家康] 8 観点 pre-review (= Phase 1 三者監査優先後の余裕時間)
    ↓
[信長] 草案 v2 (= 家康 opinion 反映)
    ↓
[Phase 1 完遂確認後]
    ↓
[信長] cmd 確定版 → 秀吉発令
    ↓
[秀吉] ashigaru dispatch
```

---

*草案完: 信長 (織田信長) — 2026-05-08 08:30 JST、Phase 1 着手中の並行起案 (Phase 5 と同時)*
