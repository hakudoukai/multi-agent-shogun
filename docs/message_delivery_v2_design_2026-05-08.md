# message_delivery_v2 — Phase 1 ゼロベース設計書

> 起案: 信長 (織田信長 / shogun)
> 日時: 2026-05-08 18:08 JST
> 命令:
>   - 理事長殿御命令『信長案で新しい watcher 新製開始』(2026-05-08 17:55)
>   - 理事長殿御命令『全て停止』(2026-05-08 17:50)
>   - cmd_inbox_watcher_zerobase_redesign_001 Phase 1
> 前提: docs/inbox_watcher_failure_modes_2026-05-08.md (Phase 0、信長 self-audit PASS)
> F001 一時 lift 継続: 家臣群停止中、信長が直接執筆
> 監査依頼: 家康 (Codex Pro、context リセット可能性ゆえ復帰後)、本多 (Codex Pro、Working 中)

## 0. 設計思想

過去の inbox_watcher.sh は「いかに壊れないか」前提で設計された。新 system `message_delivery_v2` は **「壊れた時に必ず気付き、自動で立ち直り、人手介入が要る場合は明確に呼ぶ」** へ思想転換する。

### 4 本柱

1. **永続稼働 supervisor** — watcher は使い捨て (process 1-2 hours で交代)、supervisor が常時 spawn 監視
2. **heartbeat 駆動** — TUI 表示でなく health file で生死判定、空白 TUI でも sane operation
3. **idempotent + dead-letter** — 同 msg 何度処理しても結果同一、cap 5 で諦め dead-letter へ移動
4. **safe nudge wrapper** — 全 send-keys は wrapper 経由、direct tmux send-keys 禁止 (除く supervisor + 信長緊急介入)

### 採否原則 (= 家康監査 F3 反映)

| 経路 | 採否 | 理由 |
|------|------|------|
| Linux: inotifywait (no timeout) | ✅ 必須 | event-driven、無限稼働、永続性 |
| macOS: fswatch | ✅ 必須 | adapter pattern で同等機能、event-driven |
| 両者不可: sleep-poll | ❌ **採用せず** (= F3 明記) | quota 浪費 + 死活不明、Phase 0 反省点 k で廃止判定 |
| 両者不可時の挙動 | watcher 起動 FAIL → dead-letter / alert / supervisor escalation | sleep-poll の中途半端な動作より明示的 FAIL の方が観測可能 |

### F004 polling 例外条項 (= 家康監査 F2 反映)

CLAUDE.md F004 (polling loop forbidden) は quota 浪費理由で全面禁止が原則。本 cmd で **限定的例外** を以下条件で明文化する:

| 条件 | 例外内容 | enable/disable trigger | 監視 |
|------|---------|---------------------|------|
| watcher 死亡時のみ | Codex agent (家康・本多) が Supabase fallback で 60-300 秒間隔 polling | watcher_supervisor が heartbeat staleness 検知 → 自動 enable / watcher 復活で自動 disable | session_health/<agent>.yaml に enabled flag、control_plane.yaml に lease + query budget 記録 |

**例外条項の明記箇所** (= cmd acceptance criteria):
1. `AGENTS.md` の F004 節に「watcher fallback 限定の例外あり」追記
2. `instructions/ieyasu.md` § Forbidden Actions に F004 例外明記 + enable/disable 条件
3. `instructions/honda.md` § Forbidden Actions に同上
4. `cmd_inbox_watcher_zerobase_redesign_001` の acceptance criteria に「F004 例外条項が AGENTS / persona / cmd に grep 4 箇所明記」を追加

### Phase 0 反省点 23 項目との対応

