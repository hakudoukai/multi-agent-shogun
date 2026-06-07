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
  - L-inbox: append 直後 `inbox_write.sh` が返す `id` を `queue/inbox/{recipient}.yaml` で grep し、
    `read: false` 状態の entry 実在を確認。
  - L-handshake: 対応 `pc_handshake` row の SELECT で存在確認。
  - root spec 命題: 「送ったつもり」を排除 (write 成功 ≠ 着信、必ず読み返しで grounding)。
- **Stage B — 受領確認 (receipt)**: 相手が message を ★処理した★ ことを確認。
  - 主信号: 当該 `id` の `read: true` 化 (anchored `^  read: false$` → 消失で判定、phantom 誤検知回避は
    [[stop-hook-grep-unanchored-false-positive]] 教訓順守)。
  - 副信号: 同一 `correlation_id` を参照する応答 message の着信 (報告/qc 等)。
- **fire-and-forget 禁**: Stage B 未達の間、message は「未確認」状態として送り手の retry queue に残る。
- **poll cadence 素案**: Stage A は append 直後 1 回 + 2s 後再確認、Stage B は (iv) の SLA checkpoint で poll
  (独立した高頻度 poll loop は新設しない — Watcher Design Principles「無限 retry 禁」順守)。

## (iii) recovery 中 inbox 直接投函 bypass (補助経路)

- **主経路**: pc_handshake (跨 PC) / inbox_watcher 連動 (同一 PC wake)。
- **bypass 条件**: recovery 中で ★watcher 起動前★ or cross-PC bridge 不通の場合に限り、
  送り手は `queue/inbox/{recipient}.yaml` へ ★flock 経由直接 append★ を補助経路として許容する。
  - 実装は既存 `inbox_write.sh` の local flock path を ★そのまま再利用★ (新規 writer を書かない、FKI-NO-DUP)。
  - 跨 PC で相手 inbox に直接到達できない場合は pc_handshake を主経路に保ち、bypass は同一 PC 限定。
- **bypass 後の整合**: watcher 復帰後に同一 `correlation_id` の pc_handshake row と inbox entry が
  二重に存在しうるため、(v) dedupe で 1 本化する (double-delivery 防止)。
- **third_pc 注意**: 実 inbox は `-third` suffix ([[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]]、
  `gunshi-third.yaml` であって `gunshi.yaml` ではない)。bypass 直接 append 時の path 誤りに注意。
- root spec 命題: ★recovery 中でも message を喪失させない★ (silent drop 禁、24時間ノンストップ整合)。

## (iv) 再送 SLA / 上限 (黄取りこぼし克服 — message 層)

送信後、Stage B 受領確認の poll checkpoint を下記 SLA で配置する。

| 経過 (送信後) | action | 備考 |
|---|---|---|
| 30 秒 | confirm 未達 → **1 度目再送** | 素案 ★要御差配★ |
| 120 秒 | confirm 未達 → **2 度目再送** | 素案 ★要御差配★ |
| 300 秒 | confirm 未達 → **escalate** (上位 → Commander / 副院長殿、F002 経路) | 素案 ★要御差配★ |

- **backoff**: 指数バックオフ + jitter (flood 防止)。素案間隔 30 → 60 → 120 → 240s に jitter ±20%。
- **再送上限 = 5 回**。超過時は ★人手判断要 escalation★ (自動再送停止 + 上位 inbox に
  `type: request_permission` で「N 回再送しても受領不能」を報告)。Watcher Design Principles「無限 retry 禁」必達。
- **★inbox_watcher escalation との非二重化 (FKI-NO-DUP 上の核心要件)★**:
  - inbox_watcher の escalation (PHASE1=120s Escape×2 / PHASE2=240s /clear) は ★受領側 session の wake-up★ 層。
  - 本エンジンの SLA 再送は ★送り手側 message の再投函★ 層。両者は ★key も actuator も別★
    (recipient session age + TUI nudge ⊥ message correlation_id + inbox/handshake re-append)。
  - ★本エンジンは独自の TUI nudge / Escape / clear を一切送らない★。受領側 wake は inbox_watcher に **委譲** する。
    これにより escalation の二重発火を構造的に排除する (重複回避の唯一要件、(vi) 判定に直結)。

## (v) 誤爆抑制 (dedupe — recovery 順守)

- **dedupe key**: `(correlation_id, recipient, payload_digest)` の三項組。`payload_digest` = content の sha (truncate 後)。
- **TTL window**: 60 秒。同一 key の重複送信を TTL 窓内で抑止 (Watcher Design Principles 重複検知/idempotency 順守)。
- **bypass 由来の二重を 1 本化**: (iii) の bypass で pc_handshake row と inbox entry が二重化した場合、
  同一 `correlation_id` で 1 本に収斂させる (watcher 復帰後の consolidation)。
- **★応答中 (recipient working) は skip 不要 = 必ず投函★**:
  - dedupe は ★同一 message の重複★ のみを抑止する。recipient が busy/working でも ★delivery (inbox 投函) は必ず行う★。
  - 区別: inbox_watcher は busy 時 ★nudge★ を skip する (wake 不要) が、本エンジンは ★delivery★ を skip しない。
    busy = 「起こす必要なし」であって「届けなくてよい」ではない (recovery 順守、message 喪失禁)。
- **既存 inbox_write.sh guard 再利用**: self-send guard / amplification guard (embedded header ≥3 で reject) を
  そのまま活かす (新規 guard を二重実装しない)。

## (vi) FKI-NO-DUP 第4条 — 既存 stage3 章節 (i)-(iv) との非重複確認

### 機能 surface 分解

| 機能 surface | stage3 poke engine (i)-(iv) | 本案 ack omni engine | inbox_watcher escalation | 重複? |
|---|:---:|:---:|:---:|:---:|
| 駆動層 | GUI/Desktop (pywinauto, Windows) | message (inbox YAML / pc_handshake) | TUI session (tmux) | 異層 |
| 宛先範囲 | 副院長 claude.ai Desktop chat **単一** | **全方向 全 agent pair** | 受領側 session 単位 | 異 scope |
| 駆動対象 | chat window 文字入力 (turn 進行) | message 受領 ack 確認 + 再投函 | session wake (nudge/clear) | 非重複 |
| cron/SLA 検知 | fukuincho_watch 継承 (新 poller 不新設) | 送信後 SLA poll (新 loop 不新設) | unread age (PHASE1/2) | ▲ 概念共通のみ |
| ack/retry | window title 変化検知 + M=3 再送 | read:true / 応答 検知 + 5 回上限再送 | Escape×2 / /clear | ▲ 概念共通のみ |
| dedupe | (window_handle, poke_kind, T_bucket) | (correlation_id, recipient, payload_digest) | — | 非重複 (別 key) |
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

- 全 ack イベント (send / Stage A confirm / Stage B confirm / resend#N / escalate / human-required) を
  構造化 JSON で記録、`correlation_id` を全 leg に貫通させる。
- 再送回数・最終 verdict (confirmed / escalated / human-required) を集計可能に。

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
