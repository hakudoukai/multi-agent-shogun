# W201: inbox_watcher.sh consume-before-commit 根治 (足軽3号)

- 発令: karo-second msg_20260804_183632_140786c8 (2026-08-04T18:36:32)
  + 追補①msg_20260804_184559_d970f758 (三版sha問題・移植可能性要件)
  + 追補②msg_20260804_185507_f62c10f9 (8項目ヘッダ・新正本id=60d41aee・B-4厳格化)
- 実施: ashigaru3
- 稼働開始時刻 (本工区着手): 2026-08-04T18:36:33 JST (`ps -ef` 実行時刻)
- 本報告 初版完了時刻: 2026-08-04T18:55:23+0900 / 追補反映完了時刻: 2026-08-04T19:05頃 JST

## 開始報告 必須8項目 (追補③・遡及記入)

- **EXISTING_ASSET_CHECK**: `scripts/inbox_watcher.sh` は既存資産そのもの (新規作成ではなく既存欠陥の是正)。同名の別実装は repo 内に存在しない (`find . -iname inbox_watcher.sh` で該当1件のみ)。
- **CANON_CHECK**: CLAUDE.md Watcher Design Principles 節・docs/01-architecture/watcher-design.md のチェックリスト (retry無限ループ禁/self-send即ack/手動停止flag尊重/重複検知/idempotency/専用テーブル分離) を確認済。本修正はこの原則に反しない (idempotency=同一msg_idへの二重 mark_message_processed は no-op、専用ロック=既存 LOCKFILE 機構を再利用のみで新設なし)。
- **ACTIVE_OWNER_CHECK**: `scripts/inbox_watcher.sh` の現行 owner は明示されていないが、17プロセス全稼働中 (家老/足軽/軍師/将軍レーン全域で共有) — ★共有 watcher ゆえ process 停止・再起動は行っていない (境界遵守)★。
- **DUPLICATE_IMPLEMENTATION_RISK**: ★該当あり・三版が実在★ = SecondPC実稼働 sha=6dcfc02c (本工区が修正した対象)・SecondPC別path sha=fe2ed51d (未実測・追補①で存在を知らされたのみ)・third_pc sha=288f455f (委員長殿実測・同一欠陥が別コードで存在)。★本工区は sha=6dcfc02c の一本のみを直接修正し、他二版への移植は行っていない (二重実装禁止・追補①の明示指示通り)★。詳細は下記「移植する者への申し送り」節。
- **SEARCHED_TARGET_COUNT**: `scripts/inbox_watcher.sh` を参照する bats テスト = 9ファイル (grep -l 済)。うち実行可能 = 4ファイル (bats-support/bats-assert 未 vendored のため e2e 系5ファイルは実行不能・環境欠落であり本工区の欠陥ではない)。
- **SEARCH_RESULT_STATE**: `scanned_4_targets_1_new_regression_pattern` — 4ファイル・86アサーションを実走し、2件が「是正の代価」として想定通り FAIL (LB-07/TC-FR-003)、1件が無関係の pre-existing FAIL (T-CRESET-003・`git stash` baseline で再現確認済)。`no_targets_scanned` ではない。
- **KNOWLEDGE_GAP_WARNINGS**: (1) third_pc sha=288f455f の実コードは本工区からは未読 (third_pc 触るな境界のため) — 移植要件④「移植先で当たらぬ場合の見分け方」は構造的記述に留まり、実際の当否は移植者自身の確認が必要。(2) 新正本 id=60d41aee の全文 (5343字) は Supabase 直読が必要だが、ashigaru の tool 権限には Supabase/project_documents への直接アクセス手段が無く (secret 値探索は CLAUDE.md 禁則のため試みず)、★全文は未読・追補メッセージ本文に引用された要旨 (B-4 Return-Path の一文) のみを根拠とした★。全文照合は家老/軍師/将軍等 DB アクセス権限を持つ役職に委ねる。
- **REUSE_OR_INTEGRATION_TARGET**: 既存 `mark_message_processed`/`return_message_to_sender`/`get_unread_info` の構造をそのまま再利用対象として設計 (新規並行実装なし)。移植先2版はこの節の「移植する者への申し送り」を integration target とする。

## 0. 対象 file の実在確認 (第一歩・委員長殿指示遵守)

`ps -ef` で実稼働中の 17 プロセス全てが同一 file を指している事を確認した。