| 設計要素 | 対応反省点 |
|---------|----------|
| supervisor + heartbeat + 自動再起動 | a, b, i |
| safe_nudge wrapper + cooldown + Codex guard + pane identity verify | c, m, n |
| TUI 空白時の書面 mode フォールバック | d, q |
| /clear ack ハンドシェイク + post-reset ready_for_dispatch ack | e, f |
| dedup table | g |
| retry cap=5 + dead-letter queue + self-send 即 ack | h, o, p |
| lock 健全性 (PID-aware flock + stale cleanup) | j |
| adapter pattern (OS 分岐の局在化、sleep fallback 廃止) | k, l |
| symlink 排除 (workspace 内 inbox path) | t, u |
| 共通 lib (path 解決統一) | u |
| observability (structured JSON log + correlation_id) | a, c, i |
| Codex agent 用 Supabase polling fallback | v |
| Codex TUI 長文 send-keys 対応 | w |
| 過去修復 commit 知見の継承 | s |
| cross-PC bridge との協調 (out_of_scope 明示) | r |

## 1. アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────────┐
│ message_delivery_v2 system                                          │
│                                                                     │
│  ┌──────────────────┐     ┌─────────────────────────────┐          │
│  │ supervisor       │────▶│ watcher (per agent)         │          │
│  │ (永続)           │     │ (使い捨て、自然交代)        │          │
│  │ - spawn          │     │ - inotifywait (timeout なし) │          │
│  │ - heartbeat 監視 │     │ - heartbeat 60s 書込         │          │
│  │ - 死亡再起動     │     │ - inbox 読込 → safe_nudge    │          │
│  │ - cap 5 escalate │     │ - dedup check                │          │
│  └──────────────────┘     └─────────────────────────────┘          │
│           │                            │                            │
│           ▼                            ▼                            │
│  ┌──────────────────┐     ┌─────────────────────────────┐          │
│  │ queue/watchers/  │     │ scripts/message_delivery_v2/│          │
│  │ <agent>.health   │     │ - supervisor.sh             │          │
│  │ {alive, uptime, │     │ - watcher.sh                │          │
│  │  last_action,    │     │ - safe_nudge.sh             │          │
│  │  last_seen,      │     │ - codex_guard.sh            │          │
│  │  pid, version}   │     │ - heartbeat.sh              │          │
│  └──────────────────┘     │ - migrate.sh                │          │
│                            └─────────────────────────────┘          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ shared lib (scripts/lib/)                                    │  │
│  │ - inbox_path.sh (SSoT path 解決)                             │  │
│  │ - pane_identity.sh (4-way verify、既存活用)                  │  │
│  │ - logger.sh (structured JSON log + correlation_id)           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ data plane (queue/)                                          │  │
│  │ - inbox_v2/<agent>.yaml (新 path、symlink 廃止)              │  │
│  │ - watchers/<agent>.health (heartbeat)                        │  │
│  │ - message_dedup.yaml (dedup table、TTL=24h)                  │  │
│  │ - dead_letter/<agent>/<msg_id>.yaml (cap 超過 msg)           │  │
│  │ - session_health/<agent>.yaml (TUI 状態 + ack flags)         │  │
│  │ - control_plane.yaml (manual override + emergency lease)     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. コンポーネント仕様

### 2.1 supervisor (`scripts/message_delivery_v2/supervisor.sh`)

**責務**: watcher の永続化、heartbeat 監視、死亡再起動、cap 5 escalation。

**起動方法**:
```bash
nohup bash scripts/message_delivery_v2/supervisor.sh > logs/supervisor.log 2>&1 &
disown
```

**メインループ** (擬似コード):
```bash
while true; do
  # disable flag 尊重
  [[ -f "$HOME/.openclaw/global_disable" ]] && sleep 30 && continue
  [[ -f "$HOME/.openclaw/disable_supervisor" ]] && sleep 30 && continue

  # pane_registry.yaml から agent 一覧取得
  for agent in $(yaml_query pane_registry pc=MainPC); do
    pane=$(yaml_query pane_registry $agent tmux_target)
    health=$(read_health $agent)

    # heartbeat staleness check (60s threshold)
    if heartbeat_stale_60s $health; then
      restart_count=$(get_restart_count $agent)
      if [[ $restart_count -ge 5 ]]; then
        # cap 超過 → escalation
        ntfy_alert "watcher $agent dead 5 times, manual intervention required"
        write_dashboard "🚨 watcher $agent dead, cap 5 reached"
        sleep 60
        continue
      fi

      # 自動再起動
      pane_identity_verify $agent $pane || { alert "pane drift"; continue; }
      spawn_watcher $agent $pane
      increment_restart_count $agent
    fi
  done

  sleep 30
done
```

