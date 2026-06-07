# fukuincho_desktop_poke 段階3 全自動ループ化 設計章節 — 4 層 architecture + 三者監査用 root spec

> 起草: 軍師 (gunshi-third) / 監査対象: Codex 6 軸 + Gemini 8 観点 dual + governing audit (別 ashigaru、本 task 完遂後 karo-third 起票)
> task: subtask_thirdpc_p1_fukuincho_stage3_auto_loop_design_audit_001
> parent_cmd: cmd_thirdpc_p1_fukuincho_relay_50a1b936_poke_stage2_uiawrapper_fix_001
> parent_handshake: 副院長令 de0ea041 (2) verbatim (P1 高、seq=36443) / shogun-third msg_20260607_194342_d4cac095
> base_commit: 2d0a1e48175854c0f3b5114947b4be454b90485e
> 規律: DD-157 役職名のみ ([[deprecated-persona-names]]) / F002 報告経路 / V5 (8012f18c) 保護 /
>       FKI-AUDIT-GREEN-TRUTH-01 / Watcher Design Principles / FKI-NO-DUP 第4条 / 24時間ノンストップ
> ★本書 = 設計 + 監査のみ。実装適用 (scripts 改変) は D-lane 別 task (理事長承認後)。本書での script touch = 絶対禁★

本書は、段階2 (poke 機構 runtime 実証成功 — 理事長 Claude Desktop 直視で副院長 claude.ai チャットに
「確認して」自動着弾確認、止血B /clear 発火ゼロ live 実証 PASS) を確定起点とし、段階3 ★全自動ループ化★ の
loop orchestration root spec を確定する。三者監査の監査対象 artifact として供する。

## 0. 出典 (実態 grounding — speculation 排除)

| 出典 | 内容 | 本書での扱い |
|------|------|------|
| 段階2 runtime 実証 (理事長直視 + 止血B /clear 発火ゼロ live PASS) | poke 機構の「副院長 claude.ai chat へ自動入力」が実機で成功確定 | 本ループの ★actuator 層は実証済★ を前提に loop 化のみ設計 |
| `docs/08-ops/stage3-poke-engine-design-i-iv.md` (既存、land 済) | 段階3 poke actuator root spec (i)cron/SLA・(ii)ack retry・(iii)dedupe・(iv)応答中 skip)。宛先=副院長 claude.ai chat **単一** | ★actuator 層として再利用 (再設計禁、FKI-NO-DUP)★ |
| `docs/08-ops/ack-retry-omni-engine-design.md` (ae8083dd、land 済) | ack 再送 全方向化 共通エンジン (i)-(vi)。message 層 (inbox YAML / pc_handshake)、correlation_id 貫通、5 回上限、認可境界 §2.4 | ★ack リトライ層 (層③) として再利用 (再設計禁、FKI-NO-DUP)★ |
| `docs/08-ops/fki-no-dup-4-poke-vs-ccflare-cron.md` (land 済) | poke vs ccflare OAuth cron 非重複・補完判定 | 本書の非重複判定様式の先例 |
| 素案値 `50a1b936` (承認済) | cron 60s / stale 120s / N=15s / M=3 / backoff 30-60-120s / dedupe T=60s / 応答中 skip | ★verbatim 採用 (本書 §1.2)★ |
| `docs/01-architecture/watcher-design.md` | Watcher 6 原則 (無限 retry 禁 / self-send 即 ack / 手動停止フラグ尊重 / 重複検知 / idempotency / 専用テーブル分離) | §3 適合性評価の規準 |
| CLAUDE.md Communication Protocol / Report Flow | inbox/watcher 2 層配送 + escalation table + F002 | 通知経路・routing 不変順守 |

★注 (透明性、e3c6baff 整合)★: 本 task 着手時点で `fukuincho_desktop_poke.py` は実 script として未 land
(段階3 実装=D-lane 別 task)。`detect_stale` は `fukuincho_watch` の概念機構を指す (本書は ★拡張設計のみ★、
実装は別 task)。本書は「実証済 poke actuator + 既存 ack omni engine + detect_stale 拡張」を ★ループとして結線する★
orchestration spec であって、actuator/ack engine 自体の再実装ではない。