```
実稼働 path = /home/hakudokai/projects/multi-agent-shogun/scripts/inbox_watcher.sh
修正前 sha256 = 6dcfc02c55419e9ada0b159ce7793a7bc7c70f613c8649b6b8db1c0de2eae771 (1554行)
```

★発令書記載の sha256 (`6dcfc02c55419e9a…`) と一致確認済★。委員長殿が先に誤読された
`/home/hakudokai/multi-agent-shogun/scripts/inbox_watcher.sh` (別木・68336 bytes・Jul 14更新)
は本 repo 内に実在するが ★実稼働プロセスはどれも指しておらぬ事★ を `/proc/<pid>/cwd`・
readlink で確認した (ashigaru3 自身の PID 233919 の cwd = `/home/hakudokai/projects/multi-agent-shogun`)。

修正後 sha256 = `6fc62bbe98c8e2003d78de90dbd6cea0f450447c17c73e46142361e25f9668d9`

## 1. 確定した欠陥 (発令書の記述を実コードで検証・一致)

| 発令書の指摘 | 実際の行 (修正前) | 検証結果 |
|---|---|---|
| `get_unread_info()` が抽出した瞬間に `read=True` を打つ | L489-497 | ★確認・一致★ — `if specials or expire_supersede_changed:` ブロックが unread かつ special_types の全メッセージを無条件で `read=True` にし、即 atomic write |
| busy guard が「deferred」と書いて既読を戻さず抜ける | 内側 L559-561 (`send_cli_command`)・外側 L1192-1194 (`process_unread`) | ★確認・一致★ — 外側 guard は `continue` するのみで既読を戻す処理が無い (そもそも上記①で既に読み込み前に既読化済のため「戻す」概念自体が無い)。内側 guard も `return 0` (成功偽装) |
| 次 cycle は既読を二度と拾わぬ | L489 (`unread = [m for m in messages if not m.get("read", False)]`) | ★確認・一致★ |

**根本原因の一言**: `get_unread_info()` は「読み取り専用の集計関数」という体裁でありながら、
実際には special_types を ★抽出と同時に消費 (read=True 確定) ★ していた。呼び出し側
(`process_unread()`) が実行に失敗・延期しても、ファイル上の記録は既に「既読」に確定済で
巻き戻せない。これが consume-before-commit の実体。

## 2. 発注①〜④ の対応 (差分 100行 +14行)

### ①既読は実行成功の後にのみ打て

- `get_unread_info()` から特殊メッセージの `read=True` 確定処理を除去 (期限切れ/supersede の
  自動既読化 `expire_supersede_changed` は元々「実行」を伴わない正当な自動処理のため維持)。
- 新設 `mark_message_processed(msg_id)`: 単一メッセージ id を対象に flock 保護の
  read-modify-write。`process_unread()` の specials ループが `send_cli_command` の
  ★戻り値を見た後にのみ★ 呼び出す。

### ②延期する時は必ず未読へ戻せ・戻せぬなら「延期した」と書くな

- busy guard 2箇所とも「何もしない (continue/return)」に変更 — そもそも①により
  read=True が未確定なので「戻す」操作は不要になった (=消費していないから戻す必要がない、
  という形で②を満たす)。
- `send_cli_command` 内側 busy guard の `return 0` → `return 1` (失敗を偽装しない)。
- ログ文言に `(id=..., left unread)` を追記し、「延期した」と書いた行が実際に未読のままである
  ことを id 付きで裏書きした。

### ③実行できなかった命令は送り主へ返せ

- 新設 `return_message_to_sender(msg_id, msg_from, msg_type, reason)`:
  `inbox_write.sh` 経由で送り主 (`from`) の inbox へ `type: delivery_failed` の通知を書き、
  対象メッセージを `mark_message_processed` で消費 (無限リトライ化を防ぐ)。
  `from` が空の場合はログのみで通知不能を明記 (握り潰さない)。
- 呼び出し箇所2つ: (a) `send_cli_command` が失敗を返した時、(b) `normalize_special_command`
  が空文字列を返した時 (=type/content が不正で送信コマンドを生成できなかった時。従来は
  黙って dropped されていた ★別の隠れた消失経路★ もここで塞いだ)。

### ④live log の所在を突き止めよ

`/proc/<pid>/fd/1`・`/proc/<pid>/fd/2` を実読して判明:

