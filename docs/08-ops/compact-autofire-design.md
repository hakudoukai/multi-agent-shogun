# /compact 自動発火 設計案 (L2.5 — Context Hygiene 拡張)

- task_id: `subtask_thirdpc_compact_autofire_enter_restart_design_d1065911`
- author: ashigaru-third-1 (§0-8 本体)
- addendum: ashigaru-third-2 (§9, 2026-07-11 — task_id `subtask_thirdpc_p4_compact_autofire_a3_2_20260711`、fable5_guard/seq119254 整合)
- base_commit: `6faedb7904ddbb3d6cf6a0d92e890ec9d19963a9`
- status: 設計のみ (watcher/script 実装は 0 行、本 doc 承認後の別タスクで実施)
- 提出先: gunshi-third (G1 監査) / shogun-third,karo-third (path+sha 報告)

## 0. 位置づけ (CLAUDE.md「Context Hygiene 三層機構」との関係)

CLAUDE.md 記載の既存三層 (L1 built-in auto-compact / L2 `context_usage_warn.sh` 警告 / L3 運用ルール「次 turn 内に /compact 入力」) の**間**に、本設計が **L2.5 (自動発火層)** を追加する。

| 層 | 実体 | 発火条件 | 動作 | 本設計での扱い |
|---|---|---|---|---|
| L1 | Claude Code 組込 auto-compact | context window 上限接近 (Claude Code 内部判定、非公開) | 自動要約 | ★不変・無効化しない★ (最終 fallback として温存、副院長令既定通り) |
| L2 | `scripts/checks/context_usage_warn.sh` (UserPromptSubmit hook) | jsonl size ≥ WARN_BYTES(1.6MB)/DANGER_BYTES(2.0MB) | stderr に `context_warn`/`context_danger` 出力のみ、非ブロッキング | ★不変★。本設計は同じ閾値定数を re-export して再利用するのみで、hook 自体は 1 行も変更しない |
| **L2.5 (新設)** | `compact_autofire_watchdog.sh` (enter_restart 系 thin wrapper + 共通 core、本設計) | L2 と同一 jsonl size 閾値 (DANGER_BYTES) **かつ** 対象 pane が idle **かつ** 誤発火防止ガード全通過 | pane に `/compact` をテキスト送信 + Enter (頭手分離) | ★新規 (本 doc の対象)★ |
| L3 | 運用ルール (CLAUDE.md 記載の人間/エージェント手動対応) | L2 警告を agent 自身が stderr で目視 | agent が次 turn 内に自分で `/compact` 入力 | ★不変★。L2.5 が何らかの理由 (対象外 agent・busy 継続・watchdog 停止等) で発火できなかった場合の fallback として温存 |

**整合の要点**: L2.5 は L2 の「発火閾値の定数」をそのまま再輸入する (別閾値を新設しない = FKI-NO-DUP)。L2.5 が成功発火しても L2 hook 自体は毎 turn 変わらず動作し続ける (無効化不要、警告と自動対応は独立に共存可能)。L2.5 が guard 条件で発火を見送った場合は L3 (人間/agent 自身の目視 /compact) が唯一の残存経路になる — つまり L2.5 は L3 を「代替」するのではなく「先回りして肩代わりする」設計であり、L2.5 の undershoot は L3 で必ず吸収される。L1 は常にどの層とも独立した最終防波堤。

## 1. Trigger 設計 (発火条件・閾値)

### 1.1 検討した 2 方式

| 方式 | 概要 | 採否 |
|---|---|---|
| (a) handshake topic 方式 | agent 側 hook (例: PostToolUse) が jsonl size 超過を検知した瞬間に `pc_handshake` へ `compact_request` topic を INSERT し、watchdog がそれを poll して即応答 | ★不採用 (将来拡張として temperature-hold)★ |
| (b) context_data flag (poll) 方式 | 既存 enter_restart 系と同じ「watchdog が周期的に外部状態を自分で読みに行く」方式。jsonl ファイルサイズを `context_usage_warn.sh` と同一ロジックで直接 stat し、閾値超過を watchdog 自身が判定 | ★採用★ |

**採用理由 (b)**:
1. enter_restart 系は既に「systemd timer 駆動・外部プロセスが周期的に pane/DB 状態を読む」アーキテクチャを確立済み (`enter_restart_common_watchdog.sh` の 8-step 構造)。(b) はこの資産をそのまま横展開でき、新規 hook 種別 (PostToolUse 等) をセッション内プロセスに追加する必要がない。
2. (a) は agent 自身のセッション内 hook 実行に依存するため、セッションが hang/停止している最悪ケース (compact が最も必要なケース) でこそ発火できない懸念がある。(b) は agent プロセスの生死と独立した外部監視のため、この弱点がない。
3. 新規 DB topic / enum 追加が不要 (ALL-SSH-NO-NEW-ENDPOINT-01 / FKI-CANON-GUARDIAN-01 の「新設は正本管理者の検証印必須」を避けられ、D-lane 承認コストがかからない)。

(a) は「即時性が (b) の polling cadence より高い」利点があるため、実装フェーズで (b) の cadence (後述 1.3) が不十分と判明した場合の追加拡張として設計メモに残す (本 doc では実装しない)。

### 1.2 閾値 (FKI-NO-DUP: 新定数を作らず L2 の定数を再利用)