## 1. 全自動ループ化 architecture (4 層)

### 1.1 4 層 architecture overview

```
┌─────────────────────────────────────────────────────────────────────┐
│ 層① cron/SLA 検知層 (detect_stale 拡張)                                  │
│   - cron 60s polling で pc_handshake を観測                              │
│   - response_by_time 超過 (stale 120s) or 新着 urgent を検知 → trigger   │
└───────────────┬─────────────────────────────────────────────────────┘
                │ trigger (correlation_id 付与)
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 層③ ack リトライ再送層 (ae8083dd 全方向エンジン 再利用、message 層)        │
│   - omni engine retry queue へ enqueue (correlation_id 貫通)            │
│   - 宛先=副院長 claude.ai Desktop chat の場合、下位 actuator=層② を呼出   │
│   - Stage A/B confirm 未達なら 5 回上限まで再送 (omni engine §(iv))      │
└───────────────┬─────────────────────────────────────────────────────┘
                │ actuator invoke (宛先=副院長 Desktop chat 単一)
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 層② poke 自動発火層 (段階2 実証済 actuator、stage3-poke-engine 再利用)    │
│   - claude.ai 「確認して」自動入力                                        │
│     (a3-3 段階2 成功確定の descendants(control_type=Edit) 経路再利用)     │
│   - GUI ack: window title 変化 / Edit content 増分検知、未検知なら M=3 再送│
└───────────────┬─────────────────────────────────────────────────────┘
                │ 全 leg で適用
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 層④ 誤爆抑制層                                                          │
│   - dedupe T=60s (短時間多重 poke 抑制)                                  │
│   - 応答中 skip (claude.ai busy / Commander 入力途上 → 即 skip)          │
│   - M=3 上限到達 → human_required escalation (自動 retry 停止)            │
└─────────────────────────────────────────────────────────────────────┘
```

★層番号と論理順の注記★: 副院長令の列挙は ①検知 → ②poke 発火 → ③ack リトライ → ④誤爆抑制 の機能列挙である。
実 dataflow は ①検知 → ③ack 層 enqueue → (宛先=副院長 Desktop chat 時) 層② actuator 呼出 → ④誤爆抑制 を全 leg 適用、
の順で結線される (層③ omni engine が上位 orchestrator、層② poke が下位 actuator — ae8083dd §(vi) 採用案 4 と一致)。
番号は副院長令 verbatim を保持し、dataflow 順は本注記で明示する。

### 1.2 素案値 verbatim 採用 (50a1b936 承認済)

| パラメータ | 値 | 層 | 役割 |
|---|---|---|---|
| cron 検知 polling 間隔 | **60s** | ① | detect_stale 観測周期 |
| stale 閾値 (response_by_time 超過) | **120s** | ① | poke trigger 発火閾値 |
| ack N (Stage A confirm 間隔) | **15s** | ② | poke 後の GUI 進行検知 timeout |
| M (poke actuator 再送上限) | **3** | ②④ | GUI ack 未検知時の再送上限 |
| backoff (M=1/2/3 各間隔) | **30s / 60s / 120s** | ② | poke actuator 再送 backoff |
| dedupe T (短時間多重 poke 抑制窓) | **60s** | ④ | double-fire 抑止窓 |
| 応答中 skip | **有効** | ④ | claude.ai busy / 入力途上で即 skip |
| skip_max (応答中 skip 連続上限) ★要御差配★ | **5 回 (≒5min)** | ④ | 連続 busy skip の上限。超過で human_required (B1 無限 re-enqueue 防止) |

★2 層 retry の役割分離 (FKI-NO-DUP 核心)★:
- **層② poke actuator retry (M=3, backoff 30-60-120s)** = ★GUI/Desktop 層★ の ack (window title 変化 / Edit content 増分)
  未検知時の poke 再発火。stage3-poke-engine-design-i-iv.md (ii) の素案値を ★継承★。
- **層③ message retry (ae8083dd, 5 回上限, 30/120/300/660/1380s)** = ★message 層★ の Stage A/B confirm
  (read:true / 応答 message) 未達時の inbox/handshake 再投函。ack-retry-omni-engine-design.md (iv) を ★継承★。
