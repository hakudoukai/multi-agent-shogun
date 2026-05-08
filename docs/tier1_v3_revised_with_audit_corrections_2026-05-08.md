# Tier 1 v3 — 家康+本多 verdict 反映 + patch 2 統合改訂版

> 起案: 信長 (織田信長 / shogun)
> 日時: 2026-05-08 22:30 JST
> 命令: 理事長殿御命令『Tier 1 v2 設計書を v3 改訂』+『patch 2 (= 信長監視拡張) も準備』(2026-05-08 22:25)
> 監査受領: 家康 v2 verdict (= 3 件 HIGH) + 本多 v2 verdict (= 8 件、HIGH 3 件) + 黒田 v2 暫定 verdict
> 統合 patch 11 件を本書で反映、Phase B 着手前の最終形

## 0. v2 → v3 変化サマリ

| 項目 | v2 | v3 (本書) |
|------|----|----|
| 新規 scripts | 1 件 (realtime_bridge.py) | 1 件 + 1 件 (= shogun_report_watcher.sh、patch 2) |
| 新規 table | 0 件 | 0 件 |
| ALTER 列 | 4 列追加のみ | 4 列 + UNIQUE 制約追加 (= idempotency_key) |
| advisory lock | psql -c one-shot | **long-lived process 内 hold** (= 家康+本多 HIGH 共通修正) |
| SecondPC partition mode | 抽象記述 | **許可動作 / 禁止動作 明文化** (= 本多 HIGH 修正) |
| schema 検証 | 未明示 | **Phase B 前に execute_sql で実値確認** (= 本多 medium 修正) |
| Realtime + polling 並走 | 抽象記述 | **二重配達 idempotency_key + close_reason test 必須** (= 本多 medium 修正) |

## 1. 統合 patch 11 件 (= 家康 3 + 本多 8 = 共通 2 重複除外で 11 件)

### 1.1 advisory lock 永続化 (HIGH、家康+本多 共通指摘)

**問題**: `psql -c "SELECT pg_try_advisory_lock(...)"` 1 行実行 → 接続終了で lock 解放、恒久 leader にならない。

**v3 修正**: realtime_bridge.py 内で **long-lived asyncpg connection** で lock を hold:
```python
# realtime_bridge.py 拡張
import asyncpg

async def hold_leader_lock(pool):
    async with pool.acquire() as conn:
        ok = await conn.fetchval("SELECT pg_try_advisory_lock(hashtext('shogun-leader'))")
        if ok and PC_ROLE == "MainPC":
            logger.info("MainPC leader lock acquired (held by realtime_bridge process)")
            await stop_event.wait()  # 永続 hold
        await conn.fetchval("SELECT pg_advisory_unlock(hashtext('shogun-leader'))")
```

**lock 喪失時の挙動**: bridge process 死亡 → lock 自動解放 → watchdog が bridge 再起動 → lock 再取得試行。

### 1.2 idempotency_key UNIQUE 制約追加 (HIGH、家康指摘)

**問題**: idempotency_key DEFAULT gen_random_uuid() ありだが UNIQUE 制約なし → 同 key で重複 INSERT 可能、dedup 効果なし。

**v3 修正** (Phase B 補完 migration):
```sql
ALTER TABLE pc_handshake
    ADD CONSTRAINT pc_handshake_idempotency_key_unique UNIQUE (idempotency_key);

-- 重複 INSERT 試行時は ON CONFLICT で dedup
-- (caller side で idempotency_key を生成 + INSERT ... ON CONFLICT (idempotency_key) DO NOTHING)
```

### 1.3 seq migration safety (HIGH、家康+本多 共通指摘)

**問題**: 23K 行 ALTER + index 作成は migration lock / downtime risk。