`context_usage_warn.sh` が既に定義している 2 閾値をそのまま re-export して使う。新しい閾値定数は作らない。

```
COMPACT_AUTOFIRE_TRIGGER_BYTES = ${CONTEXT_DANGER_BYTES:-2000000}   # L2 の DANGER threshold と同一
```

DANGER (2.0MB / ~95%) 到達時のみ発火対象とする。WARN (1.6MB / ~80%) では発火しない — 早すぎる自動介入で作業中断コストを増やさないため (L3 の「stderr 目視して自分で判断」余地を WARN 帯では残す)。

### 1.3 Polling cadence

enter_restart 系と同一の systemd timer 駆動想定 (例: 5分毎)。既存 `ER_THRESHOLD_MIN` 相当の考え方は流用しない (enter_restart の「idle 経過時間」閾値とは意味が異なるため、`COMPACT_AUTOFIRE_POLL_INTERVAL_MIN` として独立定義、default 5min)。

## 2. 誤発火防止設計 (★必須★ — busy pane への注入禁止)

`/compact` は「テキスト入力を伴うコマンド送信」であるため、enter_restart (Enter のみ) より一段階リスクが高い。既存の `inbox_watcher.sh` の `send_context_reset()` (=最も近い先例: `/clear`/`/new` という別のテキストコマンドを busy-safe に送る既存実装) のガード構成をそのまま流用する。

### 2.1 発火前チェックリスト (全て AND、1 つでも不通過なら発火せず次 cycle へ deferred)

| # | ガード | 実体 (再利用元) | 目的 |
|---|---|---|---|
| 1 | `agent_is_busy() == false` | `inbox_watcher.sh` の `agent_is_busy()` (idle-flag file `${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}` 存在チェック、claude CLI 前提) | mid-turn の agent に注入しない (fc3a5b0b RC-1 と同型の再発防止) |
| 2 | `is_user_typing() == false` | `inbox_watcher.sh` の `is_user_typing()` (capture-pane 末尾行 `❯` 判定) | 人間が pane を直接操作中に横入りしない |
| 3 | border-anchored prompt line が空 | `enter_restart_common_watchdog.sh` Step5 の label-match strict ロジック (境界線直後の `❯`/`│ >` 行のみを真の入力欄と見なす、NBSP 正規化込み) | 入力欄に既に未送信テキストがある状態を「空」と誤認しない (cycle4/5/5c regression の再発防止) |
| 4 | 対象 agent が `is_no_auto_clear_agent()` 型の除外対象でない、または明示的に `COMPACT_AUTOFIRE_TARGET_AGENTS` allowlist に含まれる | `inbox_watcher.sh` の `is_no_auto_clear_agent()` (prefix-match、fc3a5b0b RC-2 型対応) | 対象 pane 制約の明記 (下記 2.2 参照) |
| 5 | `LAST_CLEAR_TS` cooldown 非活性 (直近 `/clear`/`/new` 送信直後でない) | `inbox_watcher.sh` の `send_context_reset()` の cooldown 変数 | `/clear` と `/compact` の二重注入競合を避ける |
| 6 | fire-cap 未超過 (`FIRE_CAP_COUNT` 回 / `FIRE_CAP_WINDOW_MIN` 分以内) | `enter_restart_common_watchdog.sh` の fires.log 方式 (epoch タイムスタンプ per line) | 暴走発火防止 (2026-05-05 SecondPC 事故の直接教訓) |
| 7 | CLI type が `claude` (idle-flag 方式に対応する CLI) であること | `inbox_watcher.sh` の `get_effective_cli_type()` 相当の既存分岐 | codex/copilot/kimi は別の busy 判定・別のリセットコマンド体系のため本設計のスコープ外 (将来拡張) |

### 2.2 対象 pane 制約 (「/clear の no-auto-clear 境界」との異同を明記)

- **/clear (既存)**: shogun/karo/gunshi/相談役等の「状態保持型・司令塔層」agent は `is_no_auto_clear_agent()` により**完全除外** — /clear は persona・会話文脈を全消去する破壊的操作のため。
- **/compact (本設計)**: `/compact` は要約であり persona・進行中タスクの認識は保持される (会話を破棄しない)。CLAUDE.md の Context Hygiene L3 運用ルールは「全エージェント」に課されている (shogun/karo/gunshi も含め、stderr 警告を見たら自分で /compact する義務がある) ため、L2.5 の対象母集団も**同じ「全エージェント」**とする。/clear のような役職除外リストは設けない。
- ただし 2.1-#7 により、CLI type が claude 系でない agent (codex/copilot/kimi) は本設計の対象外 (busy 判定方式が異なるため)。
- allowlist ではなく **denylist 方式は採らない** — 誤って新規 agent が追加された際に「デフォルトで対象外」になる (fail-safe 側に倒す) よう、対象は `COMPACT_AUTOFIRE_TARGET_AGENTS`（明示的 allowlist、claude CLI agent 一覧を enter_restart のデプロイ済み pane 一覧から初期化）とする。新規 pane を対象に加える際は明示的にリストへ追記が必要 (ALL-SSH-NO-NEW-ENDPOINT-01 と同じ「新設は明示登録」思想を踏襲)。

## 3. 頭手分離 (enter_send) 設計

