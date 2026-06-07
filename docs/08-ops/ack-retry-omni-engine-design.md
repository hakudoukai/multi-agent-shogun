# ack 再送 全方向化 共通エンジン 設計章節 (i)-(vi) — root spec (task ae8083dd 本実装用)

> 起草: 軍師 (gunshi-third) / 監査: 軍師自身 Codex 6軸 + Gemini 8観点 dual / base_commit: 2db25d6
> parent_cmd: cmd_thirdpc_p1_fukuincho_relay_3p1_v5crash_poke_kartevisits_001
> parent_handshake: ee6ec357 (seq=36269) / task_tracker: ae8083dd (差配1 全方向共通エンジン格上げ承認)
> task: subtask_thirdpc_p1_ack_retry_omni_engine_design_draft_dual_audit_001
> 規律: DD-157 役職名のみ / F002 報告経路 / V5 (8012f18c) 保護 / FKI-AUDIT-GREEN-TRUTH-01 / Watcher Design Principles / FKI-NO-DUP 第4条

本書は差配1「ack 再送 全方向化 共通エンジン」の root spec を確定し、軍師自身の Codex 6軸 + Gemini 8観点
dual audit の監査対象 artifact として供する。素案値は ★要御差配★ 印を付す。

## 0. 出典 (実態 grounding — speculation 排除)

| 出典 | 内容 |
|------|------|
| pc_handshake `ee6ec357` (seq=36269, 副院長殿 → Commander) | 差配1 ack 再送全方向化 共通エンジン格上げ承認 |
| task_tracker `ae8083dd` | 差配1 全方向共通エンジン格上げ承認 |
| 既存実装 `scripts/inbox_write.sh` (実機) | flock 付き inbox YAML append + self-send guard + amplification guard + cross-PC Supabase pc_handshake bridge (settings.yaml `pc_mapping`/`supabase_bridge` で target_pc 解決、content 2000 char truncate) |
| 既存実装 `scripts/inbox_watcher.sh` (実機) | 受領側 wake-up + escalation。`ESCALATE_PHASE1=120` (Escape×2+nudge) / `ESCALATE_PHASE2=240` (/clear)、Working-busy guard、stop hook 補助 |
| 既存実装 `scripts/bulk_ack.sh` (実機) | type 別 filter bulk ack。保護 type = task_assigned/qc_fail/cmd_new/directive/redo/urgent_stop/request_permission |
| 既存設計 `docs/08-ops/stage3-poke-engine-design-i-iv.md` (273d01c/2db25d6 land) | fukuincho_desktop_poke GUI/Desktop actuator 段階3 (cron/SLA・ack retry・dedupe・応答中 skip)。宛先=副院長 claude.ai Desktop chat **単一** |
| 既存判定 `docs/08-ops/fki-no-dup-4-poke-vs-ccflare-cron.md` (273d01c land) | poke vs ccflare OAuth cron 非重複・補完判定 (本書の判定様式の先例) |
| CLAUDE.md Communication Protocol | inbox/watcher 2層配送 + escalation table (0-2/2-4/4min) + Report Flow (家老→将軍 = dashboard only, F002) |

## 1. 解く failure mode (root cause 起点)

- **failure mode**: agent 間 message が「送りっぱなし (fire-and-forget)」で、相手が ★受領したか / 読んだか / 応答したか★ を
  送り手が検証しない。受領側 session が落ちている / recovery 中 / watcher 停止中の場合、message が
  silent に滞留・喪失し、上位は「配送した」と誤認する。
- 既存 `inbox_watcher.sh` は ★受領側 session の wake-up★ (nudge/Escape/clear) は担うが、
  ★送り手側の「この message が確かに届き読まれた」確認 (ack)★ は担わない。この欠落層を本エンジンが埋める。
- 本エンジンの精神そのものが ★fire-and-forget 禁★ である (相手受領まで送り手の責任)。

## (i) 全方向対象範囲

- **対象 pair**: 副院長 ↔ Commander ↔ 各 PC 将軍 (shogun-main / shogun-second / shogun-third) ↔ karo ↔ ashigaru ↔ gunshi の
  **全双方向**。エンジン機構は方向非依存 (direction-agnostic)。