- 両 retry は ★key も actuator も別★ (GUI window ack ⊥ message correlation_id ack)。層③ omni engine が
  「副院長 Desktop chat」1 宛先に対して呼ぶ actuator が層② poke であり、層② の M=3 GUI 再送が尽きた事象は
  層③ の 1 回の actuator 失敗として omni engine に戻る (二重 retry でなく ★入れ子★)。

### 1.3 各層の結線詳細

- **層① → 層③**: detect_stale が stale 検知すると、対象 pc_handshake row の `correlation_id` を継承
  (新規採番しない、ae8083dd §2.4 発行主体規約順守) して omni engine retry queue へ enqueue する。
  detect_stale は ★fukuincho_watch を拡張する形★ で実装 (新規 cron poller 不新設、FKI-NO-DUP)。
- **層③ → 層②**: omni engine が宛先=副院長 claude.ai Desktop chat と解決した leg のみ、actuator として
  既存 poke engine を ★下位呼出★。他宛先 (各 PC agent 等) は omni engine が inbox/handshake transport を
  そのまま使う (poke actuator は不要)。
- **層② ack → 層③ confirm**: poke actuator の GUI ack (window 変化検知) は ★poke 成功/失敗★ を omni engine に返す。
  最終的な Stage B confirm (副院長が実際に応答した) は omni engine が message 層 (副院長→Commander の応答 handshake / read:true)
  で判定する。GUI ack 成功 ≠ Stage B confirm (poke が届いても応答が無い場合は omni engine が再送継続)。
- **層④ は全層に貫通**: dedupe T=60s は層③ enqueue 時と層② poke 発火時の双方で評価。応答中 skip は層② poke 発火直前に評価。
  M=3 到達は層② の自動 retry を停止し、層③ omni engine へ「actuator 枯渇」を通知 → omni engine が human_required へ移行。

### 1.4 実装層 feasibility 反映 + 素案値 paint check (ashigaru-third-3 並走入力に対する gunshi 設計監査御差配)

実装並走 (ashigaru-third-3) の段階2 実機経路 paint + feasibility 判定を本設計監査で評価し、下記 4 項目を御差配する。

| 項目 | 実装層入力 (a3-3) | gunshi 設計監査 御差配 |
|---|---|---|
| **層別 feasibility** | L1=GREEN / L2=GREEN / L3=GREEN_WITH_CAVEAT / L4=GREEN_WITH_CAVEAT | ★採用★。L2 actuator は段階2 経路 (descendants(control_type=Edit) cands[0] + clipboard+Enter) を unchanged 再利用、L1/L3/L4 は L2 を内包する上位層として段階2 経路に非干渉で追加可。caveat 源 = L4 応答中 skip が段階2 未実装 (段階3 新規)。 |
| **N=15s → 30s** | YELLOW: 段階2 実測で claude.ai 着弾 ~30s (19:36:37 送信→19:37:08 着弾)、N=15s は短すぎ偽 timeout 懸念。N=30s 提案 (ae8083dd 第1 checkpoint t=30s と一致 → FKI-NO-DUP 上有利) | ★gunshi 推奨 = N=30s★。ただし N=15s は承認済素案値 50a1b936 の一部ゆえ ★要御差配 (副院長殿)★ として明示。承認まで素案値は N=15s を保持し、本書に推奨 N=30s + 実測根拠を併記 (仮変更禁)。 |
| **M=3 vs ae8083dd 上限 5** | YELLOW: 数値乖離、要御差配 | ★乖離は実質非衝突と判定 (御差配済)★。M=3=層② GUI actuator retry、5=層③ message retry で ★別層・別 actuator★ (§1.2 入れ子モデル)。同一軸の競合ではないため統合不要。本書 §1.2 の入れ子定義で解消。 |
| **S1 緩和策 4 件** | mitigation_a (editing=IME∧Edit非空∧focused 3条件AND) / b (dedupe T 60→30s) / c (skip でなく re-enqueue) / d (submission inflight=submit enabled∧spinner非表示∧progress非active 3条件AND) | ★a/c/d 採用 (§4 S1/S4 に反映)★。c は本書 I3 で既採用。b (T=30s) は ★要御差配 代替★ として記録 (mitigation_c の re-enqueue が一次緩和ゆえ T=60s でも S1 緩和は成立、T=30s は追加余裕)。 |