| agent | 実際の live log (fd 1/2 の readlink) | repo 内の想定 log | 一致するか |
|---|---|---|---|
| ashigaru3 (自分) | `/home/hakudokai/projects/multi-agent-shogun/logs/inbox_watcher_ashigaru3.log` | 同左 | 一致 |
| karo-second | `/tmp/watcher-karo-second.log` (PID 215913) | `logs/inbox_watcher_karo-second.log` | ★不一致★ |

`logs/inbox_watcher_karo-second.log` の mtime は 2026-08-02T13:29 (発令書が言う 07-21 とは
ずれるが、いずれにせよ現在実稼働の書き込み先ではない)。karo-second の watcher process は
`ps -ef` 上 `bash scripts/inbox_watcher.sh karo-second multiagent-second:0.0 claude` として
起動されているが、その stdout/stderr は `/tmp/watcher-karo-second.log` に向いている。
`scripts/watcher_supervisor.sh` / `watcher_supervisor_third.sh` の `start_watcher_if_missing`
はいずれも `logs/inbox_watcher_<agent>.log` 形式のみを使う設計で、`/tmp/watcher-*.log` という
命名を生成する呼び出し箇所は repo 内 grep (`--include=*.sh`) で ★0件★ — 現行プロセスは
★repo 管理外の手動 nohup (もしくは repo に無い別 launcher) で起動され、意図しない log 先に
向いたまま★ と判定する (断定はしない。起動履歴の shell history 等は本工区の権限外)。

★この不一致自体が発令書の指摘「検出器が既に死んでおる」の直接証拠★ — karo-second 分の
`deferred to next cycle` 0件という観測は、ログが物理的に別の場所へ流れていたことによる
アーティファクトである可能性が高い (真の0件かどうかは `/tmp/watcher-karo-second.log` を
併せて見なければ判定不能。本工区は当該 log の内容精査までは scope 外)。

## 3. 負テスト (最低4形・実文つき)

harness: `/tmp/claude-1000/.../scratchpad/w201_negative_tests.sh` (発令書の認可通り scratchpad 配置・repo 非追跡)。
`process_unread_once` を `__INBOX_WATCHER_TESTING__=1` でソースして直接呼ぶ方式
(既存 `tests/test_inbox_expiry_supersession.bats` と同一手法)。

実行結果 (2026-08-04T18:52:31〜18:52:56 JST・全8アサーション PASS):

```
════════════════════════════════════════════════════════════
 W201 negative tests — start 2026-08-04T18:52:31+0900
 target=/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_watcher.sh
 sha256=6fc62bbe98c8e2003d78de90dbd6cea0f450447c17c73e46142361e25f9668d9
════════════════════════════════════════════════════════════

── (a) busy-deferred clear_command survives to next cycle ──
  input: 1x clear_command (id=msg_a_clear), agent BUSY
  cycle1 log: [SKIP] Agent ashigaru_test is busy — /clear (clear_command) deferred to next cycle (id=msg_a_clear, left unread)
  [PASS] (a) cycle1: message stays unread while busy (expected=actual=False)
  now agent IDLE — cycle2:
  cycle2 log: [SEND-KEYS] Sending CLI command to ashigaru_test (claude): /clear
  [PASS] (a) cycle2: message executed and marked read after busy clears (expected=actual=True)

── (b) execution failure returns the message to its sender ──
  input: 1x clear_command (id=msg_b_clear), agent IDLE, send_cli_command mocked to fail (rc=1)
  log: [MOCK] send_cli_command forced failure for: /clear
  log: [RETURN-TO-SENDER] ashigaru_test_fail: undeliverable clear_command (id=msg_b_clear) — send_cli_command failed (rc=1)
  [PASS] (b) failed message is consumed (read=True, not retried forever) (expected=actual=True)
  [PASS] (b) sender (karo-second) inbox received delivery_failed notice referencing msg_b_clear (expected=actual=FOUND)

── (c) model_switch — valid payload executes, invalid payload returns to sender ──
  input: 1x valid model_switch (id=msg_c_valid, '/model sonnet'), 1x invalid (id=msg_c_invalid), agent IDLE
  log: [SEND-KEYS] Sending CLI command to ashigaru_test2 (claude): /model sonnet
  log: [SKIP] Invalid model_switch payload for ashigaru_test2: switch to something without a slash
  log: [RETURN-TO-SENDER] ashigaru_test2: undeliverable model_switch (id=msg_c_invalid) — normalize_special_command produced empty command (unrecognized type/content)
  [PASS] (c) valid /model payload executed and marked read (expected=actual=True)
  [PASS] (c) invalid payload consumed (read=True, not retried forever) (expected=actual=True)
  [PASS] (c) invalid model_switch produced a delivery_failed notice to sender (expected=actual=FOUND)

── (d) positive control: idle agent, clear_command executes normally ──
  input: 1x clear_command (id=msg_d_clear), agent IDLE (no busy-guard involvement)
  log: [SEND-KEYS] Sending CLI command to ashigaru_test3 (claude): /clear
  [PASS] (d) positive control: idle clear_command executes and is marked read (expected=actual=True)

════════════════════════════════════════════════════════════
 RESULT: PASS=8 FAIL=0  finished 2026-08-04T18:52:56+0900
════════════════════════════════════════════════════════════
```