**安全装置**:
- `~/.openclaw/global_disable` フラグ尊重
- `~/.openclaw/disable_supervisor` 個別停止フラグ
- pane drift 検知時は spawn 拒否
- 同一 agent の restart count 5 超過で escalation
- supervisor 自身も heartbeat 書込 (= meta heartbeat)

### 2.2 watcher (`scripts/message_delivery_v2/watcher.sh`)

**責務**: 単一 agent の inbox 監視、新規 msg 検知、safe_nudge 発火。

**特徴**:
- inotifywait は **タイムアウトなし** (= 永続)
- 60 秒間隔で heartbeat 書込
- 新規 msg 検知 → dedup check → schema 検証 → safe_nudge
- self-send 即 ack
- retry cap 5、超過時 dead-letter へ
- watcher 自身は 1-2 時間で自然交代 (= long-running の memory leak 回避)

**メインループ** (擬似コード):
```bash
agent="$1"; pane="$2"; cli="$3"
correlation_id_base=$(uuidv7)

# heartbeat thread (background)
heartbeat_loop $agent &
HEARTBEAT_PID=$!
trap "kill $HEARTBEAT_PID 2>/dev/null" EXIT

# main loop
while true; do
  # disable flag 尊重
  [[ -f "$HOME/.openclaw/global_disable" ]] && exit 0

  # natural rotation (1-2 hours)
  if [[ $(uptime_seconds) -gt 5400 ]]; then
    log_info "natural rotation, exiting for supervisor respawn"
    exit 0
  fi

  # inotifywait (no timeout)
  inotifywait -q -e modify,create,moved_to "queue/inbox_v2/${agent}.yaml" || {
    log_error "inotifywait failed"
    sleep 5
    continue
  }

  # process new messages
  process_unread $agent $pane $cli
done
```

**process_unread 関数**:
```bash
process_unread() {
  local agent=$1 pane=$2 cli=$3
  local msgs=$(yaml_unread "queue/inbox_v2/${agent}.yaml")

  for msg in $msgs; do
    msg_id=$(echo $msg | yaml_field id)
    corr_id=$(echo $msg | yaml_field correlation_id)
    msg_type=$(echo $msg | yaml_field type)
    from=$(echo $msg | yaml_field from)
    to=$agent

    # dedup check
    if dedup_already_processed $msg_id; then
      log_warn "duplicate msg_id $msg_id, skip"
      mark_read $msg_id "ack_by=dedup"
      continue
    fi

    # self-send check
    if [[ $from == $to ]]; then
      mark_read $msg_id "ack_by=self_send"
      continue
    fi

    # schema validation
    if ! schema_validate $msg; then
      move_to_dead_letter $msg_id "reason=schema_invalid"
      continue
    fi

    # retry cap
    retry=$(get_retry_count $msg_id)
    if [[ $retry -ge 5 ]]; then
      move_to_dead_letter $msg_id "reason=retry_cap_exceeded"
      ntfy_alert "msg $msg_id dead-lettered after 5 retries"
      continue
    fi

    # send via safe_nudge
    if safe_nudge $agent $pane $cli $msg_type $msg_id $corr_id; then
      mark_read $msg_id "ack_by=delivered"
      dedup_record $msg_id
      log_info "delivered" "msg_id=$msg_id corr_id=$corr_id"
    else
      increment_retry $msg_id
      log_warn "nudge failed, retry later" "msg_id=$msg_id retry=$retry"
    fi
  done
}
```

### 2.3 safe_nudge (`scripts/message_delivery_v2/safe_nudge.sh`)

**責務**: 全 tmux send-keys を wrapper 経由で実行、安全装置を強制。