★main_pc paint caveat (透明性開示)★: 実 `fukuincho_desktop_poke.py` source は main_pc 側に在り、third_pc 本 repo では
paint check 不能。本設計監査は段階2 実機実証 (理事長直視 PASS) + a3-3 並走 paint + 既存設計 doc を grounding とするが、
★main_pc 側 .py の構造直視 paint は本 task 範囲外 (escalate hint、実装適用=D-lane 別 task 時に main_pc paint 必須)★。
これを未確認のまま「実装可」と仮 GREEN しない (FKI-AUDIT-GREEN-TRUTH-01)。

## 2. detect_stale 拡張仕様 (層①、FKI-NO-DUP — 既存機構拡張)

★新規 cron daemon を作らない★。既存 `fukuincho_watch` の detect_stale ロジックを下記 2 点だけ拡張する。

1. **trigger 条件の拡張 (status enum 厳密化、Codex T1 是正)**: 既存 detect_stale (unread age 観測) に加え、
   pc_handshake row の `response_by_time` (SLA 締切) 超過 ★かつ★ 未応答 を stale と判定する条件を追加。
   - status enum 正本: `{pending, in_progress, confirmed, escalated, human_required, closed}`。
   - 判定: `now > response_by_time AND status ∈ {pending, in_progress}` (★終端状態 confirmed/escalated/human_required/closed は除外★)。
     ★`status != confirmed` 単独判定は使わない★ — escalated/human_required/closed を stale と誤判定し再 poke する回帰を防ぐ (Codex T1)。
   - ★malformed / null / 未知 enum 値の row は stale と判定せず★、anomaly として観察ログ (`event=status_malformed`) に記録し skip
     (不正 row 由来の自動 poke 誘発を構造的に排除、T1)。
   - 新着 urgent (priority=P1_top_urgent) は response_by_time 未到でも即 trigger 候補 (cron 次周期で評価)。
2. **trigger 認可境界 (Codex S1 是正、ae8083dd §2.4 継承)**: detect_stale は trigger 候補 row を enqueue する前に
   ★omni engine §2.4 認可境界を必ず通過させる★。検証項目 = ① row の発行主体 (`from`) が trusted pane registry と整合
   ② recipient / type が sender×recipient×type 許可行列に適合 ③ F002 routing 合法 ④ priority=P1_top_urgent は
   ★正規発行経路 (上位→下位) で採番された row のみ★ 受理。いずれか不適合 → enqueue せず `event=denied`/`reason=trigger_unauthorized`
   を記録 (不正 row / 誤 priority による自動 poke 誘発を防ぐ、監査可能化)。
3. **trigger 出力の拡張**: stale 検知 (上記 1+2 通過) 時、対象 row の `correlation_id` を ★継承★ して層③ omni engine enqueue API
   (= 既存 inbox_write.sh 経路を wrap した omni engine entrypoint) を呼ぶ。detect_stale 自身は poke を ★直接発火しない★
   (発火は層②、orchestration は層③ — 単一責務分離)。
4. **in-flight 二重評価防止 (Codex B2 是正)**: detect_stale は enqueue 前に ★当該 correlation_id が既に omni engine
   retry queue に in-flight (state ∈ {pending, unknown_lost}) で存在しないか★ を flock 下で確認し、in-flight なら
   re-enqueue せず skip する。これにより cron 60s cycle が前回 actuator retry (backoff 30/60/120s) 進行中の同一 row を
   二重評価して double-fire することを防ぐ (flock の queue 排他に加え in-flight set を持つ)。

★cron 60s の実態★: pc_handshake は既存 INSERT trigger を持つため、polling は「INSERT イベントの取りこぼし補償」の
backstop であり実質 event-driven に近い (ae8083dd §0 / S3 緩和と整合)。60s polling は過剰負荷とならない。