- **routing policy は chain-of-command を不変順守 (F002)**: 機構が全方向対応でも、実 routing は
  既存規律 (gunshi/ashigaru/karo → 副院長殿 直接禁、必ず karo → shogun → Commander → pc_handshake) に従う。
  本エンジンは ★既存 inbox_write.sh / pc_handshake が許す合法経路を wrap するのみ★ で、新経路を増設しない
  (ALL-SSH-NO-NEW-ENDPOINT-01 整合)。
- **2 transport 層を両 cover**:
  - **L-inbox (同一 PC)**: `queue/inbox/{recipient}.yaml` への flock append (`inbox_write.sh` 既存経路)。
  - **L-handshake (跨 PC)**: Supabase `pc_handshake` への INSERT (`inbox_write.sh` cross-PC bridge 既存経路)。
- **scope 外 (明示)**: 家老 → 将軍/理事長 の **dashboard.md 経路** は push 型 inbox でなく pull 型 summary ゆえ
  本 ack エンジンの対象外 (CLAUDE.md Report Flow 順守、「inbox to shogun FORBIDDEN」と整合)。

## (ii) ack confirm polling 機構 (2 段確認 — fire-and-forget 禁)

送り手は下記 2 段を ★必須★ とし、Stage B 達成まで message の責任を保持する。

- **Stage A — 着信確認 (delivery)**: message が物理的に相手 inbox に landing したことを確認。
  - L-inbox: append 直後 `inbox_write.sh` が返す `id` を ★YAML parser★ (`yaml.safe_load`) で
    `queue/inbox/{recipient}.yaml` から探索し、`id == <返却 id>` の entry が ★実在すること★ のみを着信成功条件とする。
    ★`read` flag の値 (false/true) は Stage A 判定に用いない★ — append 直後に受領側が高速処理して `read == true`
    になった正常配送を着信失敗と誤判定する race を排除するため (Codex cycle2 B1)。`read == true` を観測した場合は
    その時点で Stage B `confirmed` に直行する。
    ★grep substring 一致は使わない★ (content 内 literal 誤検知回避、[[stop-hook-grep-unanchored-false-positive]] 教訓)。
  - L-handshake: `correlation_id` を key に対応 `pc_handshake` row を SELECT し存在確認。
  - root spec 命題: 「送ったつもり」を排除 (write 成功 ≠ 着信、必ず id 一致 entry の読み返しで grounding)。
- **Stage B — 受領確認 (receipt)**: 相手が当該 message を ★処理した★ ことを確認。判定は ★対象 message id (or correlation_id) に直接ひも付ける★。
  - 主信号: YAML parser で ★同一 id の entry を特定★ し、その entry の `read == true` を確認。
    ★「read: false 行の消失」を confirmed と見なさない★ — entry 削除 / YAML 整形差分 / rotation / 別 entry の
    read 変化では誤確認しうるため (Codex B1)。
  - 副信号: 同一 `correlation_id` を ★明示参照★ する応答 message (報告 / qc / ack response id) の着信。
  - ★entry 消失 (id が parser で発見不能) = `confirmed` ではなく `unknown/lost` 扱い★ → (iv) の retry / escalate
    対象とする (silent に「届いた」と断定しない)。
- **fire-and-forget 禁**: Stage B `confirmed` 未達の間、message は「未確認」状態として送り手の retry queue に残る。
- **poll cadence 素案**: Stage A は append 直後 1 回 + 2s 後再確認、Stage B は (iv) の SLA checkpoint で poll
  (独立した高頻度 poll loop は新設しない — Watcher Design Principles「無限 retry 禁」順守)。

## (iii) recovery 中 inbox 直接投函 bypass (補助経路)