`/compact` はテキストを伴うため、enter_restart (Enter のみ 1 回) では対応できない。既存の `inbox_watcher.sh` 汎用コマンド送信ブロック (`send_cli_command` 相当、および `send_context_reset()` の `/clear`/`/new` 送信パターン) をそのまま流用する。

### 3.1 送信シーケンス (既存パターンの再利用)

1. `C-c` を先に送信 (入力欄に残存するゴミ入力をクリア。既存コードでも `/clear`/`/new` 送信前に同様の前処理がある)
2. コマンドテキスト `/compact` を送信 (Enter は同時に押さない — 頭手分離)
3. `sleep` (既存の CLI 別ギャップ: `/clear`/`/new` は 1.0s、それ以外は 0.3s。`/compact` は `/clear`/`/new` と同種の「UI 遷移を伴うスラッシュコマンド」のため **1.0s ギャップを採用**)
4. Enter (`C-m`) を**別の** `tmux send-keys` 呼び出しで送信 (text と Enter を同一コマンドに混ぜない — 既存規約と同一)
5. 送信直後に idle-flag を invalidate: `rm -f "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}"` (「Fix A canary」と同一パターン。直前サイクルの stale idle-flag を誤って再利用しない)
6. `/clear` 同様に追加の `sleep 3` を入れ、要約処理中に次サイクルが誤って多重発火しないバッファを確保 (fire-cap と二重の安全策)

### 3.2 新規要素 (Anti-Dup: ここが唯一の「新規ロジック」)