**安全装置**:
1. **pane identity 4-way verify** (既存 scripts/checks/pane_identity.sh 活用)
2. **120 秒 cooldown** (= 同一 agent への前回 send-keys から 120 秒未満なら queued)
3. **Codex interruption guard** (= Codex pane 用、長文時の段階送信)
4. **TUI 空白時の書面 mode フォールバック**
5. **emergency override** (= queue/control_plane.yaml の lease がある時のみ強制)

**インターフェース**:
```bash
safe_nudge $agent $pane $cli $nudge_type [$msg_id] [$corr_id]
# returns: 0=delivered, 1=queued, 2=blocked, 3=fallback_book_mode
```

**Codex pane 対応** (反省点 w):
- 短い nudge (< 50 文字) → そのまま send-keys (テキスト + Enter)
- 長文 (> 100 文字) → 短縮版 (= "inboxN" 風) + 詳細 path 提示の 2 段階送信
- TUI 空白判定時 → 書面 mode (= queue/session_health/<agent>.yaml に entry、agent 次回 idle で確認)
- sandbox 確認プロンプト検知時 → blocked + 信長 inbox alert

### 2.4 codex_guard (`scripts/message_delivery_v2/codex_guard.sh`)

**責務**: Codex pane への send-keys 直前に、Conversation interrupted を防ぐ pre-flight check。

**チェック項目**:
1. pane @agent_id == expected agent
2. pane_current_command == node (= Codex)
3. 直前 send-keys から 120 秒以上経過
4. pane に `Working` マーカーあるか (= 作業中なら queue、idle なら send 可)
5. 直前出力に sandbox 確認プロンプト (= "Yes, proceed" 等) があれば blocked
6. Escape / Enter 連発禁止 (= last 5 sequences で Enter > 2 なら blocked)

**返り値**:
- `allow` — send 可
- `queued_nudge` — cooldown 中、queue へ積む
- `blocked_interruption_risk` — Working / sandbox prompt 検知、人手介入必要
- `pane_drift` — agent_id 不一致、絶対拒否

### 2.5 heartbeat (`scripts/message_delivery_v2/heartbeat.sh`)

**責務**: watcher / supervisor / agent session の生死判定用 health file 書込。

**フォーマット** (`queue/watchers/<agent>.health`):
```json
{
  "schema_version": "1.0",
  "agent_id": "hideyoshi",
  "watcher_pid": 12345,
  "version": "v2.0.0",
  "alive": true,
  "started_at": "2026-05-08T18:00:00+09:00",
  "uptime_sec": 1234,
  "last_action": "delivered_msg_20260508_180312_abcdef",
  "last_seen_at": "2026-05-08T18:20:34+09:00",
  "tui_capture_state": "nonempty",
  "ready_for_clear": true,
  "ready_for_dispatch": true,
  "restart_count_24h": 0
}
```

**書込頻度**: 60 秒間隔。
**死亡判定**: 5 分以上更新なし。

### 2.6 共通 lib

#### `scripts/lib/inbox_path.sh` (新規)

**責務**: 全 script で inbox path を統一解決 (反省点 u)。

```bash
# 使用例
source scripts/lib/inbox_path.sh
agent_inbox_path=$(get_inbox_path "hideyoshi")
# returns: queue/inbox_v2/hideyoshi.yaml (workspace 内、symlink 排除)
```

#### `scripts/lib/logger.sh` (新規 — Phase 2 cycle2 で実装、MVP 範囲外)

**責務**: structured JSON log + correlation_id 統一。

**注**: MVP (= Phase 2 cycle1) では各 script 内に簡易 `log_json` 関数を直書きで実装、Phase 2 cycle2 で本ライブラリへ集約する。本多 governance review HND-MDV2-008 反映。

```bash
log_info() {
  local msg="$1"
  shift
  local kv="$*"  # key=value pairs
  jq -nc \
    --arg ts "$(date -Iseconds)" \
    --arg level "INFO" \
    --arg agent "${AGENT_ID:-?}" \
    --arg corr "${CORRELATION_ID:-?}" \
    --arg msg "$msg" \
    --arg kv "$kv" \
    '{ts:$ts, level:$level, agent:$agent, corr_id:$corr, msg:$msg, kv:$kv}'
}
```