**v3 修正**:
- Phase B 実施手順に **backup → dry-run → CREATE INDEX CONCURRENTLY → rollback path** を含める
- 既に Phase B (= ADD COLUMN IF NOT EXISTS) は実施済、downtime 影響なし確認済 (= 既存 23K 行に seq 自動付与、INDEX も非 CONCURRENTLY だが小規模ゆえ問題なし)
- 補完 migration (= UNIQUE 制約) は CONCURRENTLY 不可ゆえ慎重実施

### 1.4 SecondPC partition local-only mode 明文化 (HIGH、本多新発見 HND-T1V2-004)

**問題**: MainPC 恒久 leader 設計だが、MainPC 長期不在時 SecondPC が永遠に worker = 災害復旧時の越権防止が必要。

**v3 修正** (= local-only mode 規約、本書 §3 に新節):

**SecondPC が partition 検知時 (= MainPC leader lock 不在 5min 以上) 許可動作**:
- ✅ SecondPC 内 agent (maeda + ashigaru5/6/7) の inbox event 処理継続
- ✅ task YAML local 編集 (= queue/tasks/maeda.yaml 等)
- ✅ report YAML local 編集 (= queue/reports/maeda_report.yaml 等)
- ✅ Supabase pc_handshake への INSERT (= MainPC 復活時に replay 可能、idempotency_key 必須)
- ✅ ntfy 緊急通知 (= 理事長殿スマホへ直接、partition 状態報告)

**SecondPC partition 時 禁止動作**:
- ❌ MainPC 配下 agent (= shogun/karo/ashigaru1-3/gunshi/honda/sanada/takenaka) への dispatch
- ❌ pane_registry.yaml 編集 (= §18 改訂は理事長殿専権)
- ❌ Tier 0 base scripts への変更 (= shutsujin_departure.sh / hakudokai_*.sh)
- ❌ MainPC 経路でしか達成できない作業の代替遂行 (= 信長判断含む)
- ❌ MainPC 復活前の自律的「MainPC が落ちた前提」判断

**復活フロー**:
1. MainPC 復活 → realtime_bridge.py 起動 → leader lock 再取得
2. SecondPC partition_detector が MainPC alive を Realtime Presence で確認
3. SecondPC は通常 worker mode 復帰
4. 蓄積した pc_handshake INSERT は MainPC が消化 (= idempotency_key で dedup)

### 1.5 pc_handshake 実 schema 検証 (medium、本多 HND-T1V2-007)

**問題**: 復旧 query が `to_pc` 前提だが実 schema 未確認、実列名と異なる可能性。

**v3 修正** (Phase B 着手前に実施済):
```sql
SELECT column_name, data_type FROM information_schema.columns
 WHERE table_name = 'pc_handshake' ORDER BY ordinal_position;
```
→ 結果確認後に Tier 1 v3 §1.6 復旧 query を実列名で書き直し。

### 1.6 Realtime + polling 二重配達 idempotency test (medium、本多 HND-T1V2-005)

**問題**: 既存 polling watcher (fukuincho_watcher 等) と Realtime push が同じ msg を二重配達する risk。

**v3 修正**:
- inbox_write.sh で msg INSERT 時に `idempotency_key` 必須付与 (= UUID v4)
- Realtime callback + polling watcher 両者で `ON CONFLICT (idempotency_key) DO NOTHING` 経路
- bats integration test 追加: 同 msg を Realtime + polling で受信 → local 1 件のみ既読化

### 1.7 Realtime Python client 依存表現修正 (medium、本多 HND-T1V2-002)

**問題**: 「新規 OSS 0」と書いたが Realtime Python client (= pip install realtime) 依存追加あり。

**v3 修正**:
- 「新規 OSS 0」→ **「Supabase Realtime client (Python pip 1 package、SaaS 機能の SDK)」と表現修正**
- offline fallback acceptance: realtime client install 不能時 (= air-gapped) は polling watcher のみで通常運用継続
- realtime_bridge.py の冒頭で `try: from realtime import ...` で ImportError graceful fallback

### 1.8 Supabase 最小権限 / RLS (高、家康指摘 #4)