- **主経路**: pc_handshake (跨 PC) / inbox_watcher 連動 (同一 PC wake)。
- **bypass 条件**: recovery 中で ★watcher 起動前★ or cross-PC bridge 不通の場合に限り、
  送り手は `queue/inbox/{recipient}.yaml` への flock append を補助経路として許容する。
  - ★必ず既存 `inbox_write.sh` 経由に限定する (hand-rolled 直接 writer 禁)★ — これにより
    self-send guard / amplification guard / flock を ★漏れなく継承★ する (新規 writer 余地を残さない、FKI-NO-DUP / Codex S1)。
  - bypass の受け入れ条件 (全て必須): ① ★§2.4 認可境界を通過★ (from 一致 + sender×recipient×type 許可行列 + F002)
    ② `correlation_id` 付与 (再送/応答は既存継承、§2.4) ③ ack event log に `bypass=true` を記録 (観察可能性 §2)。
    いずれか欠落で bypass 不許可 → 主経路復帰待ち。
  - 跨 PC で相手 inbox に直接到達できない場合は pc_handshake を主経路に保ち、bypass は ★同一 PC 限定★。
- **bypass 後の整合**: watcher 復帰後に同一 `correlation_id` の pc_handshake row と inbox entry が
  二重に存在しうるため、(v) dedupe で 1 本化する (double-delivery 防止)。
- **third_pc 注意**: 実 inbox は `-third` suffix ([[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]]、
  `gunshi-third.yaml` であって `gunshi.yaml` ではない)。bypass 直接 append 時の path 誤りに注意。
- root spec 命題: ★recovery 中でも message を喪失させない★ (silent drop 禁、24時間ノンストップ整合)。

## (iv) 再送 SLA / 上限 (黄取りこぼし克服 — message 層)

送信後、Stage B `confirmed` 未達のとき下記 ★単一の状態遷移表★ に従って再送する
(表と本文の数列を一本化、Codex B2 / Gemini COMP-01)。`t` は初回送信後の累計経過秒、`gap` は直前 checkpoint からの間隔。

| t (累計) | gap | retry_count | action | escalate | 出典 |
|---:|---:|:---:|---|---|---|
| 0 | — | 0 | send + Stage A 着信確認 | — | — |
| 30s | 30s | 1 | confirm 未達 → 再送 #1 | — | 副院長 verbatim |
| 120s | 90s | 2 | confirm 未達 → 再送 #2 | — | 副院長 verbatim |
| 300s | 180s | 3 | confirm 未達 → 再送 #3 + ★上位 escalate 通知★ (上位 inbox `type: notification`、再送は継続) | notify (停止せず) | 副院長 verbatim |
| 660s | 360s | 4 | confirm 未達 → 再送 #4 | — | backoff 継続 |
| 1380s | 720s | 5 | confirm 未達 → 再送 #5 (★最終再送★) | — | 上限手前 |
| >1380s & 未達 | — | 上限到達 | ★自動再送停止★ | ★human_required★ (上位 inbox `type: request_permission`「5 回再送しても受領不能」) | 5 回上限 |

- **backoff の定義 (一本化 — 表が唯一の正本、Codex cycle3 B2)**: 副院長 verbatim の固定 checkpoint
  (t=30 / 120 / 300s, gap=30 / 90 / 180s) を ★優先★ する。t=300s 以降は ★`gap_next = gap_current × 2`★
  (180 → 360 → 720s) で算出 (t=660s, t=1380s)。
  ★jitter (±20%) は「再投函の実行時刻」にのみ適用★ し、★固定 checkpoint (30/120/300s) は判定時刻として jitter 非適用★
  とする (escalate@300s 等の受け入れテストと厳密時刻が衝突しないため、Codex cycle4 B1)。
  ★上記表の値が実装の唯一正本★ で、本文式は表の tail 導出根拠 (表と本文を一致させる)。
- **escalate の意味**: 300s の escalate は ★通知 (notify) であり再送停止ではない★。再送は 5 回上限まで継続する。
- **再送上限 = 5 回**。到達後 confirm 未達なら ★自動再送停止 + human_required escalation★
  (上位 inbox に `type: request_permission`)。Watcher Design Principles「無限 retry 禁」必達。
- **confirmed 到達時**: いずれの checkpoint でも Stage B `confirmed` を観測した時点で ★即座に retry queue から除去★ し以降の再送を停止。
- **★inbox_watcher escalation との非二重化 (FKI-NO-DUP 上の核心要件)★**:
  - inbox_watcher の escalation (PHASE1=120s Escape×2 / PHASE2=240s /clear) は ★受領側 session の wake-up★ 層。
  - 本エンジンの SLA 再送は ★送り手側 message の再投函★ 層。両者は ★key も actuator も別★
    (recipient session age + TUI nudge ⊥ message correlation_id + inbox/handshake re-append)。
  - ★本エンジンは独自の TUI nudge / Escape / clear を一切送らない★。受領側 wake は inbox_watcher に **委譲** する。
    これにより escalation の二重発火を構造的に排除する (重複回避の唯一要件、(vi) 判定に直結)。