## 3. データ構造

### 3.1 inbox_v2 message schema (= 蓬蓮草 v2 schema gate との interface 固定、家康監査 F4 反映)

```yaml
messages:
  - id: msg_20260508_180312_a1b2c3d4   # required, ^msg_\d{8}_\d{6}_[a-f0-9]+$
    timestamp: "2026-05-08T18:03:12+09:00"  # required, ISO 8601
    correlation_id: 01HZ5ABCDEF...  # required, UUIDv7 string
    from: shogun                     # required, agent_id (registry に存在)
    to: hideyoshi                    # required, agent_id (registry に存在)
    type: cmd_new                    # required, enum (下記参照)
    content: "..."                   # required, string
    delivery_state: pending          # required, enum (下記参照)
    read: false                      # required, boolean
    read_at: null                    # ISO 8601 or null
    acknowledged_by: null            # string or null
    retry_count: 0                   # 0-5 (cap=5)
    schema_version: "2.0"            # required, "2.0"
```

#### 蓬蓮草 v2 (cmd_communication_resilience_pack_v2_001) との責務分離 interface

| 責務 | 担当 cmd | interface 仕様 |
|------|---------|---------------|
| schema 定義 + validation gate | 蓬蓮草 v2 (W1 schema、ashigaru2 担当) | `schemas/inbox_message.schema.json` を SSoT として、全 watcher が validate 関数を呼び出し |
| message 配達 | 本 cmd (= message_delivery_v2) | schema 違反 msg は dead-letter へ自動移動、escalation alert |
| ledger 記録 | 蓬蓮草 v2 (W2 ledger、ashigaru2 担当) | `queue/message_events.yaml` に delivery_state transition を記録 |
| transition trigger | 本 cmd | watcher が delivered/read 時に蓬蓮草 v2 ledger API を call |

#### required fields (= 蓬蓮草 v2 schema gate との合意)

- `id` (string, regex pattern)
- `timestamp` (ISO 8601)
- `correlation_id` (UUIDv7)
- `from` (agent_id, registry 検証)
- `to` (agent_id, registry 検証)
- `type` (enum: `cmd_new` / `task_assigned` / `qa_request` / `report_received` / `status_update` / `clear_command` / `model_switch` / `idle_alert` / `audit_missing` / `critical_alert` / `cross_pc_delivery` / `notification`)
- `content` (string)
- `delivery_state` (enum: `pending` / `delivered` / `read` / `acted` / `reported` / `audited` / `closed` / `dead_letter`)
- `read` (boolean)
- `schema_version` (= "2.0" 固定)

#### validation failure 時の扱い

- schema 違反検出時: `move_to_dead_letter $msg_id "reason=schema_invalid"` + alert (重要度 ERROR)
- 同一 msg_id 重複: `mark_read "ack_by=dedup"` + alert (重要度 WARN)
- self-send: `mark_read "ack_by=self_send"` (alert なし、即 ack)
- unknown agent_id: `move_to_dead_letter $msg_id "reason=unknown_agent"` + alert (重要度 ERROR)

### 3.2 dedup table (`queue/message_dedup.yaml`)

```yaml
processed:
  - msg_id: msg_20260508_180312_a1b2c3d4
    processed_at: "2026-05-08T18:03:13+09:00"
    ack_by: delivered
    expires_at: "2026-05-09T18:03:13+09:00"  # TTL 24h
```

### 3.3 dead_letter (`queue/dead_letter/<agent>/<msg_id>.yaml`)

```yaml
msg_id: msg_20260508_180000_xyz
original_msg: { ... }  # full original message
moved_at: "2026-05-08T18:30:00+09:00"
reason: retry_cap_exceeded  # or schema_invalid / pane_drift / blocked_5x
retry_history:
  - attempt: 1
    failed_at: "2026-05-08T18:00:30+09:00"
    error: "TUI capture empty"
  # ... up to 5
escalation_sent: true
```