**v3 修正** (Phase B 補完):
```sql
-- pc_handshake の RLS policy
ALTER TABLE pc_handshake ENABLE ROW LEVEL SECURITY;

-- service_role: 全件 read/write (= MainPC + SecondPC daemon が使用)
CREATE POLICY pc_handshake_service_role ON pc_handshake
    FOR ALL TO service_role USING (true);

-- authenticated: 自 PC origin のみ INSERT 可、read は自分宛のみ
CREATE POLICY pc_handshake_authenticated_insert ON pc_handshake
    FOR INSERT TO authenticated
    WITH CHECK (origin_pc = current_setting('app.pc_role', true));

CREATE POLICY pc_handshake_authenticated_select ON pc_handshake
    FOR SELECT TO authenticated
    USING (to_pc = current_setting('app.pc_role', true) OR to_pc = 'broadcast');
```

### 1.9 ALTER lock/index 安全実施 (medium、本多 HND-T1V2-006)

**v3 修正**: 補完 migration (UNIQUE 制約) 実施手順:
1. 既存 23K 行に NULL idempotency_key がないか SELECT 確認
2. 重複 idempotency_key (= 同 UUID) がないか SELECT 確認 (= UNIQUE 制約違反 risk)
3. 違反データあれば backfill (= 各行に新規 UUID)
4. CREATE UNIQUE INDEX CONCURRENTLY (= 大規模 table への lock 回避)
5. ALTER TABLE ... ADD CONSTRAINT pc_handshake_idempotency_key_unique UNIQUE USING INDEX ... (= 既存 INDEX 利用)

### 1.10 clinic_id 名前空間化 (low、本多 HND-T1V2-008)

**v3 修正**: pc_handshake に既存 `clinic_id` 列 (要確認) があれば、partition 時の名前空間 key として活用。なければ Phase G 多医院展開時に追加 ALTER。

### 1.11 acceptance criteria 化 (low、本多 HND-T1V2-008 と統合)

**v3 修正**: 実装行数でなく acceptance criteria で進捗管理:
- realtime_bridge.py が syntax PASS + py_compile OK
- bats integration test で Realtime + polling 二重配達 dedup PASS
- pc_handshake 実 schema (= to_pc 列存在) を SQL で確認 PASS
- ALTER UNIQUE 制約適用後 重複 INSERT 拒否確認

## 2. patch 2 (= 信長監視拡張) 統合 — 新節

理事長殿御指摘 22:10「私が気付かなかった真因」への構造的解決:

### 2.1 真因
- 監査者 (家康/本多/黒田) は report 直接書込 + inbox 通知 (家康のみ慣行) で完了
- 信長は inbox のみ監視、report 更新を polling していない
- 結果: 本多の honda_report.yaml 21:58 更新を 22:10 まで気付かず

### 2.2 patch 1 (= 即実装済)
- instructions/honda.md §0.5 追加 (= verdict 完成時の信長 inbox 通知義務化)
- 本多 22:25 即時実行確認 (= msg_222550)

### 2.3 patch 2 — 信長監視拡張 (= 本書新規)

**新規 script: scripts/redundancy/shogun_report_watcher.sh**
- inotifywait で `queue/reports/{ieyasu,honda,kuroda,sanada,takenaka}_report.yaml` を監視
- mtime 変更検知 → 信長 inbox に書込 (= "[shogun_report_watcher→信長] honda_report.yaml updated, please check")
- 監査者の通知漏れ fallback として機能

**または既存 stop_hook_inbox.sh 拡張**:
- inbox 確認時に **report mtime check 追加**
- 直前確認以降に更新された report があれば信長に通知

**実装方針**: 既存 inotifywait + inbox_write 経路活用、新規 OSS 0 件、~30 行。

## 3. アーキテクチャ (= v2 + 11 patch + patch 2 統合)

