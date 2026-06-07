# fukuincho 段階3 GAP-2 根治設計 — Supabase pc_handshake → 検知層 入力 bridge 設計章節

> 起草: 軍師 (gunshi-third) / task: subtask_thirdpc_p1_fukuincho_stage3_gap2_supabase_jsonl_bridge_design_001
> 副院長令 0a69041f P0 cascade (GAP-2 根治設計 task 3e4046cf) / 理事長令: 「とりあえずで作るな、根本から安定してトラブルを起こさないようにしっかり作れ」
> base_commit: c430251c142cda8da4de4aabea0f1ddbcdd707d0 (現 main HEAD)
> 規律: FKI-DEV-ROOT-CURE-FIRST (暫定禁・根本根治) / DD-157 役職名のみ ([[deprecated-persona-names]]) / F002 /
>       FKI-AUDIT-GREEN-TRUTH-01 / FKI-NO-DUP / Watcher Design Principles / 24時間ノンストップ
> ★本書 = 設計章節起草のみ。実 script 改変は本 task 非実施 (次 phase = shogun-third 実装 → gunshi-third 三者監査)★
> ★unit-green ≠ runtime-green 厳守 — runtime 実証まで「完成」と言わない (cycle1〜cycle4 教訓継承)★

## 0. GAP-2 とは — 解く欠落 (root cause 起点)

段階3 全自動ループの ★検知層 (detect_stale)★ は cycle1-4 dual audit ALL GREEN で land 済 (commit 207bcdd8、
`scripts/lib/detect_stale.sh` + `scripts/fukuincho_detect_stale_cli.sh`)。だが検知層 CLI は ★JSONL 行を stdin/`--input`
から受領する consumer★ であり、★「誰が Supabase pc_handshake を query し SLA 超過行を JSONL として CLI に渡すか」=
データ源 bridge が未設計★。これが GAP-2。本書はこの bridge を ★根本から堅牢に★ 設計する。

```
[GAP-2 本書の対象]                          [既 land 済 (cycle1-4 GREEN)]
┌──────────────────────────┐  JSONL (stdout)  ┌────────────────────────────────┐
│ Supabase pc_handshake      │ ───────────────→ │ fukuincho_detect_stale_cli.sh    │
│ → SLA 超過行 query bridge   │  pipe            │  --detect-stale-handshake         │
│ (本書 = 設計のみ、実装=次 phase)│                  │  (authz完全一致/flock/anomaly/dedupe)│
└──────────────────────────┘                  └────────────────────────────────┘
                                                          │ enqueue (層③ ae8083dd)
                                                          ▼ poke actuator → 「確認して」自動着弾
```

★完遂定義 (副院長令)★: 人手 GO 無しで SLA 超過を検知し「確認して」自動着弾 → ack リトライ。
fd10db2d 完全完遂 = ★「次も自動で入る」★ (一度きりでなく継続的に自動)。

## 1. データ源 = Supabase 唯一真実源 (要件1)

### 1.1 SLA 超過行抽出クエリ (誤検知ゼロ — 137 件誤検知教訓継承)

★唯一真実源 = Supabase `pc_handshake` テーブル★。bridge は下記 ★厳密 AND 条件★ の行のみを SLA 超過候補とする。

- 抽出条件 (verbatim): `response_by_time < now() AND requires_response = true AND resolved_at IS NULL`
- 宛先条件: `to_pc = 'fukuincho'` ★または★ 新着 urgent (priority = P1_top_urgent 等、未応答かつ未解決)
- PostgREST 表現 (既存 `inbox_write.sh` の REST 経路再利用、FKI-NO-DUP):
  ```
  GET ${SUPABASE_URL}/rest/v1/pc_handshake
      ?to_pc=eq.fukuincho
      &requires_response=eq.true
      &resolved_at=is.null
      &response_by_time=lt.<now_iso8601_utc>
      &select=correlation_id,from_pc,from,to_pc,target_agent,type,status,response_by_time,resolved_at,priority,requires_response
  ```
  新着 urgent は別 query (`priority=eq.P1_top_urgent&resolved_at=is.null&requires_response=eq.true`) を OR 合成。
