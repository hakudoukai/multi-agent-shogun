# Tier 1 — 2 PC 連動 冗長性確保レイヤ 設計書

> 起案: 信長 (織田信長 / shogun)
> 日時: 2026-05-08 21:35 JST
> 命令: 理事長殿御命令『元の安定した状態での立ち上げ → そこから 2 PC 体制への対応を作り上げ』(2026-05-08 21:00) + 『GO Tier 1 設計書執筆』(2026-05-08 21:25)
> 対象 cmd: cmd_redundancy_layer_for_two_pc_integrity_001 (新規起案)
> 監査依頼先: 家康一次 + 本多二次 + 黒田議長 (= 信長兼任) + Codex 6 軸 + Gemini 8 観点
> F001 一時 lift 継続: 信長単独執筆

## 0. 設計思想 — 「base 維持 + 冗長性追加装備」

```
Tier 0: 元の将軍システム (= 1 PC 想定で安定設計、触らず維持)
   +
Tier 1: 冗長性確保レイヤ (= 2 PC 連動の障害時リカバリー、追加装備、本書)
   +
Tier 2: 観測可能性 (= dashboard 統合、本書末尾)
   =
真の正解 (= 応急処置でも v3 ゼロベース過剰でもない、構造的安定)
```

### 過去議論の集約

| 提案 | 評価 | 採否 |
|------|------|------|
| v3 Python ゼロベース | ❌ 過剰、既存安定資産無視 | **撤回** |
| 旧 inbox_watcher.sh の bug 修正のみ | ❌ 不整合耐性なし | 部分採用 (Tier 0) |
| **元の base 維持 + 冗長性追加装備** | ✅ 構造的に正しい | **採用 (本書)** |

## 1. 不整合パターン (= 本日体験ベース、10 件)

| # | パターン | 本日の症状 | Tier 1 対策 |
|---|---------|-----------|-----------|
| 1 | PC 再起動後の起動順バラバラ | 5/8 朝 ieyasu watcher 0.4 起動失敗 (6h 半通信路停止) | bootstrap order 厳格化 + healthcheck |
| 2 | agent 単独落下 + 他継続 | sanada=5/ieyasu=7/maeda=19 unread 滞留 | per-agent state independent |
| 3 | 信長落ち + 復帰 | reset 前 brief で context 引き継ぎ要 | shogun resume protocol |
| 4 | watchdog 落ち + 復帰 | 本日 16:43-17:14 watcher 4 度死亡 (= 単発 nohup) | watchdog 自身も systemd or cron sentinel で守護 |
| 5 | tmux pane 番号 drift | 0.3↔0.4 swap (= 5/8 朝 incident、本日 19:04 ESCALATION 暴発の真因) | pane_registry 実態 SSoT 化 + drift detect |
| 6 | inbox 途中書込 + crash | maeda_report YAML 4 箇所破損 | atomic write (= os.replace) + symlink-aware (commit dd706ad/5109182) |
| 7 | /clear + nudge race | "/clearinbox1" 連結バグ (5/7 18:00) | LAST_CLEAR_TS gate (commit 1329f05) |
| 8 | agent context overflow hang | 本日 zombie watcher | process AND heartbeat AND watcher.alive=true の and 条件 |
| 9 | flag file stale | idle flag 残存 → 新 watcher 誤判定 | TTL + 起動時 cleanup (Tier 1 で強化) |
| 10 | dedup state drift (cross-PC) | MainPC inbox unread vs SecondPC 既読 数値ずれ | **Supabase agent_message_dedup 共有** (= hakudokai_notified_cache 既存活用) |

## 2. アーキテクチャ — 3 階層