**(c) の解釈注記**: model_switch には元々 busy guard に相当する分岐が存在しない
(busy guard は `clear_command`/`"/clear"` cmd 専用)。よって「同2形」は
①正常実行 (=消えぬ・成功で消費) ②不正内容→送り主へ返る (=消えぬ・失敗でも消費されて
無限リトライ化しない) の対と解釈した。busy 状態を model_switch に絡めた形は現行コードに
対応する分岐が無いため作成していない (★恣意的省略ではなく、対応する分岐が存在しない
ことを確認した上での判断★)。

**(b) の実装ノート**: `send_cli_command` の内側 busy guard (③の対象・L563-567 相当)
を直接 shogun 経由で発火させようとしたが、shogun には ★別のより手前にある無条件
suppression 分岐★ (L555 付近「shogun へは CLI コマンド注入を行わない」) が先に
"return 0" するため到達不能と判明した (これも実装上の発見であり隠さず記載する)。
`process_unread()` の specials ループ (=本工区が実際に触った箇所) の「失敗時に
送り主へ返す」契約を独立に検証するため、`send_cli_command` を mock して任意の失敗を
注入する方式に切り替えた — 単体境界としてはこちらが正しい (内側 busy guard 自体の
`return 1` 化はソースコード上で目視確認済み、別途下記§5に記載)。

## 4. 陽性対照 (④再掲・非busy正常系)

上記 (d) が該当。加えて既存 e2e 相当のログ文言 (`[SEND-KEYS] Sending CLI command to
ashigaru3 (claude): /clear` 等) が変更されていないことを diff で確認済み — 正常系の
ユーザー可視文言に非互換変更は無い。

## 5. 既存試験への影響 (壊れる試験の件数を隠さず記載・rule 9 準拠)