- ★`now()` は bridge 実行ホスト時刻でなく ★UTC 統一★★ で生成し、`response_by_time` も UTC 比較 (タイムゾーン差による誤検知防止)。

### 1.2 137 件誤検知教訓の根治反映

- ★誤検知ゼロ原則★: 3 条件 (`response_by_time<now` ∧ `requires_response=true` ∧ `resolved_at IS NULL`) を
  ★全て AND★ で必須。1 条件でも欠落/緩和したクエリ禁 (137 件誤検知 = 条件緩和が真因)。
- `requires_response` 列が NULL/欠落の行は ★超過候補にしない★ (true 明示のみ。NULL を true 扱いしない)。
- `resolved_at` が非 NULL (= 解決済) 行は ★抽出対象外★ (二重 poke 源を query 段階で排除)。
- 抽出は ★server-side filter (PostgREST query params)★ で行い、client 側で全行取得後フィルタする実装禁
  (全件取得は誤検知・負荷・機密露出の温床)。

## 2. 冪等性 = 同一超過二重 poke 禁 (要件2)

二重 poke を ★3 層★ で防ぐ (1 層が抜けても次層で止める defense-in-depth)。

1. **query 層 (§1)**: `resolved_at IS NULL` filter で解決済を抽出しない。
2. **検知層 (既 land)**: `fukuincho_detect_stale_cli.sh` の ★in-flight marker (flock atomic check-and-mark)★ が
   同一 correlation_id の二重 enqueue を 1 run 内で防ぐ (cycle2 HIGH-2 cure 済、再利用)。
3. **poke 済 mark (本 bridge 新設の唯一の状態書込)**: poke + ack 成功後、当該 `correlation_id` の pc_handshake 行に
   ★`resolved_at = now()` (または専用 `poke_acked_at`) を PATCH★ する。これにより次 cron cycle で §1 query が
   当該行を ★再抽出しない★ (「次も自動で入る」を満たしつつ二重 poke を恒久排除)。
   - PATCH は ★既存 REST 経路 (inbox_write.sh と同 sb_url/sb_key)★ で行い、新規 writer を作らない (FKI-NO-DUP)。
   - ★再実行で壊れない★: PATCH 前に `resolved_at IS NULL` を condition に含め (`&resolved_at=is.null`)、
     既に他 run が解決済にした行への二重 PATCH を no-op 化 (idempotent PATCH)。
- ★状態の単一真実源は Supabase★ (in-flight marker は 1 run 内の race 防止用 ephemeral、跨 run 冪等性は resolved_at が担保)。

## 3. 障害時安全側 (要件3) — 空 fall-through 禁 (cycle2 HIGH-3 教訓継承)

★「0 件」と「取得失敗」を厳密に区別する★。これが本設計の安全核。

| 事象 | 判定 | 動作 |
|---|---|---|
| query 成功 + 0 行 | ★正常 (超過行なし)★ | poke せず正常終了 (exit 0)、`[OK] overdue=0` log |
| query 成功 + N 行 | 正常 | 各行を JSONL で検知層へ pipe |
| HTTP 非 2xx (4xx/5xx) | ★異常★ | poke せず ★異常記録 + exit≠0 で停止★、`[ANOMALY] http_status=<code>` |
| 接続断 / timeout / DNS 不能 | ★異常★ | 同上 (`[ANOMALY] connection_failed`) |
| 応答 body が JSON parse 不能 | ★異常★ | 同上 (`[ANOMALY] parse_failed`)、★空配列扱いに fall-through 禁★ |
| 認証失敗 (401/403) | ★異常★ | 同上 (`[ANOMALY] auth_failed`)、token 値はログ非出力 (機密) |