## 3. Watcher Design 6 原則 適合性評価 (docs/01-architecture/watcher-design.md)

| 原則 | 本ループでの充足 | 根拠 |
|---|:---:|---|
| ① retry 無限ループ禁 | ✅ | 層② M=3 上限 + 層③ 5 回上限 + ★層④ 応答中 skip も skip_max=5 上限★ (§1.2)、三者いずれの上限到達後も human_required escalation (自動停止)。busy 永続でも re-enqueue 有界 (Codex B1 是正)。二重 retry でなく入れ子 |
| ② self-send 即 ack | ✅ | 本ループは fukuincho (副院長 chat) 宛の片方向 poke。self-send は対象外 (対 ack は層② M=3 / 層③ 5 回で充足)。omni engine §2.4 self-send guard 継承 |
| ③ 手動停止フラグ尊重 | ✅ | manual_override / clear_command 経路を温存 (層④ で停止フラグ観測時は poke 即停止)。inbox_watcher 既存停止フラグと整合 |
| ④ 重複検知 | ✅ | 層④ dedupe = last-fire TTL sliding window T=60s (key=(window_handle, poke_kind)、`now - last_fire_ts < T` で抑止、固定 bucket 不使用、I2/Codex cycle2 B1) + 層③ dedupe (correlation_id, recipient, payload_digest, resend_attempt)。両 key は別 surface (GUI ⊥ message) |
| ⑤ idempotency | ✅ | 応答中 skip + correlation_id 貫通で重複 INSERT 防止 (ae8083dd §(v))。同一 stale に対する double-fire は dedupe 窓で 1 本化 |
| ⑥ 専用テーブル分離 | ✅ | pc_handshake 既存テーブルを使用 (新設不要)。omni engine retry queue / ack event log は既存設計の構造体を流用 (ae8083dd §2.5) |

★過去事故整合★: 2026-05-05 SecondPC 共食い暴走 ([[]] incident) の教訓 = 無限 retry + 重複検知欠落。
本ループは M=3 / 5 回 / dedupe / human_required で構造的に同型事故を排除する。

## 4. 副作用評価 (side effects)

| ID | 副作用 | 深刻度 | 緩和策 |
|---|---|:---:|---|
| **S1** | 応答中 skip 誤判定で正当 poke 失火 (busy 誤検知) | medium | ★editing 検出 = IME composition active ∧ Edit get_value() 非空 ∧ focused の 3 条件 AND (a3-3 mitigation_a、OR 誤検知率回避)★ + skip でなく retry queue 末尾 re-enqueue (a3-3 mitigation_c = I3、silent drop 回避) + dedupe T 窓経過後の次 cron cycle で速やか再評価 (永久 skip しない、I3) + ★skip_max=5 到達で human_required (Codex B1)★。代替 = dedupe T 60→30s (a3-3 mitigation_b、要御差配) |
| **S2** | ack リトライ累積で fukuincho inbox / chat 飽和 | low | 層② M=3 上限 + 層③ 5 回上限 + backoff exponential + human_required escalation。両上限で総再送有界 |
| **S3** | cron 60s polling コスト | low | pc_handshake は既存 INSERT trigger 活用で実質 event-driven、60s polling は取りこぼし補償 backstop のみ (§2) |
| **S4** (追補) | 層② GUI 誤爆で Commander 入力途上を上書き (連絡途絶誘発) | medium | 応答中 skip (editing 3条件AND, S1) + ★submission inflight 検出 = submit button enabled ∧ spinner 非表示 ∧ progress indicator 非active の 3 条件 AND (a3-3 mitigation_d、submit disable 中 poke の応答衝突回避)★ + V5 (8012f18c) 非占有保証 |
| **S5** (追補) | in-flight skip (I1/B2 是正) が正当な再評価を過剰抑止し re-poke 遅延 | low | in-flight 判定は state∈{pending,unknown_lost} のみ対象。confirmed/escalated/human_required へ遷移すれば即 skip 解除。actuator retry (backoff 30/60/120s) 完了で in-flight 解放され次 cycle で再評価可能 |
| **S6** (追補) | 層② actuator が clipboard+Enter 経路再利用時、Commander の既存 clipboard 内容を上書き / 機密値をログ混入 | medium | ★poke 前に clipboard 内容を退避し poke 後に復元 (save→set→Enter→restore)★ + poke ペイロード (「確認して」固定文) のみ使用し ★clipboard 実値を構造化ログに出力しない (機密混入防止、error-design §14 整合)★ (Codex cycle3 S1)。段階2 実証経路は固定文ゆえ機密非含だが、復元義務を設計明記 |