```
┌─────────────────────────────────────────────────────────────────┐
│ Tier 2: 観測可能性 (dashboard.md + ntfy + alert)               │
├─────────────────────────────────────────────────────────────────┤
│ Tier 1: 冗長性確保レイヤ (本書、新設)                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ scripts/redundancy/                                       │ │
│  │  - system_integrity_check.sh (= 起動時 state validation)  │ │
│  │  - system_integrity_recover.sh (= 不整合 → 自動復旧)      │ │
│  │  - cross_pc_state_sync.sh (= Supabase mirror、両 PC 共有) │ │
│  │  - partition_detector.sh (= 片方 PC 落ち検知)             │ │
│  │  - graceful_shutdown_flush.sh (= 終了時 state flush)      │ │
│  └───────────────────────────────────────────────────────────┘ │
│              │                                                   │
│              ↓ Supabase mirror push/pull                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Supabase (既存資産活用、新規 table 不要)                  │ │
│  │  - pc_handshake (23,425 行、PC 間双方向対話)             │ │
│  │  - hakudokai_notified_cache (39 行、dedup state)         │ │
│  │  - codex_audit_results / gemini_audit_results (監査蓄積) │ │
│  └───────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Tier 0: 元の将軍システム (= 触らず維持)                        │
│  shutsujin_departure.sh / hakudokai_start_watchers.sh          │
│  hakudokai_watchdog.sh / inbox_watcher.sh / inbox_write.sh     │
│  hakudokai_secondpc_receiver.sh (= cross-PC bridge)           │
└─────────────────────────────────────────────────────────────────┘
```

## 3. コンポーネント仕様

### 3.1 system_integrity_check.sh — 起動時 state validation

**呼出箇所**: shutsujin_departure.sh の冒頭 + hakudokai_watchdog.sh 起動前