## (v) 誤爆抑制 (dedupe — recovery 順守)

- **dedupe の対象 (限定)**: dedupe は ★偶発的な重複「初回」送信★ と ★(iii) bypass 由来の二重 delivery★ のみを抑止する。
  ★(iv) の SLA scheduled retry は dedupe 対象外★ — さもなくば retry#1 (t=30s) が TTL=60s 窓内で同一 key として
  抑止され、正当な再送が落ちる (Codex cycle3 B1)。
- **dedupe key**: `(correlation_id, recipient, payload_digest, resend_attempt)` の四項組。`payload_digest` = content の sha (truncate 後)、
  `resend_attempt` = retry_count (初回=0, 再送#N=N)。★`resend_attempt` を key に含めることで同一 retry_count の二重実行のみを抑止★ し、
  異なる retry_count の scheduled retry は別 key として必ず投函される。
- **TTL window**: 60 秒。同一四項 key の重複送信を TTL 窓内で抑止 (Watcher Design Principles 重複検知/idempotency 順守)。
- **bypass 由来の二重を 1 本化**: (iii) の bypass で pc_handshake row と inbox entry が二重化した場合、
  同一 `correlation_id` で 1 本に収斂させる (watcher 復帰後の consolidation)。
- **★応答中 (recipient working) は skip 不要 = 必ず投函★**:
  - dedupe は ★同一 message の重複★ のみを抑止する。recipient が busy/working でも ★delivery (inbox 投函) は必ず行う★。
  - 区別: inbox_watcher は busy 時 ★nudge★ を skip する (wake 不要) が、本エンジンは ★delivery★ を skip しない。
    busy = 「起こす必要なし」であって「届けなくてよい」ではない (recovery 順守、message 喪失禁)。
- **既存 inbox_write.sh guard 再利用**: self-send guard / amplification guard (embedded header ≥3 で reject) を
  そのまま活かす (新規 guard を二重実装しない)。
- **retry queue の atomicity**: retry queue / dedupe state の更新は ★flock 排他★ で行い、複数 sender が同一
  `correlation_id` を同時操作しても状態破損・二重投函を起こさない (inbox_write.sh の flock 機構と同様、§2.6 test #16-17)。

## (vi) FKI-NO-DUP 第4条 — 既存 stage3 章節 (i)-(iv) との非重複確認

### 機能 surface 分解

| 機能 surface | stage3 poke engine (i)-(iv) | 本案 ack omni engine | inbox_watcher escalation | 重複? |
|---|:---:|:---:|:---:|:---:|
| 駆動層 | GUI/Desktop (pywinauto, Windows) | message (inbox YAML / pc_handshake) | TUI session (tmux) | 異層 |
| 宛先範囲 | 副院長 claude.ai Desktop chat **単一** | **全方向 全 agent pair** | 受領側 session 単位 | 異 scope |
| 駆動対象 | chat window 文字入力 (turn 進行) | message 受領 ack 確認 + 再投函 | session wake (nudge/clear) | 非重複 |
| cron/SLA 検知 | fukuincho_watch 継承 (新 poller 不新設) | 送信後 SLA poll (新 loop 不新設) | unread age (PHASE1/2) | ▲ 概念共通のみ |
| ack/retry | window title 変化検知 + M=3 再送 | read:true / 応答 検知 + 5 回上限再送 | Escape×2 / /clear | ▲ 概念共通のみ |
| dedupe | (window_handle, poke_kind, T_bucket) | (correlation_id, recipient, payload_digest, resend_attempt) | — | 非重複 (別 key、SLA retry は対象外) |
| 応答中 skip | editing/submission inflight → poke 中止 | ★delivery は skip せず★ (nudge は watcher に委譲) | busy → nudge skip | 非重複 (意味反転) |

### 判定

> **三者いずれとも 二重実装ではない (NOT a duplicate)。補完関係 (complementary)。**

1. **vs stage3 poke engine**: poke = ★GUI/Desktop actuator・宛先単一 (副院長 Desktop chat)★。
   本案 = ★message 層・全方向★。poke は本 omni engine が「副院長 Desktop chat」という ★1 宛先に対して
   呼び出す actuator の 1 種★ と位置付けられる (omni engine が上位、poke が下位 actuator)。
   重複は「cron/SLA」「ack/retry」の ★概念名★ のみで、駆動層・key・actuator は完全異層。**補完**。
2. **vs inbox_watcher escalation**: watcher = ★受領側 session wake-up★、本案 = ★送り手側 message ack★。
   本案は ★独自 nudge/Escape/clear を一切送らず watcher へ wake を委譲★ することで escalation 二重発火を排除。
   両者は別層で連動する。**補完 (重複回避要件 = (iv) の委譲設計で達成)**。
3. **vs inbox_write.sh / pc_handshake / bulk_ack.sh**: 本案は ★既存 writer / bridge / guard を再利用★ し、
   新規 transport・新規 guard を ★一切新設しない★。ack 確認層のみを新規追加。**非重複**。

### 採用案 (統合 + 補完並存)

1. **transport**: 既存 `inbox_write.sh` (L-inbox flock + L-handshake pc_handshake bridge) を ★唯一の writer★ として再利用。
2. **受領側 wake**: 既存 `inbox_watcher.sh` escalation に ★委譲★ (本案は独自 nudge を新設しない)。
3. **ack 確認層**: 本案が新規追加する ★唯一の層★ = Stage A/B confirm poll + SLA 再送 + 5 回上限 + 人手 escalation。
4. **副院長 Desktop 宛先**: 本 omni engine の actuator として既存 stage3 poke engine を ★下位呼び出し★。
5. **削除責務**: なし (全て非重複)。新規 transport / 新規 escalation poller を作らない限り二重実装は発生しない。

## 2. 観察可能性 (docs/error-design-medical.md §14 整合)

- 全 ack イベント (send / Stage A confirm / Stage B confirm / resend#N / escalate / human_required) を
  構造化 JSON で記録、`correlation_id` を全 leg に貫通させる。
- 再送回数・最終 verdict (confirmed / escalated / human_required) を集計可能に。

## 2.4 認可境界 (authorization — 全方向化の権限境界、Codex S1)

全方向化により ★ローカル実行可能な任意主体が高権限 type を偽装して inbox_write.sh を叩く★ 余地が生じる。
これを機械的に閉じるため、本エンジンは下記認可契約を ★必須★ とする (bypass / 通常経路 双方に適用)。

- **caller identity の確定 (多層、tmux option 単独を認証根拠にしない、Codex cycle3 S1)**:
  - inbox_write.sh は ★中央管理された trusted pane registry★ を唯一の認可根拠とする。registry =
    `config/settings.yaml` `pc_mapping.*.agents` (固定 pane ↔ agent_id 対応の正本)。
  - 呼出時、inbox_write.sh は ① 呼出元 pane (`$TMUX_PANE`) を取得 ② registry で当該 pane に紐づく agent_id を引き
    ③ 引いた agent_id と引数 `from` が ★一致必須★ (不一致 → reject + `event=denied`/`reason=from_mismatch`)。
  - ★`$TMUX_PANE` 文字列照合だけでは不足 (env var 偽装可能)★ → ★実プロセス所属検証を必須★ とする (Codex cycle4 S1):
    inbox_write.sh は当該 pane の `tmux display-message -p '#{pane_pid}'` を取得し、自プロセスの PPID/PGID/SID 系譜を
    辿って ★当該 pane_pid 配下から実行された★ ことを照合する (`$TMUX_PANE` env のみを根拠にしない)。系譜不一致 → reject。
  - ★tmux `@agent_id` option の自己申告値は補助確認のみ★ で、registry (固定 pane↔agent_id) + プロセス系譜が優越する。
  - ★非 tmux 実行 (pane_pid 系譜照合不能) は原則 reject★。例外 = infrastructure 層の Commander SSH 着火 (DD-177 第1層) のみで、
    ★固定 allowlist (caller host/user) + 署名 + 監査ログ必須★ とし、汎用 bypass にしない。
- **sender × recipient × type 許可行列 (最小)**:

  | 区分 | 許可される sender → recipient / type | 拒否例 |
  |---|---|---|
  | F002 routing | 下位 → 直上位のみ (ashigaru→karo/gunshi, gunshi→karo, karo→shogun(dashboard), shogun→commander, commander→副院長) | gunshi/ashigaru → 副院長 直接、下位 → 2段飛ばし |
  | 高権限 type | `directive` / `urgent_stop` / `clear_command` / `model_switch` は ★上位 → 下位 のみ★ | ashigaru/gunshi が `directive`/`clear_command` を発行 |
  | self-send | sender == recipient | inbox_write.sh 既存 guard で reject |

- **correlation_id 発行主体**: ★初回送信者のみ★ が新規 `correlation_id` を採番する。再送・bypass・応答は
  既存 `correlation_id` を ★継承★ し新規採番しない (なりすまし新規 thread 防止)。
- **trusted-caller 境界**: 認可判定は ★inbox_write.sh 内★ で行う (単一 choke point)。hand-rolled writer 禁 ((iii) と一体)。
- **拒否時**: 投函せず ack event log に `event=denied` + 理由 (from_mismatch / routing_violation / type_not_allowed) を記録。

## 2.5 最小スキーマ (実装者向け、Codex T1)

| 構造体 | 必須 field | 型 | nullable | 備考 |
|---|---|---|:---:|---|
| inbox YAML entry | `id` | string | no | inbox_write.sh 採番 (既存) |
| | `correlation_id` | string | no | ★本エンジン新設 (全 leg 貫通 key)★ |
| | `from` / `type` / `content` / `timestamp` | string | no | 既存 inbox_write.sh field |
| | `read` | bool | no | Stage B 判定対象 (既存) |
| pc_handshake row | `correlation_id` | string | no | inbox entry と同値で対応付け |
| | `from_pc` / `target_pc` / `target_agent` | string | no | 既存 bridge field |
| retry queue item | `correlation_id` / `recipient` | string | no | dedupe key 構成 |
| | `payload_digest` | string | no | content sha (truncate 後) |
| | `retry_count` | int | no | 0..5、(iv) 状態表と対応 |
| | `next_checkpoint_at` | epoch sec | no | 次 poll/再送予定時刻 |
| | `state` | enum | no | pending / unknown_lost / confirmed / escalated / human_required (`unknown_lost` = (ii) entry 消失時) |
| | `status_detail` | string | yes | unknown_lost の理由 (entry_missing / parse_error 等) |
| ack event log | `correlation_id` / `event` / `ts` | string | no | event ∈ {send, stageA, stageB, resend, escalate, human_required, **denied**} |
| | `retry_count` / `bypass` | int / bool | no | bypass=true は (iii) 経路のみ |
| | `reason` | string | yes | denied 時必須 (from_mismatch / routing_violation / type_not_allowed / non_tmux) |

## 2.6 受け入れテスト観点 (SKIP=0 必達、Codex TS1)

| # | 観点 | 期待 |
|---|---|---|
| 1 | 正常: send → 相手 read:true → confirmed | 1 回送信で retry queue 除去、再送ゼロ |
| 2 | Stage B 誤確認防止: read:false 行のみ消失 (id は別) | confirmed と判定しない (unknown/lost → retry) |
| 3 | entry 消失 (id parser 発見不能) | unknown/lost 扱い → retry / escalate |
| 4 | 重複 delivery (同 correlation_id+recipient+digest, TTL 60s 内) | dedupe で 1 本化、二重投函なし |
| 5 | busy recipient | ★delivery は実行★ (nudge のみ watcher が skip) |
| 6 | watcher 停止 + 同一 PC | bypass (inbox_write.sh 経由) で投函成功 + 復帰後 dedupe |
| 7 | pc_handshake 不通 (跨 PC) | bypass せず主経路復帰待ち + escalate checkpoint 到達 |
| 8 | retry 上限 (5 回) 到達 | 自動再送停止 + human_required (request_permission) |
| 9 | F002 routing 違反 (gunshi→副院長 直接) | bypass/通常とも拒否 + denied ログ |
| 10 | escalate@300s | notify 発火 + 再送継続 (停止しない) |
| 11 | 高権限 type 偽装 (ashigaru が `directive`/`clear_command` 発行) | §2.4 行列で拒否 + denied ログ |
| 12 | `from` 詐称 (呼出元 @agent_id 不一致) | from_mismatch で拒否 |
| 13 | correlation_id 再採番試行 (再送/応答が新規採番) | 拒否 (既存 id 継承必須) |
| 14 | dedupe TTL(60s) vs retry#1(30s) 相互作用 | 未 confirmed の retry#1 は TTL 窓内でも必ず再投函 (resend_attempt 差で別 key)、同一 retry_count 二重実行のみ抑止 |
| 15 | 非 tmux 実行 ($TMUX_PANE 不在 / pane_pid 系譜照合不能) | reject + denied/non_tmux ログ (Commander SSH 着火 allowlist のみ例外) |
| 16 | 並行: 複数 sender が同一 correlation_id を同時再送 | retry queue 更新 atomicity (flock) で競合解消、二重投函なし |
| 17 | 並行: retry queue lock 競合 | flock 待ち後に整合更新、状態破損なし |
| 18 | 片側 transport 成功 (pc_handshake 成功 / inbox 失敗 or 逆) | 復旧後 correlation_id で 1 本化、喪失・二重なし |
| 19 | correlation_id 衝突 (異 thread が同値採番) | §2.4 発行主体規約で防止、検出時 reject |

## 3. 軍師 dual audit 対象マッピング (本案件 self-audit)

| 軸/観点 | 評価対象 |
|---|---|
| Codex 1 purpose 一致 | 差配1「ack 再送全方向化共通エンジン」と本書 scope の一致 |
| Codex 2 acceptance 6 章節網羅 | (i)-(vi) 全章節の存在と充足 |
| Codex 3 FKI-NO-DUP 第4条整合 | (vi) 三者非重複判定 + 委譲設計 |
| Codex 4 SLA 数値妥当性 | 30/120/300s + backoff + 上限5 の妥当性 |
| Codex 5 誤爆抑制実装可能性 | dedupe key (correlation_id, recipient, payload_digest) の実装可能性 |
| Codex 6 副院長殿 verbatim 順守 | parent_handshake ee6ec357 趣旨逸脱なし |
| Gemini O1 全方向対象範囲妥当性 | (i) 全 pair + 2 transport 層 + F002 routing 不変 |
| Gemini O2 ack 機構実装可能性 | (ii) 2 段確認の grep/SELECT 実装可能性 |
| Gemini O3 recovery bypass 安全性 | (iii) flock 直接 append + 跨 PC 限定 + dedupe 整合 |
| Gemini O4 再送 SLA 数値根拠 | (iv) inbox_watcher 120/240 との非二重化根拠 |
| Gemini O5 誤爆抑制 dedupe key 設計 | (v) busy≠skip-delivery の意味整合 |
| Gemini O6 既存 stage3 章節整合 | (vi) poke = 下位 actuator 位置付け |
| Gemini O7 DD-157 役職名順守 | 戦国 persona 名 ゼロ ([[deprecated-persona-names]]) |
| Gemini O8 FKI-AUDIT-GREEN-TRUTH-01 順守 | dual 並走・仮 GREEN 禁 |

## 4. 絶対前提順守

- F002 順守 (報告経路 = gunshi-third → karo-third → shogun-third → commander-third → 副院長殿)。
- DD-157 役職名のみ (戦国 persona 禁、副院長令 3efc70d2 整合)。
- 新経路増設禁 (ALL-SSH-NO-NEW-ENDPOINT-01)、既存 writer/bridge 再利用。
- Watcher Design Principles 順守 (無限 retry 禁 = 5 回上限、重複検知 = dedupe、idempotency = correlation_id)。
- fire-and-forget 禁 (本案件自身の精神)。

## 5. 完了条件

Codex 6軸 + Gemini 8観点 双方 GREEN → (i)-(vi) 全 PASS と判定。
1 観点でも RED → 起草修正 + 再 audit (PDCA)。最終 PASS は副院長殿照合後 (provisional まで)。
land 後、本職 (karo-third) inbox へ commit hash + dual audit row id (codex+gemini) + base_commit hash を添えて報告 (F002)。