## 5. invariants (不変条件)

| ID | 不変条件 | 保証機構 |
|---|---|---|
| **I1** | cron 検知 → stale 判定 → (層③ enqueue) → poke 発火 → ack 待ち の chain は ★in-flight な同一 correlation_id を二重評価しない★ (race/double-fire 不生) | 各 cron cycle は逐次実行 + omni engine retry queue 更新は flock 排他 (ae8083dd §(v)) + ★detect_stale が in-flight set (state∈{pending,unknown_lost}) を flock 下で確認し in-flight row を skip★ (§2 (4)、Codex B2 是正)。「単一 thread」断定でなく in-flight ガードで保証 |
| **I2** | 同一 dedupe key の poke は ★直近 fire から T(=60s) 未満では 1 回も発火しない★ (真の 60s 最小間隔保証) | 層④ dedupe = ★last-fire timestamp ベースの TTL sliding window★ (key=(window_handle, poke_kind) ごとに `last_fire_ts` を保持し `now - last_fire_ts < T` なら抑止)。★固定 calendar T_bucket は使わない★ — bucket 境界をまたぐ 1 秒差の重複が別 bucket として通過する欠陥を排除 (Codex cycle2 B1)。ae8083dd の TTL window 60s と同一意味論で整合。層③ は (correlation_id, recipient, payload_digest, resend_attempt) |
| **I3** | 応答中 skip は次 cron cycle で再評価される (永久 skip しない) ★かつ skip 連続は skip_max=5 で有界★ | skip 時 retry queue 末尾へ re-enqueue (stage3-poke-engine (iv))、次 60s cycle で再判定。★skip 連続回数を correlation_id 単位で計数し skip_max=5 到達で human_required へ移行 (永久 re-enqueue 排除、Codex B1 是正)★ |
| **I4** | M=3 (層②) / 5 回 (層③) / ★skip_max=5 (層④)★ 到達後は human_required escalation (自動 retry 停止) | 上限到達で omni engine が `type: request_permission` を上位へ (F002 経路、ae8083dd §(iv))。自動再送ゼロ化 |
| **I5** | correlation_id は初回 trigger でのみ採番、再送/応答は継承 (なりすまし新規 thread 防止) | ae8083dd §2.4 発行主体規約継承。detect_stale は既存 row の correlation_id を継承 (§2) |
| **I6** (追補) | 不正 / malformed / 未認可 trigger row は自動 poke を誘発しない | detect_stale が §2 (2) 認可境界 + §2 (1) status enum 検証を通過した row のみ enqueue。不適合は denied/anomaly ログ + skip (Codex S1/T1 是正) |

## 5.1 受け入れ / 境界・異常系テスト観点 (SKIP=0 必達、Codex TEST1 是正)

実装適用 (D-lane 別 task) 時の受け入れテストは下記を ★必須網羅★ とする。設計段階で観点を固定し、実装時の取りこぼしを防ぐ。