- ★絶対禁: query 失敗時に「結果 = 空」として正常 exit すること★ (cycle2 HIGH-3 の `空→fall-through→誤判定` と同型事故)。
  query 失敗 = ★暴走 poke も沈黙も両方を避け、異常記録して止まる★ (人手が異常に気付ける observability)。
- curl は ★`--fail-with-body --max-time <T> --retry 0`★ 相当で HTTP error を exit code に反映し、
  非 2xx を「成功 0 件」と誤認しない。retry は ae8083dd ack エンジン層に委譲 (bridge 層で独自 retry loop 新設禁、FKI-NO-DUP)。
- parse は ★厳格 JSON parser (python3 json.loads)★ で行い、失敗は anomaly (寛容 parse で空配列化しない)。
- 検知層 CLI 側の anomaly (rc=2: malformed/empty-deadline) も ★enqueue させない★ (cycle2/cycle4 で verify 済、再利用)。

## 4. 競合制御 = flock atomic (要件4、cycle2 HIGH-2 教訓継承)

- bridge は ★run 単位の排他 flock★ を取得してから query→pipe→PATCH を実行する
  (`flock -n -x` on 専用 lock file、例: `/tmp/fukuincho_sbridge.lock`)。`-n` で多重起動は ★即 skip★ (待たない、
  cron 60s 間隔の重畳起動を防止)。
- 検知層内部の in-flight marker も flock atomic (cycle2 HIGH-2 cure 済、§2-2) — ★bridge run 排他 ⊥ 検知層 marker 排他★ の
  二重防御。lock file は別 (bridge run lock ≠ detect_stale inflight lock) で責務分離。
- ★resolved_at PATCH も condition 付き (resolved_at=is.null) で atomic★ (§2-3)、複数ホスト/プロセスの同時 PATCH も
  Supabase 側の row 単位で安全 (1 回のみ成功、他は 0 rows affected で no-op)。

## 5. 認可 = 完全一致 validation (要件5、cycle2 HIGH-1 教訓継承、prefix 禁)

- bridge が抽出した行は ★必ず検知層 CLI の `_detect_stale_authz_check` を通過★ する (既 land、cycle2 HIGH-1 cure 済)。
  これは `sender:recipient:type` の ★完全一致 allowlist★ で、`karo-*` 等の prefix glob は ★禁 (spoof 通過源)★。
- bridge 層は ★認可ロジックを再実装しない (FKI-NO-DUP)★ — 抽出行をそのまま検知層に渡し、authz は検知層の単一 choke point に委譲。
- query の `to_pc=eq.fukuincho` filter は ★宛先絞り込み (誤配除去)★ であって認可ではない。認可は検知層 allowlist 完全一致が正本。
- ★bridge が Supabase から取得した `from` を信頼して authz を skip することは禁★ (Supabase 行も外部入力扱い、完全一致検証必須)。

## 6. ガード (要件6) — 全順守確約

- ★止血B (commit e0e98b7) 保護範囲 touch 0★: 本 bridge は ★`scripts/inbox_watcher.sh` を一切 import/改変しない★。
  cycle1〜cycle4 + post-land + systemd 切替 5 段通算で L625/L1138/L1174-1207/L1259-1264 touch 0 を維持確約
  (本書=設計のみ、実 script 触接 0)。
- ★V5 (8012f18c) 保護★: bridge は WSL file render / Windows デスクトップ窓に一切触接しない (message 層のみ)。
- ★機密 2 件触接禁★: `hermes_ro` PW + Supabase token を ★ログ・標準出力・エラー文に一切出さない★。
  token は既存 `$HOME/.hakudokai/env` (`SUPABASE_SERVICE_ROLE_KEY`) から読むのみ、値は emit_event で redact (検知層 §14 整合)。