既存の `send_context_reset()` は CLI type ごとに固定コマンド (`/clear` or `/new`) を選択する分岐を持つが、`/compact` は claude CLI 固定 (2.1-#7 によりスコープが claude CLI のみのため分岐不要)。よって新規に書くのは:
- `/compact` という固定テキストを送るという 1 行の差分のみ。
- 送信シーケンス自体 (C-c→text→sleep→Enter→idle-flag invalidate→追加 sleep) は 100% 既存パターンの再利用。

## 4. Anti-Dup 表 (流用範囲 vs 新規範囲)

| 要素 | 由来 | 流用/新規 |
|---|---|---|
| 8-step cycle 構造 (fire-cap halt→pane存在確認→DB経過時間クエリ→pane capture+NBSP正規化→idle閾値判定→border-anchored label-match→条件付発火→dual audit INSERT) | `enter_restart_common_watchdog.sh` | ★流用 (骨格そのまま)★。「idle 閾値判定」ステップは本設計では「jsonl size 閾値判定」に置換 (中身のみ差し替え、構造は同一) |
| fire-cap レート制限 (`ER_FIRE_CAP_COUNT`/`ER_FIRE_CAP_WINDOW_MIN`、fires.log epoch方式) | 同上 | ★流用 (そのまま)★ |
| dual audit trail (`shireiko_audit_log` + `pc_handshake` heartbeat 両方 INSERT、judgment_level 整数、result enum) | 同上 | ★流用 (event_type/engine 名のみ `compact_autofire_*` に変更)★ |
| 安全な Python heredoc (`os.environ`+`json.dumps`、`urllib.parse.urlencode`) | 同上 | ★流用 (そのまま、新規 DB 書込みにも同一パターン適用)★ |
| border-anchored label-match (NBSP正規化込み) | 同上 | ★流用 (そのまま、guard #3 として) |
| `agent_is_busy()` / `is_user_typing()` / `pane_is_active()` / `session_has_client()` | `inbox_watcher.sh` | ★流用 (そのまま呼び出し)★ |
| `is_no_auto_clear_agent()` の prefix-match 手法 | 同上 | ★流用 (思想のみ — 本設計では denylist でなく allowlist に反転適用、§2.2 参照)★ |
| 頭手分離送信シーケンス (C-c→text→sleep→Enter→idle-flag invalidate) | 同上 (`send_context_reset()`) | ★流用 (そのまま)★ |
| WARN_BYTES/DANGER_BYTES 閾値定数 | `context_usage_warn.sh` | ★流用 (re-export、新規定数を作らない)★ |
| `/compact` という送信テキスト自体、CLI-type-claude-only スコープ限定、`COMPACT_AUTOFIRE_TARGET_AGENTS` allowlist、event_type/engine 名の命名 | (本設計) | ★新規 (唯一の差分)★ |

**結論**: 新規に書くコードは「既存 8-step 構造への envvar/定数注入 + `/compact` 固定テキスト送信 1 箇所」のみであり、per-role thin wrapper (`compact_autofire_<role>_watchdog.sh`) + 共通 core への微小 diff (もしくは既存 `enter_restart_common_watchdog.sh` へのモード分岐追加) という enter_restart と全く同型の「thin wrapper + shared core」構成を維持する。実装フェーズでは新規 shared core ファイルを作るか、既存 core にモードフラグ (`ER_MODE=enter_only|compact_text`) を追加するかの 2 択になるが、いずれも本 doc の責務外 (実装タスクで決定)。

## 5. Watcher Design Principles (6原則) 整合表

| # | 原則 | 本設計での担保 |
|---|---|---|
| 1 | 無限retryループ禁止 (retry-cap/dead-letter/TTL) | fire-cap (§2.1-#6) がそのまま retry-cap の役割を果たす。DANGER閾値を下回るまで(=/compact成功で jsonl size相当のcontext使用量が下がるまで)発火対象から自然に外れるため、TTL的な自然終了性を持つ |
| 2 | self-send (`from_pc==to_pc`) 即ack | 本設計は pc_handshake heartbeat を `enter_restart` と同じ from_pc/to_pc 規約で送るのみで、self-send ループは発生しない (既存パターンの継承) |
| 3 | 手動停止フラグ尊重 | `enter_restart` 系の HALT ログ機構 (fire-cap 超過時の自己停止) をそのまま継承。加えて `~/.openclaw/global_disable` 相当の手動停止フラグを本設計でも `COMPACT_AUTOFIRE_DISABLE` フラグファイルとして新設予定 (実装時、既存 disable-flag 規約に倣う) |
| 4 | message_id dedupe | 本設計はメッセージ配送系ではなく pane 直接注入系のため直接該当しないが、fires.log による「直近発火時刻」記録が事実上の dedupe (同一 agent への短時間重複発火防止) として機能する |
| 5 | idempotency (cross-PC操作の重複耐性) | `/compact` 自体が要約という冪等に近い操作 (再度打っても状態が壊れない) であり、誤って連続発火しても enter_restart の Enter 連打と同程度の安全性を持つ。fire-cap が主たる保護層 |
| 6 | 専用テーブル分離 (heartbeat) | 既存 `pc_handshake` heartbeat 経路をそのまま再利用 (専用テーブルは既に enter_restart で分離済み、新設不要) |

## 6. /clear統治規則 v1.0 との整合表

出典: 正本は Supabase `project_documents` (canon id `5dcf2302`)。本リポジトリにはローカルファイルとして存在しないため、永続 memory (`clear-command-governance-rule-v1-and-canonical-watcher-already-guarded`) に記録された要約 — 「queued /clear は Enter せず Up/C-u で除去。本 repo watcher は busy guard + advisor 除外を実装済」— を引用元として整合を取る。実装フェーズで Supabase 直接参照による一次ソース確認を推奨 (本 doc は設計時点の二次引用に留める旨を明記)。

| 統治規則の原則 (要約引用) | 本設計での整合 |
|---|---|
| queued な `/clear` は Enter を押さず、Up/C-u で除去する (誤発火の巻き戻し) | `/compact` は誤って queue された場合も同種の Up/C-u 除去操作で巻き戻し可能な設計とする (テキストコマンドである以上、Enter前ならterminal入力欄から除去可能なため、/clear と同じ復旧手段が適用できる) |
| busy guard を実装済であること | §2.1-#1/#2/#3 のガード構成がこれに対応 (`agent_is_busy()`＋`is_user_typing()`＋border-anchored prompt判定の三重チェック) |
| advisor (相談役等) 除外を実装済であること | §2.2 で「全エージェント対象、ただし claude CLI 限定 + allowlist 明示登録制」とし、相談役 (Hermes 等、非 claude CLI) は §2.1-#7 により自動的にスコープ外となる |

## 7. Test / Harness 計画 (設計レベル、実装は別タスク)

実装フェーズで以下を検証する (enter_restart の smoke test 資産流用を想定):

1. **Dry-run mode**: `COMPACT_AUTOFIRE_DRY_RUN=1` で実際の send-keys を行わず、判定結果 (fire would occur / deferred + 理由) のみログ出力するモードを用意し、まず dry-run で 1 サイクル以上の実測を取る (enter_restart cycle1-2 で採った手法と同型)。
2. **Busy pane 誤発火 negative test**: agent が明示的に busy (idle-flag 不在) な状態を人工的に作り、fire しないことを確認 (guard #1 の単体検証)。
3. **人間 typing 中 negative test**: pane に `❯` プレフィックス付きの未送信テキストを人工投入し、fire しないことを確認 (guard #2/#3 の単体検証)。
4. **fire-cap 検証**: 短時間窓内に閾値超過状態を人工的に維持し、`FIRE_CAP_COUNT` 到達で HALT することを確認。
5. **頭手分離 injection 順序検証**: tmux capture-pane で実際に `/compact` テキストが単独送信された後に Enter が別イベントとして送信されていることをログタイムスタンプで確認 (テキストと Enter が同一 send-keys 呼び出しに混在していないことの回帰防止)。
6. **idle-flag invalidate 検証**: 発火直後に idle-flag ファイルが削除され、次サイクルで stale idle と誤判定しないことを確認 (「Fix A canary」と同型の回帰テスト)。
7. **dual audit trail 検証**: 発火 (成功/deferred 両方) が `shireiko_audit_log` と `pc_handshake` の両方に正しい judgment_level (整数) / result enum で記録されることを確認。
8. **Dual Green ゲート**: 本 doc の gunshi-third G1 監査 PASS + 第二監査者 (Codex/Hermes、Gemini経路は廃止済) PASS の両方が揃って初めて実装タスクに着手可能とする (本タスクの `done_when` 明記の Dual Green 要件に対応)。

## 8. 未解決事項・実装時の決定事項 (本 doc の範囲外)

- shared core を新規ファイルにするか、既存 `enter_restart_common_watchdog.sh` へモード分岐追加するかは実装フェーズで決定。
- `COMPACT_AUTOFIRE_TARGET_AGENTS` allowlist の初期値 (どの pane から展開するか) は実装フェーズで shogun-third/karo-third 等の deployment 状況を踏まえて決定。
- `/clear統治規則 v1.0` の一次ソース (Supabase project_documents id=5dcf2302) 直接参照による本 doc 記載内容の correction は、実装着手前に一度確認することを推奨。
- **★§9.3 Deployment gate の判定・記録主体 (2026-07-12 redo 追記／2026-07-14 redo2 追記)★**: 「fable5_guard 引退確認済み (gate b)」の判定は Commander/karo が行い、pc_handshake 等へ記録する運用とする想定だが、判定タイミング・記録先 topic・判定権限者の確定は実装着手前に別途決定する (本 addendum は設計方針のみ提示、運用フロー確定は範囲外)。gate (a) (host をまたぐ単一 coordination namespace/単一注入 owner) は本 addendum の host-local lock 設計では原理的に未達であり、判定主体を決めても現行構成では成立しない — (a) を将来満たす場合は cross-host coordination の新規設計 (次項) が前提となる。
- **cross-host injector 拡張時の coordination 経路**: §9.3.1 で示した通り、compact-autofire を将来 cross-host 注入へ拡張する場合は filesystem lock から DB 経由調整へ切り替える必要があるが、その具体設計 (どのテーブル/topic を使うか) は本 addendum の範囲外・別 task とする。

---

## 9. fable5_guard (pc_handshake seq=119254) との整合 — 複数 pane-injection watchdog 間の排他設計 (a3-2 追補, 2026-07-11)

- addendum task_id: `subtask_thirdpc_p4_compact_autofire_a3_2_20260711` / tracker `d1065911`
- 契機: karo-third clear_command (2026-07-11T22:47:06)「既存機構(enter_restart/context_warn/fable5_guard seq119254)実査先行・整合」指示
- 本 addendum は §0-8 (ashigaru-third-1 稿、base_commit `6faedb7`) を一切変更せず追記のみ (Anti-Dup / 正本保全)。実装は依然 0 行、本 §9 も設計・PROPOSE-ONLY。

### 9.1 fable5_guard.sh の実体 (実査結果)

- 実体 = `scripts/fable5_guard.sh` (71行、cron駆動)。理事長令 2026-07-11 の日付ゲート式フェーズ切替: 〜07-12=claude-fable-5 固定、07-13〜14=claude-opus-4-8 復帰、07-15〜=no-op 自動引退。
- 対象 = 8 pane (third local 2 + second/main/mac 各2 を SSH 経由): `shogun-third:0.0` / `multiagent-third:0.0` / `shogun-second:0.0` / `multiagent-second:0.0` / `shogun-main:0.0` / `multiagent-main:0.0` / `shogun-mac:0.0` / `multiagent-mac:0.0`。★本設計 §2.2 の `COMPACT_AUTOFIRE_TARGET_AGENTS` 想定 pane 群 (shogun/karo 系) と重複する★。
- 動作: busy判定 (`esc to interrupt` の capture-pane grep のみ) → `/model <target>` を `-l` (リテラル) text送信 → `sleep 1` → Enter → `sleep 2` 固定 → 確認ダイアログ (`Yes, switch` grep) → 検出時のみ `1` 送信で確定。text/Enter 分離は本設計 §3 と同型の頭手分離だが、busy 判定は `inbox_watcher.sh` の `agent_is_busy()`/idle-flag とは別実装 (独立の capture-pane grep ロジック)。
- 既知バグ (pc_handshake `seq=119254`、2026-07-11 16:35 将軍→Commander報告): ダイアログ確認が `sleep 2` 固定の **one-shot** 判定のため、context 肥大 pane でダイアログ描画が2秒を超えるケースで検出漏れ→ダイアログ wedge が発生。提案修正 = 2秒毎ポーリングを10-12秒まで継続 + 開始前の「既存ダイアログ開状態」pre-check。★本提案は Commander/cron 管轄下で PROPOSED ONLY・third_pc worker 権限外・未実装★ (本 addendum もこの実装状況を変更しない)。

### 9.2 整合点 — 「同一 pane への複数独立 cron watchdog による同時注入」という共通リスクパターン

fable5_guard (モデル切替注入) と本設計の compact-autofire watchdog (`/compact` 注入) は、① 同一 pane 群を対象、② 各々が独立 cron/timer 駆動、③ 各々が text+Enter 分離送信、という3点で構造が同型。両者が同一 pane へほぼ同時刻に発火した場合、`tmux send-keys` の物理的競合 (一方の text 送出中にもう一方の Enter が割り込む等) により、入力欄に想定外の複合文字列が入る「二重注入コリジョン」が理論的に起こりうる。

既存 enter_restart 系 (および本設計 §2.1 の fire-cap) は**自分自身のレート制限のみ**で排他しており、**他 watchdog (fable5_guard) との相互排他は設計されていない**。この整合ギャップが今回 karo の「整合要」指示の核心と判断する。

fable5_guard は 2026-07-15 以降 no-op 自動引退の時限措置 (理事長令) のため、本設計の実装着手時期次第では実運用競合窓口は限定的。ただし**同型の複数 watchdog 併存は今後も再発しうるパターン**(将来別の cron guard が同じ pane 群を対象にする可能性) であるため、個別回避でなく汎用の排他規約を提案する。

### 9.3 提案: pane 注入排他規約 (gunshi-third G1 REDO 反映、2026-07-12 改訂 — 片側実装は排他完成と扱わない／2026-07-14 redo2 改訂 — host-local lock の並行採用だけでは gate(a) 不成立と明記)

**★redo 反映の核心 (G1-PANE-LOCK-BILATERAL-001 blocker 対応)★**: 9.3(旧稿) は compact-autofire 側だけがロックを取得する設計だったが、現行 `fable5_guard.sh` は同ロックを一切見ないため、compact-autofire 稼働中に fable5_guard が無条件に send-keys してしまい相互排他が成立しない。よって guard #8 を「compact-autofire 単独の自己防御」ではなく「同一 pane 群を対象とする全 injector が従うべき共通契約」として再定義し、片側実装のみでの enable を明示的に禁止する。

1. **注入直前ロックディレクトリ方式 (契約の中身は変更なし)**: `/tmp/pane_inject_lock_<canonical_key>` (`mkdir` の atomicity をロック代わりに使用)。injector は注入シーケンス開始 (C-c 送信) 直前に取得し、シーケンス完了 (§3.1 手順6の追加 sleep 後) まで保持、`trap EXIT` で確実に `rmdir` する。ロック取得失敗時は当該 pane を本 cycle skip → 次 cycle deferred (§2.1 の既存フローに合流、guard #8)。
2. **★Deployment gate (redo2 改訂 — G1-PANE-LOCK-NAMESPACE-002 blocker 対応、2026-07-14)★**: compact-autofire watchdog は、以下のいずれかが満たされるまで `enable` してはならない (design doc レベルの必須前提条件として明記。実装フェーズでの deploy checklist 項目とする):
   - (a) 同一 pane 群 (§2.2 `COMPACT_AUTOFIRE_TARGET_AGENTS` と fable5_guard §9.1 の対象 8 pane の重複範囲) を対象とする**全ての** injector (fable5_guard 含む) が、**同一の coordination namespace を共有する単一のロック実体 (単一注入 owner)** の下で調停されていることを Commander/karo が確認・記録する。★「各 injector が独立に本 §9.3 のロック契約を採用済み」であるだけでは (a) は成立しない★ — fable5_guard は中央 (Commander/cron) ホストから SSH 経由で remote pane へ注入し、compact-autofire は対象 pane と同一ホストで動く (§9.3.1 参照) ため、`/tmp` ロックは host-local であり、双方が「契約に従って」各自のホストでロックを取得しても、それらは物理的に別々のロックであり互いを見ない。結果として両者は各自「安全に取得できた」と誤認したまま同一 pane へ二重注入しうる。ゆえに (a) を満たすには、host をまたいで単一の判定主体になる仕組み (例: 単一ホストが全 injector を代表して注入する集中実行、または §9.3.1 で範囲外とした DB 経由調整 (`pc_handshake`/`shireiko_audit_log`) 等の cross-host 可視な coordination) が必須であり、host-local filesystem lock の並行採用だけでは不十分と明記する。
   - (b) fable5_guard が理事長令の日付ゲートにより no-op 自動引退 (2026-07-15 以降) した状態を Commander が確認する (この場合ロック相手が実質不在になるため単独稼働で安全)。
   - **★現行構成の帰結★**: 本 addendum が採用する filesystem lock (§9.3.1) は host-local である以上、fable5_guard (中央ホスト→remote 注入) と compact-autofire (対象と同一ホスト注入) が併存する現行構成では **(a) は原理的に達成不能**。したがって現時点で安全な enable 経路は **実質 (b) の fable5_guard 引退確認のみ** であると明記する。(a) を実際に満たしたい場合は host-local lock の運用ではなく cross-host coordination の新規設計が前提となり、それは本 addendum の scope_out (§9.3.1 injector 実行場所の方針決定、末尾の cross-host injector 拡張時の別 task 化方針) と一致する。
   - (a)(b) いずれも未達の間 (現状 2026-07-14 = fable5_guard 稼働中 かつ (a) は上記の通り現行構成で原理的に未達) は、compact-autofire 実装が完了していても **enable 禁止 (PROPOSE-ONLY のまま)**。この gate 判定は本 addendum の scope_out (deploy) と重複しないよう、「実装タスクの done_when」ではなく「実装完了後・deploy 前」の独立ゲートとして §8 未解決事項にも追記する。
3. **fable5_guard 側の改修は本設計の範囲外** (third_pc worker 権限外・Commander/cron 管轄)。本 addendum は fable5_guard 自体の書き換えを提案せず、「同じロック規約に相乗り可能な軽量な取り決め」として Commander への申し送り事項に留める (fable5_guard 側へのロック採用は別task起票・karo/Commander判断)。ただし上記 2. の gate により、fable5_guard 側が未採用のままでは compact-autofire 側も enable できないため、この申し送りは「推奨」ではなく「compact-autofire 稼働の前提条件」に格上げする。
4. ロック規約自体は新規 DB テーブル/新規 topic を要さない (ファイルシステムのみ) ため、ALL-SSH-NO-NEW-ENDPOINT-01 / FKI-CANON-GUARDIAN-01 の「新設は正本管理者の検証印必須」の対象外と判断する (この判断は変更なし)。

#### 9.3.1 ロック lifecycle (G1-PANE-LOCK-LIFECYCLE-001 major 対応 — owner metadata / stale 回収 / canonical key / cross-host)

- **owner metadata**: `mkdir` 成功直後、ロックディレクトリ内に `owner.yaml` を書き込む (mkdir 自体が atomicity の担保、metadata 書き込みは mkdir 後の非競合領域)。必須フィールド: `pid` (injector プロセスの PID)、`actor_host` (injector を実行しているホスト。fable5_guard は Commander/cron ホストから SSH 経由で複数 PC の pane へ注入するため、注入元と注入先ホストが一致しない構成があり得る)、`target_pc_id` (注入先 pane が属する PC 識別子。§18 配置表の PC 単位: main_pc/second_pc/third_pc/mac)、`target_pane` (完全 pane id、例 `shogun-third:0.0`)、`acquired_at` (ISO8601 UTC)。
- **canonical key の再定義**: 旧稿の `<pane_sanitized>` は pane 名のみで sanitize していたため、異なる PC 上の同名 pane (例: `shogun-third:0.0` と、将来 mac 側に同名構成が出来た場合の `shogun-mac:0.0` が誤って同一 sanitized 文字列に縮退するケース等) を区別できない欠陥があった。canonical key = `<target_pc_id>__<target_pane_sanitized>` (例 `third_pc__shogun-third_0.0`) とし、PC 境界を key に必ず含める。sanitize 規則 = pane id 中の `:`/`.`/`/` を `_` へ置換、他文字は変更しない (正規化の衝突余地を最小化)。
- **owner metadata 未完成窓の fail-closed 規則 (redo2 追加 — G1-LOCK-METADATA-RACE-002 対応)**: `mkdir` 成功から `owner.yaml` 書き込み完了までの間 (非競合領域だが有限の窓が存在する) に他 injector が同一ロックディレクトリを検分した場合、`owner.yaml` が存在しない/読み取り不能/必須フィールド欠落のいずれであっても、それを stale ロックとして即時回収してはならない。この窓を検知した injector は **owner 不明 (unknown owner) として fail-closed** — 当該 pane を本 cycle skip → 次 cycle deferred (§2.1 の既存フローに合流) とし、`STALE_THRESHOLD_SEC` の判定対象にも入れない。owner metadata が確定(書き込み完了)して初めて、以降の stale 判定ロジックの対象になる。
- **stale 回収規則**: 通常の注入シーケンス最長想定時間 (§3.1 手順 + §9.4 の追加 sleep 込みで概算 10 秒程度) に安全マージンを載せた `STALE_THRESHOLD_SEC` (実装フェーズで確定、目安 60 秒) を超えて `acquired_at` から経過し、かつ owner metadata が確定済みのロックのみを stale 判定の対象とする (未確定窓は上記 fail-closed 規則が優先)。
  - **同一ホスト上の判定** (`actor_host` == 回収を試みる watchdog 実行ホスト): `owner.yaml` の `pid` が生存していなければ即時 stale 確定・強制 `rmdir` 可 (SIGKILL/クラッシュでロックプロセスが trap EXIT を実行できずに死亡したケースをカバー)。
  - **cross-host の判定 (redo2 改訂 — G1-CROSSHOST-STALE-WORDING-002 対応、文言統一)** (`actor_host` != 回収を試みるホスト、または `actor_host` へ liveness 確認する経路がない): PID liveness を直接確認できないため、`STALE_THRESHOLD_SEC` の経過のみでは **「stale 確定」ではなく「stale 候補」に留まる** と明記する (タイムスタンプ超過だけでは相手ホストのプロセス死活を確認できず、確定的な stale 判定の根拠にならないため)。stale 候補を検知した injector は **自動 `rmdir` (自動回収) を一切実行してはならない** — Commander へ pc_handshake で通知し、人手確認・人手回収を経てのみロックを解除する。cross-host 自動回収を「デフォルト無効・実装フェーズの追加判断事項」とする旧稿の位置づけは撤回し、**cross-host stale 候補の自動回収は本設計として恒久的に禁止**と明記する (実装フェーズでの緩和判断も本 addendum の scope 外・別途正本改訂が必要)。
- **injector 実行場所の方針決定 (新設)**: fable5_guard は Commander/cron ホストから SSH 経由で 4 PC 8 pane へ注入する構成のため、`/tmp` ロックはホストローカルであり cross-host 注入には自然には共有されない。本設計は以下を採用する: **compact-autofire watchdog は対象 pane と同一ホスト上で実行する構成のみを前提とする** (§2.2 の対象が shogun-third/karo-third 等 third_pc ローカル pane である現行想定と整合、FKI-NO-DUP=新規 cross-host coordination channel を作らない方針にも合致)。将来 compact-autofire を SSH 経由の cross-host injector として拡張する場合は、filesystem lock ではなく既存の DB 経由調整経路 (`pc_handshake` / `shireiko_audit_log`) を使う設計に切り替える必要があり、これは本 addendum の範囲外・別 task として明記する。
- **collision 正規化テスト**: 実装フェーズで、上記 canonical key 生成関数に対し (a) 同名 pane・異なる `target_pc_id` が異なる key を生成すること、(b) 同一 pane id の異なる表記揺れ (あれば) が同一 key に正規化されること、の単体テストを §7 に追加する (下記 §7 test 11 参照)。
- **ロック配置パス (G1-FABLE-LINE-DRIFT-001と別のcaveat G1-LOCK-PATH-001 反映)**: 旧稿は予測可能な `/tmp` 直下パスを採用していたが、G1 caveat (medium) を受け、実装フェーズでは各 PC の権限分離された既存 runtime directory (例: エージェント専用の既存作業ディレクトリ、または `XDG_RUNTIME_DIR` 相当) の利用を優先検討することを推奨事項として明記する。`/tmp` 直下は他プロセスからの推測・衝突・権限混在のリスクがあるため、実装フェーズで既存の類似運用 (idle-flag ファイル等) がどの directory 規約を採用しているかを ALL-SEARCH-BEFORE-CREATE で確認し、可能な限りそれに合わせる (新規 directory 規約を追加で作らない = FKI-NO-DUP)。

### 9.4 fable5_guard の one-shot ダイアログ確認バグからの教訓の再輸入

seq119254 の根本原因 (「`sleep 2` 固定 → one-shot grep」が context 肥大 pane の UI 描画遅延に弱い) は、本設計 §2.1 guard#3 (border-anchored label-match) および §3.1 手順6 (追加 `sleep 3`) と同種のリスク領域である。本設計は元々 enter_restart 系の「境界行判定 + 固定 sleep」パターンを流用しているため、**fable5_guard と同じ弱点 (固定 sleep 起因の UI 描画遅延見逃し) を継承しうる**。よって §7 Test/Harness 計画に以下を追加する:

9. **UI 描画遅延 negative test (fable5_guard seq119254 教訓の輸入)**: context 肥大 pane (jsonl サイズが DANGER 閾値付近) に対して意図的な描画遅延を模擬し、固定 sleep 一発判定でなく必要ならポーリング化 (fable5_guard 提案と同型) を検討する。§3.1 手順6の追加 `sleep 3` は暫定緩和であり、実装フェーズで fable5_guard 側修正 (実装されていれば) とパターンを揃え、同一のポーリングヘルパー関数を共有できないか検討する (重複実装回避)。
10. **ロック SIGTERM/SIGKILL negative test (G1-PANE-LOCK-LIFECYCLE-001 対応)**: injector プロセスをロック保持中に SIGTERM で正常終了させ `trap EXIT` による `rmdir` を確認、続けて別サイクルで SIGKILL による異常終了 (trap 発火せず) を再現し、§9.3.1 の stale 回収規則 (同一ホスト pid liveness 判定) が `STALE_THRESHOLD_SEC` 経過後に正しくロックを回収し次サイクルで発火可能になることを確認する。
11. **canonical key 衝突 negative test**: 異なる `target_pc_id` を持つ同名 pane (例: `third_pc__shogun-third_0.0` と仮想の `mac__shogun-third_0.0`) が別々の canonical key/ロックディレクトリに正規化され、一方のロック保持が他方の発火を妨げないことを確認する (§9.3.1 canonical key 再定義の回帰防止)。
12. **cross-host stale ロック negative test**: `actor_host` が回収試行ホストと異なるロックを人工的に作成し、`STALE_THRESHOLD_SEC` 経過後も自動 `rmdir` が実行され**ない**こと (§9.3.1 の方針=cross-host は stale 確定でなく stale 候補に留まり、自動回収は恒久禁止) を確認する。
13. **owner metadata 未完成窓 fail-closed negative test (redo2 追加 — G1-LOCK-METADATA-RACE-002 対応)**: `mkdir` 成功直後・`owner.yaml` 書き込み完了前のタイミングを人工的に再現し (書き込み遅延を模擬)、その窓を検分した別 injector が stale 回収を試みず unknown owner として当該 cycle を skip → 次 cycle deferred すること、および `STALE_THRESHOLD_SEC` の起点計算に未確定ロックが算入されないことを確認する (§9.3.1 owner metadata 未完成窓の fail-closed 規則の回帰防止)。

### 9.5 副院長令3fea6891 / FKI-CONTEXT-CADENCE-01 要件充足の再確認

- 副院長令 `3fea6891` (pc_handshake id、2026-06-10 18:29、decision_code「[P1][副院長→Commander] compact発火経路=裁定」) の指示 — 「恒久形=自動発火・既存 enter_restart エンジン拡張 (FKI-NO-DUP=新規watcher建てない)・頭手分離 (AI=compact_request発信→エンジン=`/compact`+Enter送信)・C-laneタスクとして登録・trigger形式は handshake topic 方式 or context_dataフラグ方式」— は a3-1 本体 §0〜§4 で全て充足済み (既に enter_restart 拡張として設計、頭手分離 §3、trigger 方式は (b) context_data-poll 方式を採用と明記)。本 addendum はこの充足状態を変更しない。
- `FKI-CONTEXT-CADENCE-01` は design_decisions 全文検索 (decision_code/title/description) で**独立の定義 DD は未検出**。別 DD (`FKI-HERMES-UPSTREAM-RELAY-01`, 2026-06-16) 内に「Commander context健全 (FKI-CONTEXT-CADENCE-01) でhub停滞回避」という運用趣旨での言及が1件存在するのみで、これは `3fea6891`の「節目でcompactするcadence」という考え方を指す呼称として使われていると判断する。**正本未検出のためこれを事実として断定しない** (虚偽厳禁遵守)。実装着手前に一次 DD 定義の存在有無を再確認することを推奨事項として残し、a3-1 §8「未解決事項」に合流させる。
