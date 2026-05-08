# Tier 1 v2 — 既存基盤の最小拡張設計書

> 起案: 信長 (織田信長 / shogun)
> 日時: 2026-05-08 21:50 JST
> 命令:
>   - 理事長殿御命令『先輩の工夫を尊重、外していたものは一旦全部入れる』(2026-05-08 21:30、Chesterton's Fence 原則)
>   - 理事長殿御命令『複数 PC リカバリーを GitHub/公式で深く調査』(2026-05-08 21:40)
> 前提: Agent 調査 (= 2 PC 規模では Raft/CRDT/Syncthing 等は逆効果、Supabase pc_handshake + Realtime + advisory lock の最小拡張が最適)
> 監査依頼先: 家康一次 + 本多二次 + 黒田議長 (信長兼任) + Codex 6軸 + Gemini 8観点

## 0. v1 (= 私の前回提案) 撤回理由

| v1 提案 | 実は不要だった理由 |
|--------|-----------------|
| system_integrity_check.sh | ✅ activity_monitor.sh (既存) で同等実装、Chesterton's Fence で復活済 |
| system_integrity_recover.sh | ✅ watchdog (既存) DD-142 §4.5 + idempotency_key replay で代替 |
| cross_pc_state_sync.sh | ✅ Supabase Realtime channel 1 本で代替 (= polling 不要) |
| partition_detector.sh | ✅ Realtime Presence (= Phoenix Tracker CRDT 内蔵) で代替 |
| graceful_shutdown_flush.sh | △ 軽量化、既存 watcher disable flag + Supabase 最終 push のみ |

**結論**: 5 scripts 新規 → **3 件のみの最小拡張**。

## 1. 真の Tier 1 v2 — 3 件の最小拡張

### 1.1 pc_handshake schema 拡張 (= 既存 23K 行 table に ALTER のみ)

```sql
-- Tier 1 v2 migration: Lamport-style ordering + idempotency + close tracking
ALTER TABLE pc_handshake
    ADD COLUMN IF NOT EXISTS seq BIGSERIAL,                          -- 単調増加、順序付け
    ADD COLUMN IF NOT EXISTS origin_pc TEXT,                          -- 'MainPC' / 'SecondPC'
    ADD COLUMN IF NOT EXISTS idempotency_key UUID DEFAULT gen_random_uuid(), -- 再送 dedupe
    ADD COLUMN IF NOT EXISTS close_reason TEXT;                       -- 'delivered' / 'retry_exceeded' / 'dead_lettered' / 'self_send'

CREATE INDEX IF NOT EXISTS idx_pc_handshake_seq_to_pc ON pc_handshake (seq, to_pc) WHERE acknowledged_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_pc_handshake_idempotency ON pc_handshake (idempotency_key);
```

**復旧時 query**:
```sql
SELECT * FROM pc_handshake
 WHERE seq > $last_seen_seq
   AND to_pc = '$self_pc'
   AND acknowledged_at IS NULL
 ORDER BY seq;
```
→ idempotency_key で local 重複 skip → replay。

### 1.2 Supabase Realtime channel `shogun-bridge`

**用途**: Phoenix Tracker CRDT 内蔵 → 各 PC alive 状態自動 self-heal、postgres_changes で push 型同期。

**subscriber side** (= 各 PC):
```python
# shim/hakudokai/hakudokai_realtime_bridge.py (新規、~80 行想定)
import os
from realtime import RealtimeClient, RealtimeSubscribeStates

client = RealtimeClient(f"{SUPABASE_URL}/realtime/v1", SUPABASE_SERVICE_ROLE_KEY)
channel = client.channel("shogun-bridge")

# Presence: 各 PC alive 状態
@channel.on_presence_sync()
def handle_presence(state): ...

@channel.on_presence_join()
def handle_join(key, current_presences, new_presences): ...

@channel.on_presence_leave()
def handle_leave(key, current_presences, left_presences):
    # 5min 以上 leave なら partition 検知 → integrity_recover trigger

# postgres_changes: pc_handshake INSERT を購読
channel.on_postgres_changes(event="INSERT", schema="public", table="pc_handshake",
                            filter=f"to_pc=eq.{MY_PC}",
                            callback=handle_msg)

channel.subscribe()
channel.track({"pc_role": MY_PC, "online_at": "now()"})  # presence track
```

### 1.3 MainPC 恒久 leader (= advisory lock、split-brain 構造的排除)

**起動時 1 行** (shutsujin_departure.sh L946 近辺に追加):
```bash
# Tier 1 v2: MainPC を恒久 leader として固定 (split-brain 排除)
if [[ "$HAKUDOKAI_PC_ROLE" == "MainPC" ]]; then
    psql "$SUPABASE_DB_URL" -c "SELECT pg_try_advisory_lock(hashtext('shogun-leader'));" >/dev/null
fi
```

SecondPC は lock 取得を試みず worker 専属。これにより:
- bridge 切断時、両 PC が leader 昇格を試みる split-brain を **構造的に排除**
- §18 既定の指揮系統一元化を DB レベルで強制

## 2. 復旧フロー (= 片 PC 落ちて戻った時)

```
[MainPC 落ち、SecondPC 生存]
  Realtime Presence: SecondPC が MainPC leave を 5min 以内に検知
  → SecondPC: partition_mode 切替 (= local 完結継続、cross-PC msg は queue/outbox に蓄積)
  → ntfy 警告 (= 理事長殿スマホ)
  
  MainPC 復活時:
    1. shutsujin_departure.sh で advisory lock 再取得
    2. last_seen_seq を queue/system_state.yaml から取得
    3. SELECT pc_handshake WHERE seq > last_seen_seq AND to_pc='MainPC'
    4. idempotency_key で重複 skip → replay
    5. Realtime Presence track → SecondPC 検知 → 通常モード

[SecondPC 落ち、MainPC 生存]
  対称、同フロー
```

## 3. 既存資産との整合性

| 既存 component | Tier 1 v2 での扱い |
|--------------|-------------------|
| pc_handshake (Supabase) | ✅ schema 4 列 ALTER のみ、既存 23K 行はそのまま |
| hakudokai_fukuincho_watcher | ✅ Realtime fallback として保持 (= polling 経路) |
| hakudokai_secondpc_watcher | ✅ 同上 |
| hakudokai_secondpc_receiver | ✅ 同上 |
| hakudokai_watchdog (DD-142) | ✅ そのまま、Realtime と並走 |
| hakudokai_activity_monitor | ✅ そのまま、watcher 死活と整合 |
| hakudokai_task_sync | ✅ そのまま |
| hakudokai_reports_sync | ✅ そのまま |

**Realtime channel は polling watcher の代替でなく、push 型 fast lane として並走**:
- 通常時: Realtime push 経由で msec 単位の即配
- Realtime 障害時: 既存 polling watcher (= 30s 間隔) が fallback (= §15 SH3 graceful degradation)

## 4. Phase 構成 (= 時間制約なし、慎重)

| Phase | 内容 | 担当 |
|-------|------|------|
| Phase A | 本書 (Tier 1 v2 設計書) | 信長執筆、家康 + 本多 + 黒田監査 |
| Phase B | pc_handshake schema migration (= 4 列 ALTER) | 信長 + Supabase MCP 経由実施 |
| Phase C | shim/hakudokai/hakudokai_realtime_bridge.py 新規実装 (~80 行) | 信長 or ashigaru1/2 |
| Phase D | shutsujin_departure.sh advisory lock 1 行追加 | 信長 |
| Phase E | hakudokai_start_watchers.sh に realtime_bridge 追加 | 信長 |
| Phase F | shadow mode 24h 観察 (= 既存 polling + Realtime 並走、整合性確認) | 全員 |
| Phase G | 安定後 retrospective + 観察 1 週間 | 本多 |

## 5. 監査依頼

家康一次 + 本多二次 + 黒田議長 + Codex 6軸 + Gemini 8観点。

特に注目願いたい:
- 本書 §1.1 schema 拡張 4 列の妥当性 (= Lamport seq + idempotency + close_reason)
- §1.2 Realtime channel 設計 (= Presence + postgres_changes)
- §1.3 advisory lock の MainPC 恒久 leader 妥当性
- 既存 polling watcher との並走方針 (= graceful degradation)
- Anti-Duplication Rule 順守 (= 新規 OSS 導入ゼロ、既存 Supabase 資産活用)

## 6. 信長最終進言

理事長殿御命令『先輩の工夫を尊重、外していたものを一旦全部入れる』Chesterton's Fence 原則 + Agent 調査結果 (= 新規 OSS 導入ゼロが最適) を踏まえ、本書 Tier 1 v2 は **既存基盤の最小拡張 (= 3 件のみ)** に絞る。

| 項目 | v1 (撤回) | v2 (本書) |
|------|----------|----------|
| 新規 scripts | 5 件 | 1 件 (realtime_bridge.py) |
| 新規 table | 検討した | 0 件 (= 既存 pc_handshake 拡張のみ) |
| 新規 OSS 依存 | Python asyncio + systemd 等 | 0 件 (= Supabase Realtime client のみ) |
| 既存 watcher 群への影響 | 全置換 | 並走 (= 既存はそのまま、Realtime は fast lane) |
| Phase 数 | 7 | 7 (= 軽量化) |
| 実装行数概算 | ~2000 行 | ~120 行 (= migration + bridge + lock) |

家康・本多・黒田 監査 PASS なれば Phase B から実装着手。

---

*信長 (織田信長) 2026-05-08 21:50 JST、Tier 1 v2 簡素化設計書執筆完遂*