- ★ALL-SSH-NO-NEW-ENDPOINT-01★: 新規エンドポイント増設禁。Supabase URL は既存 `inbox_write.sh` と ★同一 sb_url★ を再利用。
- ★DD-164 (sudo 不要)★: bridge は sudo を要求しない (user 権限で REST + flock + pipe 完結)。
- ★FKI-NO-DUP★: 新規 transport / poller / retry loop を ★ゼロ★ で作る。query=既存 REST 経路、retry=ae8083dd ack エンジン、
  検知=既 land CLI、認可/flock=検知層再利用。bridge が新規追加するのは ★query→pipe の結線 + resolved_at PATCH のみ★。
- ★歯式エディタ (8a6c4ddb/f719f21e G-1) 新規実装禁★ (本 task と無関係、触接ゼロ)。

## 7. 起動経路 (cron/SLA 検知層との結線)

- bridge は ★既存 cron/SLA 検知周期 (60s) から invoke★ される想定 (新規 daemon/poller 新設禁、FKI-NO-DUP)。
- 結線: `cron(60s) → fukuincho_sbridge (本書) → JSONL → fukuincho_detect_stale_cli.sh --detect-stale-handshake`。
- bridge 自体は ★1-shot CLI (query→pipe→exit)★ で常駐しない (常駐 poller は Watcher Design「専用テーブル分離」「無限ループ禁」に整合する形で cron 駆動)。

## 8. 完遂定義との対応 (人手 GO 無し自動着弾)

| 完遂要素 | 本設計での担保 |
|---|---|
| 人手 GO 無し SLA 超過検知 | §1 cron 60s + Supabase query で自動抽出 (人手介在ゼロ) |
| 「確認して」自動着弾 | 検知層 enqueue → ae8083dd → poke actuator (既 land) |
| ack リトライ | ae8083dd 全方向エンジン (再利用、新規 retry loop 禁) |
| ★「次も自動で入る」 (fd10db2d 完全完遂)★ | §2-3 resolved_at PATCH で処理済を除外しつつ、未解決の新規超過は次 cycle で再抽出 → 継続自動化 |

## 9. cycle1〜cycle4 教訓継承 (明示)

| 教訓 | 本設計での反映 |
|---|---|
| ★unit-green ≠ runtime-green★ (cycle1 dead code / cycle3 \|\| true) | 本書は設計のみ。実装後 ★runtime 実証 (実 Supabase query → 実 pipe → 実 enqueue) まで「完成」と言わない★。dual audit + runtime proof 必須 |
| RED-C3 (\|\| true で rc 破壊) | bridge は curl rc / parse rc を ★`|| true` で潰さず素直に捕捉★、HTTP error/parse fail を exit code に反映 (§3) |
| cycle2 HIGH-1 (authz prefix) | §5 完全一致委譲、prefix 禁 |
| cycle2 HIGH-2 (flock 無) | §4 run flock + 検知層 marker flock 二重 |
| cycle2 HIGH-3 (空 fall-through) | §3 「0 件」と「失敗」を厳密区別、失敗は anomaly + 停止 |
| 暫定禁 (FKI-DEV-ROOT-CURE-FIRST) | 全 6 要件を ★根本から★ 設計、暫定 stub/TODO を残さない |

## 10. 次 phase へのハンドオフ + 完了条件

- ★本 task = 設計章節起草のみ完遂★ (status: completed)。実 script 改変は ★次 phase = shogun-third 実装★。
- 実装後、★gunshi-third が三者監査 (Codex 6 軸 + Gemini 8 観点 + governing wrap-up)★ を cycle1-4 と同パターンで実施。
  実装は ★runtime 実証 (実 Supabase → 実 poke 着弾) まで「完成」と認めない (unit-green≠runtime-green 厳守)★。
- 完了条件 (実装 phase): 三者 ALL GREEN + runtime proof (人手 GO 無し SLA 超過 → 「確認して」自動着弾 + 次 cycle も自動) +
  止血B touch 0 通算維持 + 誤検知ゼロ実証。