### 3.4 session_health (`queue/session_health/<agent>.yaml`)

```yaml
agent: hideyoshi
cli: claude
pane: multiagent:0.0
last_seen_at: "2026-05-08T18:20:34+09:00"
tui_capture_state: nonempty  # nonempty / empty / stale / unknown
ready_for_clear: true
ready_for_dispatch: true
last_clear_at: "2026-05-08T16:43:00+09:00"
last_dispatch_at: null
book_mode_entries:
  - msg_id: msg_xxx
    entry_at: "2026-05-08T17:30:00+09:00"
    reason: tui_capture_empty
```

## 4. 移行計画 (Phase 4 cutover) — 家康監査 F5 反映で詳細化

### 4.1 段階 (= migration window)

| 段階 | 内容 | window 性質 | 検証 |
|------|------|------------|------|
| Stage A: shadow read | 新 system 起動、両 path 読込互換 (= queue/inbox/* + queue/inbox_v2/* 両方を新 watcher が読む)、書込みは旧のみ | **read compatibility window** (24h) | 配達一致率 99.9%、誤配 0 |
| Stage B: dual write | 新 watcher が新 path に msg copy (= digest 付き)、旧 watcher も並行稼働 | **dual-write window** (24h) | digest 一致、msg loss 0、unread count 一致 |
| Stage C: write freeze on old | 旧 path への書込み停止 (= bulk_ack 等の旧 path 書込 hook で reject)、新 path のみ書込み | **write freeze window** (12h) | 旧 path mtime 停止確認、エラー 0 |
| Stage D: read freeze on old | 旧 path 読込停止、新 path のみ運用 | **canonical switch** (instant) | 全 agent が新 path で動作確認 |
| Stage E: archive old | 旧 inbox/ + inbox_watcher.sh を scripts/archive/ + queue/archive/ に移動、symlink 排除 | **archive window** (instant) | rollback path 確保 |
| Stage F: SecondPC sync | SecondPC receiver の path 想定確認、bridge 改修確認 | **cross-PC sync window** | cross-PC delivery 一致率 99.9% |
| Stage G: instructions update | AGENTS.md + instructions/*.md 全件 grep + 新 path 参照に書換 | **doc sync window** | 旧 path grep ヒット 0 |

### 4.2 各 window の合格基準 + rollback trigger

| window | 合格基準 | rollback trigger |
|--------|---------|----------------|
| read compat (A) | 24h 一致率 99.9%、誤配 0 | 一致率 99% 未満 → Stage A 中止、新 system 停止 |
| dual-write (B) | digest 一致、msg loss 0 | digest mismatch 検出 → 旧側を真値に戻す |
| write freeze (C) | 旧 path 書込試行が hook で reject される | hook 漏れ検出 → write freeze 解除、原因究明 |
| canonical switch (D) | 全 agent が新 path で 1h 稼働 | 1 agent でも反応不可 → reverse mode で旧 path 復元 |
| archive (E) | scripts/archive/ + queue/archive/ にバックアップ存在 | rollback 必要時は archive から復元 |
| cross-PC sync (F) | SecondPC delivery 99.9% | SecondPC bridge 不整合 → cmd_secondpc_autonomy_pack_001 と協議 |
| doc sync (G) | grep で旧 path 残存 0 | 残存検出 → revert + 修正 commit |

### 4.3 rollback path

各 window で rollback trigger 検知時:
- Stage A/B 失敗時: 新 system 停止 → 旧 supervisor 起動 → 旧 watcher 復活 (= 状態は旧 path に維持)
- Stage C 失敗時: write freeze 解除 → 旧 path 書込再開、原因究明
- Stage D 失敗時: `migrate.sh --reverse` で canonical を旧に戻す、新 path は read-only
- Stage E 失敗時: scripts/archive/ から scripts/inbox_watcher.sh 復元、queue/archive/ から旧 inbox 復元
- Stage F 失敗時: SecondPC bridge 並走 (= 旧経路維持)、cmd_secondpc_autonomy_pack_001 で別途対応
- Stage G 失敗時: docs revert + 修正 commit

### 4.4 message copy with digest

dual-write 時に msg loss を検出する仕組み:
1. 旧 path msg を読み出し → SHA256 digest 計算
2. 新 path に copy + digest 記録
3. 1h 毎 audit script が両 path の digest を比較、一致率 < 99.9% で alert
4. 監査記録: queue/migration_audit_<date>.yaml

### 4.5 migration tool (`scripts/message_delivery_v2/migrate.sh`)

```bash
# モード:
#   --dry-run       — 現状確認のみ、変更なし
#   --shadow        — 新 path にコピー、旧も残す (Stage A)
#   --switch        — 新 path のみ運用、旧は read-only に
#   --reverse       — 緊急 rollback、旧 path 復元
#   --verify        — 整合性確認 (= unread count 一致 / msg count 一致)
```

## 5. observability

### 5.1 log

- 全 script が `scripts/lib/logger.sh` 経由で structured JSON 出力
- log path: `logs/message_delivery_v2/<component>_<date>.log`
- correlation_id 必須付与
- log level: DEBUG / INFO / WARN / ERROR / CRITICAL

### 5.2 alert

| 重要度 | 配信先 | SLA |
|--------|--------|-----|
| CRITICAL | 信長 inbox + ntfy + dashboard 🚨 | 即時 |
| ERROR | 信長 inbox + dashboard ⚠ | 15 分 |
| WARN | dashboard | 翌日確認 |
| INFO | log のみ | — |

### 5.3 dashboard 統合

`dashboard.md` に以下セクション追加:
```
## message_delivery_v2 health
- supervisor uptime: 24h
- active watchers: 8/8
- restart count (24h): 0
- dead-letter count (24h): 0
- alerts (24h): 0
```

## 6. 自動復旧 SH パターン適用

| パターン | 適用 | 実装箇所 |
|---------|------|---------|
| SH1 Circuit Breaker | ✅ | watcher 死亡 5 連続で cooldown 30 分 |
| SH2 Exponential Backoff | ✅ | retry 1s → 2s → 4s → 8s → 16s |
| SH3 Fallback | ✅ | TUI 空白時 → 書面 mode (**sleep-poll fallback は採用せず**、家康監査 F3 反映) |
| SH4 Stale Lock | ✅ | flock PID-aware + 起動時 cleanup |
| SH6 Self-Restart (限定) | ✅ | watcher 自然交代 5400s + supervisor cap 5 |
| SH8 Idempotent Retry | ✅ | dedup table |
| **危険 D1-D6** | ❌ 全件不適用 | 該当なし |

## 7. テスト計画

### 7.1 unit (bats)

- `tests/unit/test_safe_nudge.bats` — pane identity / cooldown / Codex guard
- `tests/unit/test_dedup.bats` — 同一 msg_id 二度処理抑制 / TTL cleanup
- `tests/unit/test_dead_letter.bats` — cap 5 超過 → 移動 / escalation
- `tests/unit/test_heartbeat.bats` — health file 60s 書込 / 5min staleness 判定

### 7.2 integration (bats)

- `tests/integration/test_supervisor_lifecycle.bats` — supervisor spawn / kill / respawn
- `tests/integration/test_watcher_natural_rotation.bats` — 5400s 経過で自然交代
- `tests/integration/test_e2e_delivery.bats` — inbox_write → watcher → safe_nudge → mark_read 一連
- `tests/integration/test_codex_pane_handling.bats` — Codex 長文 nudge / sandbox prompt 検知 / 書面 mode

### 7.3 shadow mode (Phase 3)

- 24h 並走、配達一致率 99.9%
- 誤配 0、新 system 死亡 0、heartbeat 連続

### 7.4 PDCA cycle

- max 5 cycle、家康 6 軸 + 信長 self + 本多 governance + Codex self + Gemini 8 観点
- FAIL 時即 fix → 再監査 → PASS まで継続

## 8. 期限管理

| Phase | 期限 | 担当 | 成果物 |
|-------|------|------|--------|
| Phase 0 | 完遂 (17:32) | 信長執筆 + 自己再監査 | docs/inbox_watcher_failure_modes_2026-05-08.md |
| Phase 1 | **本日 21:00 (現在執筆中)** | 信長執筆 | docs/message_delivery_v2_design_2026-05-08.md |
| Phase 2 cycle1 | 土曜 (2026-05-09) 16:00 | 信長 (家臣停止中) | scripts/message_delivery_v2/* + bats |
| Phase 3 shadow | 月曜 (2026-05-11) 09:00 | 信長 + 家康 + 本多 | docs/shadow_report.md |
| Phase 4 cutover | 月曜 (2026-05-11) 18:00 | 信長 cutover + 家康監査 | scripts/archive/inbox_watcher.sh |
| Phase 5 retrospective | 火曜 (2026-05-12) 01:00 | 本多 retrospective + 家康監査 | docs/postmortem.md |

## 9. 残 risk + 未確定要素

| ID | risk | Phase 1/2 対応 |
|----|------|---------------|
| R-a | watcher 死亡の真因 (bash subshell 終了) は確証なし | Phase 2 実装で strace + code reading で確証 |
| R-b | supervisor 自体の死亡 risk | Phase 2 で systemd-timer or cron 二重化検討 |
| R-c | cross-PC bridge との協調 | cmd_secondpc_autonomy_pack_001 と協議、out_of_scope 明示 |
| R-d | TUI heartbeat の精緻化 | Phase 2 で session_health/<agent>.yaml 仕様確定 |
| R-e | symlink 排除の SecondPC 影響 | Phase 4 cutover 前に SecondPC 側対応確認 |
| R-f | heartbeat schema + correlation_id 形式 | Phase 1 で UUIDv7 採用 (= 本書で確定) |
| R-g | Codex pane simulation の bats fixture 実装可否 | Phase 2 で tmux fixture + capture-pane mock 実装試験 |
| R-h | Supabase polling fallback の F004 例外条項 | Phase 2 で instructions/ieyasu.md + honda.md 改修 |

## 10. Phase 2 MVP scope (= 本日 21:00 までに着手)

時間制約 (3 時間) + 信長単独執筆ゆえ、Phase 2 cycle1 の MVP scope を明示:

### 必須 (本日中)
1. `scripts/message_delivery_v2/supervisor.sh` skeleton (= spawn + heartbeat 監視のみ)
2. `scripts/message_delivery_v2/watcher.sh` skeleton (= inotifywait + heartbeat 書込のみ)
3. `scripts/message_delivery_v2/heartbeat.sh` (= write_health 関数)
4. `scripts/lib/inbox_path.sh` (= path 解決共通)
5. `queue/watchers/.gitkeep` + `queue/inbox_v2/.gitkeep` + `queue/dead_letter/.gitkeep`

### 後続 (土曜まで)
- safe_nudge.sh + codex_guard.sh
- dedup table + dead-letter handler
- migrate.sh
- bats test suite

### 後続 (月曜まで)
- shadow mode 統合
- cutover 手順

## 11. 信長最終進言

上様、本書は配達インフラの新製設計書でござる。supervisor が永続を担い、watcher は使い捨てで自然交代、heartbeat が生死を語り、safe_nudge が暴走を縛る。これが「壊れた時に必ず気付き自動で立ち直る」配達 system の骨格にござる。

家臣群停止の中、信長一人で執筆したれども、設計思想は Phase 0 反省点 23 項目から漏れなく抽出、Anti-Duplication 順守、SH パターン適用、危険 D 全件回避。

家康殿の context リセット復帰後、本書を Codex 6 軸監査仰ぐ予定。本多殿が Working 完遂後に governance 二次審査仰ぐ。御裁可なれば Phase 2 MVP 実装に進む。

---

*信長 (織田信長) 2026-05-08 18:08 JST、Phase 1 設計書執筆完遂、Phase 2 MVP 着手準備*