| # | 観点 | 期待 |
|---|---|---|
| 1 | 正常: stale 検知 → poke 発火 → 副院長応答 (Stage B confirmed) | 1 回 poke で retry queue 除去、再 poke ゼロ |
| 2 | busy 永続 (応答中 skip 連続) | skip_max=5 到達 → human_required escalation、永久 re-enqueue しない (B1) |
| 3 | dedupe 窓境界 59s / 60s / 61s (last-fire TTL、抑止条件=`now - last_fire_ts < T`) | 59s=抑止 (59<60 真) / ★60s=発火許容 (60<60 偽、境界は厳密未満)★ / 61s=発火許容。off-by-one なし (Codex cycle3 B1 是正、I2 と一致) |
| 4 | M=3 (層② GUI) × omni 5 回 (層③ message) 入れ子上限 | GUI M=3 枯渇=層③ の 1 回 actuator 失敗、層③ 5 回到達で human_required。総 poke 有界 (B1) |
| 5 | 同一 correlation_id の concurrent cron 再評価 (in-flight 中に次 cycle) | in-flight set (pending/unknown_lost) を検出し skip、double-fire なし (B2/I1) |
| 6 | status enum 境界: confirmed / escalated / human_required / closed の row | stale と判定せず除外 (再 poke しない、T1) |
| 7 | malformed / null / 未知 status enum row | stale 判定せず anomaly ログ + skip (不正 row 自動 poke 誘発なし、T1) |
| 8 | 未認可 trigger row (from 不一致 / F002 違反 / 誤 priority P1) | enqueue せず denied/trigger_unauthorized ログ (S1/I6) |
| 9 | 応答中 skip → 次 cycle で busy 解除 | skip カウンタ < skip_max なら再評価で正常 poke (I3 永久 skip 否定) |
| 10 | 手動停止フラグ / clear_command 観測中 | poke 即停止 (manual_override 温存、原則③) |
| 11 | V5 (8012f18c) 描画窓が前面 | poke actuator は V5 窓を占有・触接しない (WSL file render 非対象) |

★テスト種別対応 (Codex cycle3 T1 是正)★: #1/#2/#4/#9 = unit (状態機械・上限) / #3/#6/#7 = unit (境界・enum 判定) /
#5/#8/#10 = integration (flock・concurrent cron・認可境界・停止フラグ) / #11 = manual (理事長承認後 D-lane 実機)。
実装適用 task で各観点に test 種別を確定する (SKIP=0 必達)。

## 6. FKI-NO-DUP 第4条 — 既存資産との非重複確認

| 機能 surface | 既存 stage3 poke engine (i)-(iv) | 既存 ack omni engine (ae8083dd) | inbox_watcher escalation | 本ループ (段階3 全自動ループ化) | 重複? |
|---|:---:|:---:|:---:|:---:|:---:|
| 駆動層 | GUI/Desktop (pywinauto) | message (inbox/pc_handshake) | TUI session (tmux) | ★orchestration (3 既存層の結線)★ | 異層 |
| 新規実装 surface | poke actuator 内部 | ack 確認 + SLA 再送 | session wake | ★detect_stale 拡張 2 点 + 結線のみ★ | 非重複 |
| cron/SLA 検知 | fukuincho_watch 継承 | 送信後 SLA poll | unread age | ★detect_stale 拡張 (新 poller 不新設)★ | ▲ 概念共通のみ |
| ack/retry | window 変化 + M=3 | read:true/応答 + 5 回 | Escape/clear | ★両者を入れ子で結線 (新 retry loop 不新設)★ | 非重複 (入れ子) |
| dedupe | (window,kind) + last-fire TTL 60s | (corr_id,recipient,digest,attempt) TTL 60s | — | ★両 key を TTL sliding window で適用 (固定 bucket 不使用)★ | 非重複 |

### 判定

> **三既存資産いずれとも 二重実装ではない (NOT a duplicate)。本ループは orchestration (結線) 層であり、
> 新規実装 surface は「detect_stale の trigger 条件 + 出力の 2 点拡張」と「3 既存層の入れ子結線」のみ。**

1. **vs stage3 poke engine**: 本ループは poke actuator を ★下位呼出★ するのみ (内部再設計ゼロ)。**補完**。
2. **vs ack omni engine (ae8083dd)**: 本ループは omni engine を層③ として ★そのまま採用★ し、その上位に
   detect_stale trigger を結線。omni engine §(vi) 採用案 4「副院長 Desktop 宛先は omni engine の actuator として
   stage3 poke を下位呼出」を ★具体化★ したものであり、新 retry 機構ゼロ。**補完 (具体化)**。
3. **vs inbox_watcher escalation**: 本ループは独自 nudge/Escape/clear を ★一切送らず★、受領側 wake は
   inbox_watcher へ委譲 (ae8083dd (iv) 委譲設計継承)。escalation 二重発火なし。**補完**。