**チェック項目**:
1. **tmux session 存在**: shogun + multiagent + multiagent (SecondPC)
2. **pane @agent_id 4-way audit** (= scripts/checks/pane_identity.sh 既存活用)
3. **inbox YAML parse 全件** (= 破損なし確認、queue/inbox/*.yaml + queue/inbox/*.yaml.canonical)
4. **stale lock cleanup** (= queue/inbox/*.yaml.lock の 30 分超過チェック)
5. **flag file cleanup** (= ~/.openclaw/idle_*, /tmp/agent_busy_* の TTL 24h)
6. **agent CLI process 生存** (= claude / codex プロセス pane に対応)
7. **watcher / watchdog process 死活** (= heartbeat staleness + process check)
8. **Supabase 接続性** (= ~/.hakudokai/env validation)
9. **cross-PC reachability** (= ssh 1s timeout で SecondPC ping)
10. **pane_registry vs 実態 drift detect**

**出力**: `/tmp/system_integrity_<timestamp>.json` (= JSON report)

**判定**:
- 全件 PASS → `exit 0`、起動継続
- 致命的不整合 → `exit 1` + alert + recover.sh 自動呼出

### 3.2 system_integrity_recover.sh — 不整合自動復旧

**呼出条件**: integrity_check.sh が `exit 1` で報告した時、または手動

**復旧アクション**:
| 不整合 | 復旧 |
|--------|------|
| pane_registry vs 実態 drift | 実態を真値として registry を update (理事長殿事後承認、commit log 残す) |
| stale lock | 30 分超過は force release |
| inbox YAML 破損 | backup → repair (= python yaml.safe_load 試行 → 失敗時は最後の正常 commit から restore) |
| stale flag | 24h 超過は削除 |
| watcher zombie | process kill (= disable_watcher_<agent> flag 配置) → watchdog が再 spawn |
| Supabase 不通 | local-only mode (= cross-PC sync 一時停止) |
| SecondPC 不達 | partition mode (= MainPC local 完結動作継続) |

### 3.3 cross_pc_state_sync.sh — Supabase 経由 mirror (両 PC 共有)

**動作**:
1. **push**: 各 PC の local state (= queue/inbox/*.yaml + queue/watchers/*.health) を **30 秒間隔**で Supabase pc_handshake / hakudokai_notified_cache に upsert
2. **pull**: 起動時 + 30 秒間隔で Supabase から最新 state を pull → local sync
3. **conflict resolution**: timestamp-based (= 最新が勝ち)、ただし vector clock or epoch counter で「どちらが先」判定強化

**Supabase table 活用 (= 既存資産、新規不要)**:
- `pc_handshake` (23K 行運用中) — PC 間双方向対話、agent state mirror
- `hakudokai_notified_cache` (39 行) — dedup state per-role

**実装**:
```bash
#!/usr/bin/env bash
# cross_pc_state_sync.sh — local <-> Supabase mirror

source ~/.hakudokai/env

while true; do
    if [[ -f ~/.openclaw/disable_cross_pc_sync ]]; then sleep 30; continue; fi

    # PUSH: local state → Supabase
    for agent in $(ls queue/inbox/*.yaml | xargs -n1 basename | sed 's/\.yaml$//'); do
        unread_count=$(...)
        last_seen=$(...)
        # upsert to pc_handshake
        curl -X POST "$SUPABASE_URL/rest/v1/pc_handshake" \
             -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
             -d "{\"pc_origin\":\"MainPC\",\"agent_id\":\"$agent\",\"unread\":$unread_count,\"last_seen\":\"$last_seen\"}"
    done

    # PULL: Supabase → local sync
    other_pc_state=$(curl -s "$SUPABASE_URL/rest/v1/pc_handshake?pc_origin=eq.SecondPC&order=last_seen.desc.nullslast&limit=20" -H "...")
    # apply diff to local view

    sleep 30
done
```

### 3.4 partition_detector.sh — 片方 PC 落ち検知

**動作**:
1. 各 PC は 60 秒間隔で **自身の generation_counter** を Supabase pc_handshake に書込
2. 30 秒間隔で **他 PC の generation_counter** を確認
3. 5 分以上更新なし → partition 検知 → graceful degradation mode 切替
4. 復活検知 → integrity_recover.sh 呼出 → diff 同期

**通知**: ntfy + dashboard.md 更新

### 3.5 graceful_shutdown_flush.sh — 終了時 state flush

**呼出**: shutsujin_departure.sh shutdown signal、または手動

**動作**:
1. 全 watcher / watchdog に disable_* flag 配置 (= graceful exit)
2. local state を Supabase に最終 push
3. queue/inbox/*.yaml の atomic flush 確認
4. tmux session の last_state を queue/system_state.yaml に保存

## 4. データ構造 — 既存 Supabase 資産活用 (= 新規 table 不要、Anti-Duplication 順守)

### 4.1 pc_handshake (既存 23K 行)

```yaml
# 既存 schema (確認済)
columns:
  - id                  # PK
  - pc_origin           # MainPC / SecondPC
  - source_persona      # 送信元 agent_id
  - target_persona      # 受信先 agent_id
  - msg_id              # 一意 message ID
  - msg_type            # cmd_new / status_update / qa_request 等
  - payload             # JSONB
  - created_at          # 送信 timestamp
  - acknowledged_at     # 受信 timestamp
  - generation          # epoch counter (= partition 復旧時の比較)
```

Tier 1 では:
- agent state (= unread_count / last_seen / health) を pc_handshake に **mirror** (= 専用 type で書込)
- partition 検知用 generation_counter

### 4.2 hakudokai_notified_cache (既存 39 行)

```yaml
# 既存 schema
columns:
  - id                  # PK
  - role                # 受信 agent
  - msg_id              # dedup key
  - notified_at         # TTL 24h
  - pc_origin           # MainPC / SecondPC
```

Tier 1 では:
- 両 PC 共通 dedup state として活用
- watcher が msg 配達前に Supabase で重複確認

## 5. boot / shutdown sequence

### 5.1 boot sequence (= shutsujin_departure.sh 改修、または前段 hook 追加)

```bash
# Phase 0: pre-flight
bash scripts/redundancy/system_integrity_check.sh
[[ $? -ne 0 ]] && bash scripts/redundancy/system_integrity_recover.sh

# Phase 1: tmux session create (existing)
# Phase 2: agent CLI 起動 (existing)
# Phase 3: cross_pc_state_sync.sh 起動 (Tier 1 新規)
nohup bash scripts/redundancy/cross_pc_state_sync.sh > logs/cross_pc_sync.log 2>&1 &
disown

# Phase 4: partition_detector.sh 起動 (Tier 1 新規)
nohup bash scripts/redundancy/partition_detector.sh > logs/partition_detector.log 2>&1 &
disown

# Phase 5: hakudokai_watchdog.sh 起動 (existing、Tier 0 base)
nohup bash shim/hakudokai/hakudokai_watchdog.sh > logs/watchdog.log 2>&1 &
disown

# Phase 6: heartbeat 確認 (60s 後全件書込確認)
sleep 65
bash scripts/redundancy/health_dashboard.sh

# Phase 7: 通信疎通テスト (Tier 1 新規)
bash scripts/redundancy/cross_pc_smoke_test.sh
```

### 5.2 shutdown sequence

```bash
bash scripts/redundancy/graceful_shutdown_flush.sh
# → 全 watcher / watchdog stop → state Supabase push → tmux session 保存
```

## 6. partition recovery protocol

```
[MainPC 落ち、SecondPC 生存]
  SecondPC partition_detector が 5min 検知
  → SecondPC: graceful degradation mode (= local 完結継続)
  → SecondPC: ntfy 警告
  → MainPC 復活時:
     1. integrity_check.sh 実行
     2. Supabase から最新 state pull
     3. local state と diff 確認
     4. cross_pc_state_sync で両 PC 整合性確保
     5. 通常 mode 復帰

[SecondPC 落ち、MainPC 生存]
  同上 (対称)

[bridge 切断、両 PC 生存]
  両 PC partition_detector 検知
  → 両 PC: local 完結継続
  → bridge 復活後:
     1. Supabase 経由 state diff 確認
     2. timestamp-based merge
     3. 衝突は manual review 候補として alert
```

## 7. 家康 v2 verdict 反映 (= schema gate 等を Tier 1 必須要件化)

家康一次監査 verdict (= subtask_inbox_watcher_zerobase_phase2_cycle2_delivery_audit_001、FAIL_required_corrections) の指摘:

| 家康 finding | Tier 1 要件 |
|------------|------------|
| MDV2-C2-S1 (msg_id 検証なし → path traversal risk) | scripts/redundancy/system_integrity_check.sh で全 inbox msg_id を `^msg_\d{8}_\d{6}_[a-f0-9]+$` regex 検証 |
| MDV2-C2-B1 (watcher schema validation 全未実装) | inbox_watcher.sh に schema gate hook 追加 (= Tier 1 schema_validate.sh 呼出)、failure 時 dead_letter |
| MDV2-C2-B2 (book_mode_fallback 実書込なし) | Tier 1 で session_health/<agent>.book_mode.jsonl 仕様化、watcher が exit 4 時に必ず entry |
| MDV2-C2-B3 (mark_read lock/atomic/read_at 不足) | Tier 1 で mark_read を fcntl + atomic 化、read_at timestamp 必須 |

これら 4 件は Tier 1 acceptance criteria に組込必須。

## 8. 観測可能性 (Tier 2)

### 8.1 health_dashboard.sh

両 PC 全 component 状態を一覧:
```
─────────────────────────────────────────────────────────
🏯 Multi-Agent Shogun System Health (2026-05-08 21:35)
─────────────────────────────────────────────────────────
MainPC (sasebo@sasebo.or.jp):
  watchdog       : ✅ alive (uptime 5m, restart_count 0)
  inbox_watcher  : ✅ 9/9 alive
    shogun       : ✅ heartbeat fresh (15s ago)
    karo (hideyoshi)        : ✅ heartbeat fresh (12s ago)
    ashigaru1    : ✅ heartbeat fresh (8s ago)
    ashigaru2    : ✅ heartbeat fresh (10s ago)
    gunshi (ieyasu)         : ✅ heartbeat fresh (11s ago)
    ashigaru3    : ✅ heartbeat fresh (13s ago)
    takenaka     : ✅ heartbeat fresh (9s ago)
    honda        : ✅ heartbeat fresh (10s ago)
    sanada       : ✅ heartbeat fresh (12s ago)
  cross_pc_sync  : ✅ alive (last sync 12s ago)
  partition_detector : ✅ alive (last check 25s ago)

SecondPC (hakudoukai@gmail.com):
  watchdog       : ✅ alive (via Supabase)
  inbox_watcher  : ✅ 4/4 alive (maeda + ashigaru5/6/7)
  cross_pc_sync  : ✅ alive

Supabase pc_handshake: ✅ 23,425+N rows, last write 8s ago
─────────────────────────────────────────────────────────
```

### 8.2 alert 連携

- partition 検知 → ntfy CRITICAL
- watcher 死亡 cap=5 超過 → ntfy ERROR + dashboard 🚨要対応
- inbox 24h 滞留 → dashboard 注意
- pane drift 検知 → ntfy + dashboard

## 9. Phase 構成 — 時間制約なし

| Phase | 内容 | 担当 |
|-------|------|------|
| Phase A | 本書 (Tier 1 設計書) | 信長執筆、家康 + 本多 + 黒田監査 |
| Phase B | scripts/redundancy/ 5 scripts 実装 (= integrity_check / recover / cross_pc_sync / partition_detector / graceful_shutdown) | 信長 + ashigaru1/2 (= bats 担当) |
| Phase C | shutsujin_departure.sh hook 追加 (= boot sequence Tier 1 統合) | 信長 + 家老 |
| Phase D | hakudokai_watchdog.sh の Tier 1 連携 (= integrity_check 呼出 + Supabase mirror) | 信長 |
| Phase E | health_dashboard.sh + alert 連携 | 信長 |
| Phase F | 両 PC shadow mode 24h (= Tier 0 単独 vs Tier 0+1 並走、整合性確認) | 全員観察 |
| Phase G | cutover (= Tier 1 を default 起動) + retrospective | 信長 + 本多 |

各 Phase 三者監査 PASS まで進行禁止、PDCA cap 5。

## 10. 監査依頼

家康 + 本多 + 黒田 + Codex 6 軸 + Gemini 8 観点:

### 監査軸
- security: cross-PC sync の auth、Supabase RLS、ssh 経路安全性
- bugs: race condition、partition 復旧の merge logic、circular dependency
- types: msg schema、health JSON schema、generation counter 形式
- tests: bats / pytest fixture、partition 模擬テスト、shadow mode 検証
- duplication: 既存 Supabase 資産活用、Tier 0 触らず維持の徹底
- git: commit 構造、archive path、rollback path
- governance (本多): cutover gate、Anti-Duplication、§17 多医院展開整合
- 議長 (黒田): 三者整合性、設計論理、戦略観点

### 期待 verdict
PASS / PASS_WITH_CONDITIONS / FAIL の総合 + 軸別 + Phase 構成妥当性 + 反省点 a〜z mapping 完全性。

## 11. 信長最終進言

理事長殿、本書は「元の base + 冗長性追加装備」の真の正解にござる:

1. **Tier 0 元の将軍システム** = 触らず維持 (= 1 PC 想定で安定設計、9 watcher + watchdog 稼働中)
2. **Tier 1 冗長性確保レイヤ** = 追加装備 (= 2 PC 連動の障害時リカバリー、本書)
3. **Tier 2 観測可能性** = dashboard 統合
4. **既存 Supabase 資産** (= pc_handshake 23K 行 / hakudokai_notified_cache 39 行) を真値 SSoT として活用、新規 table 作成回避

家康 + 本多 + 黒田 監査 PASS なれば Phase B 実装着手、時間制約なし慎重に。

---

*信長 (織田信長) 2026-05-08 21:35 JST、Tier 1 設計書執筆完遂*