`bats` (v1.13.0) にて `tests/agent_selfwatch.bats`・`tests/unit/test_send_wakeup.bats`・
`tests/unit/test_idle_flag.bats`・`tests/test_inbox_expiry_supersession.bats` を実行
(★e2e/*.bats・その他一部は `tests/test_helper/bats-support`・`bats-assert` が
空ディレクトリ (未 vendored) のため実行不能・本工区の欠陥ではなく環境の欠落。
`git status` で該当ディレクトリが元から空である事を確認済み)。

| suite | 実行前 (baseline・`git stash`) | 実行後 (本修正適用) |
|---|---|---|
| `tests/agent_selfwatch.bats` + `tests/unit/test_send_wakeup.bats` + `tests/unit/test_idle_flag.bats` (計77件) | (T-CRESET-003 のみ既存 FAIL・他76件 PASS) | 75 PASS / 2 FAIL |
| `tests/test_inbox_expiry_supersession.bats` (9件) | 9 PASS | 8 PASS / 1 FAIL |

**壊れた試験 = 2件、いずれも「是正の代価」であって欠陥ではない (rule 9 該当)**:

★★この2件は落ちたのではなく、正しく落ちた★★ (将軍second殿具申・裁定は委員長殿へ)。
機構 (試験) が働かなかったのではなく、機構は「誤った契約」を正しく守っていた
(consume-before-commit を仕様として固定していた) — 契約が誤っていれば試験も誤り、
かつ緑に光る。緑は正しさの証ではない、という足軽7号 PASS 則と同型の教訓である。
★2件の試験ファイル自体は本工区では ★消して直していない★ (対象外の scope・
`tests/*.bats` は本工区の書込認可外)。将軍second殿の具申どおり「supersedeマーカーで
旧契約を検めていたと残す」形での処理が望ましいが、★その実施可否・実施方法の裁定は
委員長殿に委ねる★ (当職も将軍second殿も裁いていない、という原文の位置づけをそのまま
継承する)。

1. `TC-FR-003: get_unread_info routes task/special messages correctly`
   (`tests/agent_selfwatch.bats:86`) — `get_unread_info()` を単独で1回呼んだ直後に
   `msg_clear`/`msg_model` の `read` が `True` になっている事を assert している。
   これは ★本工区が根治した consume-before-commit の挙動そのもの★ を「正しい経路」として
   固定していた試験であり、今回の是正で意図的に破れる。count/specials 件数の正しさ
   (count=1, specials件数=2) 自体は変更後も一致しており、破れているのは「誰が・いつ
   read=True を打つか」という契約変更部分のみ。
2. `LB-07: clear_command special is still consumed exactly once (no regression)`
   (`tests/test_inbox_expiry_supersession.bats:257`) — 同様に `get_unread_info()` の
   2回目呼び出しで specials が消えている事を assert。理由は上記と同じ。

**壊れていない事を確認した試験 (該当・非該当の両方)**: 期限切れ/supersede 自動既読化
(LB-02/LB-03/LB-04/LB-05/LB-06/LB-08/LB-09 = 6件)・busy 判定/エスカレーション/CLI別分岐/
self-watch/idle flag 系 (T-SW-*, T-ESC-*, T-BUSY-*, T-CODEX-*, T-COPILOT-*, T-SHOGUN-*,
T-SHOOK-*, T-001〜T-009 = 計73件) は ★全て変更前と同じ結果で PASS★。本工区は
「特殊メッセージが read=True になるタイミング」のみを変えており、それ以外の busy 判定・
CLI 分岐・エスカレーション経路には手を入れていないことの裏付けとなる。

**pre-existing failure (本修正と無関係)**: `T-CRESET-003: send_context_reset sends /clear
for ashigaru` (`tests/unit/test_send_wakeup.bats:1102`) は `git stash` で本修正を外した
baseline でも同一の FAIL を再現した。★本工区が生んだものではない★ (別件として karo-second
殿へ別途報告要否を委ねる。本工区の scope_out=「上記2件以外の既存欠陥の修正」に該当する
ため、本工区では手を入れない)。

**この修正が新たに開ける穴は何か (fix-review-must-ask-new-hole 準拠)**:

1. `is_no_auto_clear_agent()` が真の間 (SecondPC role recovery 中)、clear_command は
   ★毎 cycle 未読のまま残り、毎 cycle 同じ SKIP ログが出続ける★ (以前は1回で黙って
   消費されていた)。実害は無い (実際の /clear 送信は起きない・ログ量が増えるのみ) が、
   ログ量増加は明記しておく。フラグが解除されれば正しく実行される — 「延期は延期のまま」
   という②の要求を満たした帰結として発生する意図された挙動。
2. `send_cli_command` の cli_restart 分岐 (`__CLI_RESTART__:*`) は既存コードのまま
   `switch_cli.sh` の終了コードをパイプ越しに握り潰し、常に `return 0` する
   (③の対象として本工区が新設した失敗検知の網に ★掛からない★)。これは本工区が
   ★新たに開けた穴ではなく、既存の穴が今回未着手のまま残存している★ ものである。
   発令書の確定欠陥リストに cli_restart 分岐は名指しされておらず、修正には
   `switch_cli.sh` 側の戻り値伝播という別ファイルへの波及が必要なため、
   scope_in (「上記 script とその負テスト」) を超えると判断し ★意図的に手を付けていない★。
   次工区候補として書き残す。
3. `mark_message_processed`/`return_message_to_sender` は特殊メッセージ1件ごとに
   追加の python subprocess + flock 取得を発生させる。特殊メッセージは頻度が低い
   (clear_command/model_switch/cli_restart のみ) ため実用上の性能影響は無いと判断する
   (計測はしていない・判断根拠は頻度の低さのみである事を明記)。

## 6. 対になる他工区

同日 `docs/incident_logs/` 配下に multiple W-番号 (W141〜W206等) が存在するが、
`inbox_watcher.sh` の本体コード修正を scope とする工区は本 W201 のみ (grep 済)。
対になる工区は ★無し (探した範囲=本日の docs/incident_logs/ 全件のファイル名)★。

## 7. 境界の遵守

- third_pc 側は触っていない (grep・読み取りも含め本報告で third_pc パスへの言及なし)。
- 対象 file の commit/push/stage は行っていない (`git status --short` で `M
  scripts/inbox_watcher.sh` のみ・staged なし)。
- process の停止・再起動・kill は行っていない (17プロセス全て `ps -ef` 時点のまま)。
- 患者データ・secret 値の出力は行っていない。

## 8. 成果物

- 修正: `scripts/inbox_watcher.sh` (差分 +121/-14行・最終 sha256
  `3a7779f9fa3639bb76871a94e6b8be537d18bc5d4c9451b20b961939b5867c4d`。
  内訳=初版差分 +100/-14 (sha256 6fc62bbe98c8e2003d78de90dbd6cea0f450447c17c73e46142361e25f9668d9)
  + 追補②B-4対応差分 +21行 (§10 参照))
- 本報告書: 本 file (開始報告8項目・移植申し送り・B-4対応を含め全 10 節)
- 負テスト harness (scratchpad・非 repo・非 commit 対象・追補後も 8/8 PASS 再確認済
  2026-08-04T19:01:48+0900):
  `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/5a4a89fc-113f-40df-82f9-0bf88818ddc9/scratchpad/w201_negative_tests.sh`

## 9. 移植する者への申し送り (追補①・DUPLICATE_IMPLEMENTATION_RISK 対応)

★確認済の事実★: 同一欠陥 (consume-before-commit) が3つの別コードに実在する
(SecondPC実稼働 sha=6dcfc02c=本工区が直した対象／SecondPC別path sha=fe2ed51d／third_pc
sha=288f455f)。★本工区は sha=6dcfc02c の一本のみを直接修正した。他二版は未読・未変更★
(third_pc は境界により触っていない。SecondPC別path fe2ed51d は存在を知らされたのみで
実物は未確認)。以下は ★行番号ではなく構造で★ 移植者へ引き継ぐ情報である。

### 9.1 何を変えたか (構造で)

1. **「抽出時 read=True 確定」を撤去**: `special_types` (`clear_command`/`model_switch`/
   `cli_restart`) を unread から抽出する関数 (本版では `get_unread_info()`) が、
   ★抽出と同時に対象メッセージを read=True にして atomic write する処理★ を持つなら、
   それを撤去する。期限切れ/supersede 由来の自動既読化 (実行を伴わない正当な自動処理)
   はそのまま残してよい — 見分け方は「実行 (tmux send-keys 等の副作用) を伴うかどうか」。
2. **「post-execution commit」関数を新設**: 単一メッセージ id を対象に、実行成功が
   確認できた ★後にのみ★ read=True を打つ関数 (本版=`mark_message_processed`)。
   既存の atomic write パターン (realpath 経由 tmp→rename、flock 保護) を再利用する。
3. **busy guard の戻り値契約を「成功偽装しない」形へ**: エージェントが busy で
   コマンドを送れなかった時、呼び出し元にそれを「失敗」として伝える (本版では
   /clear 送信部の busy guard を `return 0`→`return 1` に変更)。
4. **specials 処理ループを「実行結果を見てから commit/return」の形へ**: 各特殊
   メッセージについて、実行関数の戻り値を見て ①成功→②新設の post-execution commit
   関数を呼ぶ ②失敗 or 認識不能→③送り主へ返す関数を呼ぶ、という分岐にする。
5. **「送り主へ返す」関数を新設**: 実行できなかったメッセージについて、送り主の
   inbox へ delivery_failed 通知を書き込み (自前の `inbox_write.sh` 相当を再利用)、
   対象メッセージを②の commit 関数で消費する (無限リトライにしない)。可能なら、
   書込み後に送り主の inbox ファイルを再読して着地を確認するログを追加する
   (③B-4 参照・完全な「本人到達確認」ではないことに注意)。

### 9.2 三版のどこが違うと見込まれるか (未確認・推測)

- sha が3つとも異なる = 少なくとも一部の行番号・関数名・変数名が異なる可能性が高い。
  本版の `get_unread_info`/`send_cli_command`/`process_unread` に相当する関数が
  ★別名かもしれない★ ので、まず「unread かつ special_types のメッセージを read=True に
  する箇所」「busy 判定で `return 0` している箇所」を構造 (処理内容) で検索すること。
- CLI 別分岐 (claude/codex/copilot) の実装粒度が版によって異なる可能性がある
  (本版は §CLI別コマンド変換 という独立ブロックを持つ)。
- lockfile/atomic-write の実装方式 (flock vs mkdir フォールバック) が版によって
  簡略化されている可能性がある — 移植時に元の版の atomic-write 方式を壊さないこと。

### 9.3 移植時に確かめるべき点

1. 対象版の `special_types` に相当する定数・タプル・配列を特定し、それを
   ★抽出と同時に★ read 済にしている書込みブロックを見つける (本工区の §2①相当)。
2. その書込みブロックを呼ぶ関数の「呼び出し元」を辿り、呼び出し元が実際に
   コマンドを送信 (tmux send-keys 等) する箇所との時間的前後関係を確認する
   (「読む前に確定」か「確定してから読む」かが本欠陥の核心)。
3. busy guard がどこに何個あるか (本版は2箇所=内側/外側) を洗い出し、両方とも
   「延期時に成功を偽装していないか」を確認する。

### 9.4 移植先で「当たらぬ」場合の見分け方 (★移植者が自分で証拠を取れる形★)

★本工区自身の反省 (W195 由来の型) を踏まえ、以下は「当たった」ことの証拠を
本工区が先に渡すのではなく、★移植者が自分の手で再現できる検査手順★ として書く★:

1. 対象版を `__INBOX_WATCHER_TESTING__=1`（もしくは対象版の同等テストガード）で
   ソース可能か確認する。ソースできない設計 (テストガードが存在しない版) なら、
   まずガードの追加自体が移植の前提条件になる — その場合「当たらぬ」の第一の意味は
   「そもそも単体テストの土俵が無い」。
2. ソース可能なら、本工区の `/tmp/.../scratchpad/w201_negative_tests.sh` と同型の
   4形 (busy延期→次cycle実行／実行失敗→送り主へ返る／model_switch同型2形／陽性対照)
   を対象版の関数名に置き換えて ★移植者自身が実行し★、8/8 PASS することを自分の
   実行ログで確認する。本工区の PASS ログ (§3) を「証拠として渡す」のではなく、
   ★移植者が自分の環境・自分の sha に対して再実行して初めて証拠になる★
   (これが将軍second殿の一般化「求めた証拠を己が先に渡しておれば、それは証拠に
   成り申さぬ」への応答)。
3. もし対象版の構造が本工区の想定 (①〜⑤) と大きく異なり当てはめ不能な場合、
   ★「当たらぬ」と判定してよい基準★ = 「read=True を打つ箇所が1箇所に集約されておらず
   複数箇所に分散している」「busy guard が3箇所以上ある」等、本工区が前提とした
   構造上の仮定が崩れている場合。この場合は移植ではなく個別設計が必要 — 無理に
   当てはめず、委員長殿/環境部長殿へ「構造不一致」として差し戻すこと。

## 10. B-4 Return-Path 対応 (追補②・project_documents id=60d41aee-5128-427d-82ae-dc0946d94682 v1.1)

★全文未読 (§KNOWLEDGE_GAP_WARNINGS 参照)★。追補メッセージに引用された要旨のみを根拠に
以下を実施・自己評価する:

> 引用: 「配送失敗時は送り主へ返し、別経路で本人到達を確認するまで警告義務は解けぬ」

**実施した事**: `return_message_to_sender()` に、`inbox_write.sh` 呼び出し後、
送り主の inbox ファイルを ★再読して★ 当該 msg_id への参照が実際に着地しているかを
確認するログ (`landing confirmed via file re-read` / `WARNING: could not confirm`)
を追加した (sha256=3a7779f9fa3639bb76871a94e6b8be537d18bc5d4c9451b20b961939b5867c4d)。
負テスト(b)(c) で実際にこのログが出ることを確認済 (§3 参照・再実行ログに
`landing confirmed via file re-read` が出現)。

**★これは B-4 の完全充足ではない★ — 正直に書く**:
- 「別経路」の解釈= 本実装は「inbox_write.sh の exit code」とは独立に「ファイルを
  再読する」という意味で最小限の別経路にはなっている。しかし「本人到達」= 送り主
  (人間またはエージェント) が実際にその通知を ★読んで認識した★ ことの確認では ★ない★。
  ファイルに書き込まれた=届いた、ではないことは本日の家老second台帳
  (`docs/incident_logs/2026-08-04_karo-second_day_ledger.md` §8「4点セットが実在する
  ゆえ守られておるように見える」)・`acknowledged_at` 無情報化の教訓そのものであり、
  ★本工区が同じ誤りを踏まぬよう、あえて「landing confirmed」であって
  「arrival confirmed」ではないと明記する★。
- 真の「本人到達確認」を実装するには、この delivery_failed 通知メッセージ自体の
  `read` フィールドを ★後続の watcher cycle で追跡し read=true になるまで待つ★
  仕組みが必要になる。これは本工区 (inbox_watcher.sh 内の consume-before-commit
  根治) の scope を超える別機能 (通知の往復確認) であり、★意図的に未着手★ とする。
  次工区候補として書き残す (委員長殿/軍師second殿の裁定を仰ぐ)。

## 11. 追補 (2026-08-04T19:25頃・委員長殿裁可 msg_20260804_191210_11930ef7 対応・append-only)

### 11.1 壊れた試験2件への supersede マーカー (裁可①の実施)

委員長殿裁可=「消さず supersede マーカーを付し、新しい試験のどれが役目を引き継いだかを書け」。

- `tests/agent_selfwatch.bats` の `TC-FR-003` 直前に supersede コメントを追加し、
  同ファイルへ新規 `TC-FR-003b`「get_unread_info does not consume specials at
  extraction (W201 fix)」を追加した。TC-FR-003b は (a) 抽出のみでは read=True が
  立たない事 (b) `get_unread_info()` を複数回呼んでも specials が消えない事
  (c) `mark_message_processed()` を呼んで初めて read=True が立つ事、の3点を
  自分の実行で検証する (bats 実行結果: ok)。
- `tests/test_inbox_expiry_supersession.bats` の `LB-07` 直前に同様の supersede
  コメントを追加し、新規 `LB-07b`「clear_command special survives repeated
  get_unread_info (W201 fix, no consume-on-extract)」を追加した (bats 実行結果: ok)。
- 旧 `TC-FR-003`/`LB-07` 自体は ★変更していない★ (assertion 不変・引き続き FAIL)。
  supersede はコメント (マーカー) のみで実施し、「試験が欠陥を守っていた」記録を
  消していない。
- 実行結果 (2026-08-04T19:2x JST): `tests/agent_selfwatch.bats` 15件中 TC-FR-003
  のみ FAIL・他14件 (新設 TC-FR-003b 含む) PASS。`tests/test_inbox_expiry_supersession.bats`
  10件中 LB-07 のみ FAIL・他9件 (新設 LB-07b 含む) PASS。★壊れる試験の件数は本追補
  でも増減せず2件のまま★ (rule 9 準拠・新規追加分は両方 PASS)。
- 差分: `tests/agent_selfwatch.bats` (+70行前後)・`tests/test_inbox_expiry_supersession.bats`
  (+55行前後・supersede コメント込み)。両ファイルとも commit/push/stage は行っていない
  (`git status --short` で `M` のまま)。

### 11.2 KNOWLEDGE_GAP_WARNINGS (2) の追跡結果 — ★「判らぬ」で報告★

msg_20260804_191513_99be1b5f (Supabase 直読認可) は msg_20260804_192004_8243f6f3
(19:20:04) により ★撤回・上書き★ 済 (fetch 解禁・`git -C /mnt/c/Projects/hakudokai-dev
show origin/main:<path>` 経路へ変更)。指示「path が判らねば『判らぬ』と報せよ・推し量って
渡すな」に従い、以下の通り自分で探索した結果を報告する。

- 探索: `git -C /mnt/c/Projects/hakudokai-dev log --grep="60d41aee"` (0件)・
  `git grep -l "60d41aee" origin/main` (0件)・`git grep -l "Return-Path" origin/main -- '*.md'`
  で1候補 (`docs/rules/delivery-protocol.md`) を発見。
- ★この候補は ★却下した★★: 当該ファイル自身の冒頭コメント (26b6e049 直前の版) に
  「組織上の最上位正本: 配送規約 (★Supabase未登録★)」と明記されており、Supabase
  project_documents id=60d41aee の doc とは ★別の corpus★ であると自己申告している。
  加えて該当ファイルは本日18:02 (`26b6e049`) に「v2.0 全面改訂」として ★構成を
  作り直された★ばかりであり、当職が引用した「v1.1」(§10 参照) とはそもそも版が
  異なる — 「典拠は固まった最新を取れ (新しすぎる版を掴むな)」の教訓に照らしても
  採用を見送るべき候補だった。
- ★結論=「判らぬ」★。`project_documents id=60d41aee-5128-427d-82ae-dc0946d94682`
  に対応する origin/main 上の path を特定できなかった。憶測で path を渡すことはしない
  (発令書「推し量って渡し申さぬ」に従う)。KNOWLEDGE_GAP_WARNINGS (2) は ★未解消のまま★
  残し、path 特定は家老/軍師/将軍等 DB アクセス権限を持つ役職に委ねる。