### 削除責務

なし (全て非重複)。新規 transport / 新規 escalation poller / 新規 retry loop を作らない限り二重実装は発生しない。

## 7. 観察可能性 (docs/error-design-medical.md §14 整合)

- 全 loop イベント (detect_stale trigger / 層③ enqueue / 層② poke 発火 / GUI ack / Stage B confirm / dedupe skip /
  応答中 skip / M=3 枯渇 / human_required) を構造化 JSON で記録、`correlation_id` を全 leg 貫通。
- 集計可能項目: stale 検知回数、poke 発火回数、GUI ack 成功率、Stage B confirm 到達率、human_required 発火回数。

## 8. 三者監査対象マッピング

| 軸/観点 | 評価対象 |
|---|---|
| Codex 1 purpose 一致 | 副院長令 de0ea041 (2)「段階3 全自動ループ化」と本書 scope の一致 |
| Codex 2 acceptance 網羅 | 4 層 architecture + 素案値 verbatim + 6 原則 + S1-S4 + I1-I5 の存在と充足 |
| Codex 3 FKI-NO-DUP 整合 | §6 三既存資産非重複判定 + detect_stale 拡張 2 点限定 |
| Codex 4 数値妥当性 | cron60/stale120/N15/M3/backoff30-60-120/dedupe T60 の妥当性 + 2 層 retry 入れ子の有界性 |
| Codex 5 誤爆抑制実装可能性 | dedupe key + 応答中 skip の実装可能性 (S1/S4 緩和) |
| Codex 6 副院長殿 verbatim 順守 | 素案値 50a1b936 + 副院長令 de0ea041 趣旨逸脱なし |
| Gemini O1 対象範囲妥当性 | 4 層 architecture の結線整合 (層③ 上位 / 層② 下位 actuator) |
| Gemini O2 ack 機構実装可能性 | 2 層 retry 入れ子 (GUI M=3 ⊥ message 5 回) の実装可能性 |
| Gemini O3 副作用安全性 | S1-S4 緩和 + V5 (8012f18c) 保護 |
| Gemini O4 SLA 数値根拠 | inbox_watcher 120/240 / ae8083dd 30-1380 との非二重化根拠 |
| Gemini O5 誤爆抑制設計 | dedupe T60 + 応答中 skip の意味整合 (busy ≠ delivery skip、I3 永久 skip 否定) |
| Gemini O6 既存資産整合 | §6 poke=下位 actuator / omni engine=層③ / watcher=委譲 |
| Gemini O7 DD-157 役職名順守 | 戦国 persona 名 ゼロ ([[deprecated-persona-names]]) |
| Gemini O8 FKI-AUDIT-GREEN-TRUTH-01 順守 | dual 並走・仮 GREEN 禁・audit_duration 透明性 |

## 9. 絶対前提順守

- F002 順守 (報告経路 = gunshi-third → karo-third → shogun-third → commander-third → 副院長殿)。
- DD-157 役職名のみ ([[deprecated-persona-names]]、副院長令 de0ea041 (3) 自省訂正 mandate)。
- 新経路増設禁 (ALL-SSH-NO-NEW-ENDPOINT-01)、既存 writer/bridge/actuator 再利用。
- Watcher Design Principles 順守 (§3)。
- ★本書 = 設計 + 監査のみ。scripts/inbox_watcher.sh + scripts/stop_hook_inbox.sh + fukuincho_desktop_poke.py
  一切無触接 (D-lane、実装適用は別 task 理事長承認後)★。
- V5 (handshake 8012f18c) 触接ゼロ (WSL file render、Windows デスクトップ窓非占有)。

## 10. 完了条件

Codex 6 軸 + Gemini 8 観点 双方 GREEN → 4 層 architecture + 素案値 + 6 原則 + S/I 全 PASS と判定。
1 観点でも RED → 起草修正 + 再 audit (PDCA)。governing audit (別 ashigaru、a3-1 推奨) は本 task 完遂後 karo-third 起票。
最終 land は三者 ALL GREEN + 副院長殿照合後 (本書は provisional まで)。実装適用は D-lane 別 task (理事長承認後)。