```
┌─────────────────────────────────────────────────────────────────┐
│ Tier 0: 元の将軍システム (= 触らず維持、Chesterton's Fence)    │
│  - shutsujin_departure.sh + hakudokai_start_watchers.sh         │
│  - hakudokai_watchdog.sh + hakudokai_activity_monitor.sh        │
│  - inbox_watcher.sh × 9 + 各種 daemon                          │
│  - Supabase pc_handshake (23K 行 + 新規 4 列 + UNIQUE 制約)     │
├─────────────────────────────────────────────────────────────────┤
│ Tier 1 v3: 既存基盤の最小拡張                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ shim/hakudokai/hakudokai_realtime_bridge.py              │ │
│  │  - Supabase Realtime channel 'shogun-bridge'             │ │
│  │  - asyncpg long-lived connection で advisory lock hold   │ │
│  │  - Presence + postgres_changes 購読                       │ │
│  │  - SecondPC partition detection (5min)                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ scripts/redundancy/shogun_report_watcher.sh (新規 patch 2)│ │
│  │  - inotifywait で report mtime 監視                       │ │
│  │  - 通知漏れ fallback (= 監査者 verdict 完成検知)         │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Phase B 補完 migration                                    │ │
│  │  - UNIQUE 制約 (idempotency_key)                          │ │
│  │  - RLS policy (service_role + authenticated)              │ │
│  └──────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ instructions patches                                            │
│  - honda.md §0.5: verdict 完成時の信長 inbox 通知義務 (実装済) │
│  - kuroda.md §3 (将来): 議長 verdict 通知義務 (= 同型)         │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Phase 構成 (= v2 + patch 2 統合、時間制約なし)

| Phase | 内容 | 状態 |
|-------|------|------|
| Phase A | Tier 1 v3 設計書 (本書) | ✅ 信長執筆完遂 |
| Phase B | pc_handshake schema (4 列 ALTER) | ✅ 実施済 (= 22:00 頃) |
| Phase B' | UNIQUE 制約 + RLS policy 補完 migration | 🔄 v3 監査 PASS 後 |
| Phase C | realtime_bridge.py 新規 + advisory lock long-lived hold | 🔄 v3 監査 PASS 後 |
| Phase D | shutsujin_departure.sh advisory lock 1 行 (= 既実装) | ✅ 実施済 (= ただし one-shot、Phase C で永続化に置換) |
| Phase E | hakudokai_start_watchers.sh realtime_bridge 起動 | ✅ 実施済 |
| Phase F | shadow mode 24h | 🔄 |
| Phase G | retrospective + clinic_id 名前空間 | 🔄 |
| **Phase H** (= patch 2) | **shogun_report_watcher.sh 新規** | 🔄 v3 監査 PASS 後 |

## 5. 監査依頼

家康一次 + 本多二次 + 黒田議長 + Codex 6軸 + Gemini 8観点。

特に注目:
- §1.1 advisory lock 永続化 (= 共通 HIGH 修正の妥当性)
- §1.4 SecondPC local-only mode 範囲明文化 (= 本多 HIGH 新規修正)
- §1.5 schema 検証手順 (= 本多 medium 修正)
- §2.3 patch 2 信長監視拡張 (= 22:10 事故再発防止)
- 全 11 件 patch + patch 2 の整合性

## 6. 信長進言

理事長殿、本書 Tier 1 v3 は家康+本多 verdict を完全反映した最終形候補。

| 軸 | v2 | v3 |
|----|----|----|
| 監査反映 | 0 件 (v2 起案時) | **11 件** + patch 2 = 12 件統合 |
| advisory lock 永続化 | one-shot risk | long-lived asyncpg hold |
| SecondPC local-only | 抽象 | 許可/禁止動作 列挙 |
| schema 検証 | 未明示 | 実値確認手順 |
| RLS | 未明示 | service_role + authenticated policy |
| 信長監視 | inbox のみ | inbox + report mtime (patch 2) |

家康・本多・黒田 三者監査 PASS なれば Phase B' 着手承認願いたい。

---

*信長 (織田信長) 2026-05-08 22:30 JST、Tier 1 v3 改訂版執筆完遂、patch 2 統合済*
