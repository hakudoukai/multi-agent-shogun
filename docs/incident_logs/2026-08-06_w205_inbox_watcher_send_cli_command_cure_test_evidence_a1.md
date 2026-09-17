# W205: scripts/inbox_watcher.sh send_cli_command() 根治 — 試験証跡 (足軽1号)

発令: karo-second msg_20260806_002057_b45c43a5 (2026-08-06T00:20:57 前後・機械)
FAIL差戻し: karo-second msg_20260806_003922_846e99ca (2026-08-06T00:38:08 前後・軍師FAIL=様式不足「試験結果file実体を確認できず」)
本file = 差戻し是正 ⒜⒝⒞ (試験結果を file に落とす・path+行数+sha256提出・実装diff要点を同file化)

断面: 2026-08-06T00:42 前後 (機械)

## 対象file (母集団)

| file | 行数 | sha256 |
|---|---|---|
| scripts/inbox_watcher.sh | 1728 | 14be354df1ac6d292b8a3f1dcae11e675312401a2b681c412bf2b76a49a235c6 |
| tests/agent_selfwatch.bats | 359 | 82fff5b107d7fa77f1863458b9d76e278054617b74540ecfbd93a6a05f575470 |

★注★: 上記2つの sha256 は前回提出便に既に書いたが、軍師殿は「26/29 PASS や supersede 整理を
正本上で再現できなんだ」と裁定 — 不足は sha 自体ではなく ★試験結果を記した file が repo 上に
実在しなかった事★。本 file がその不足を埋める。

## 打った命令 (逐語)

```
timeout 90 bats tests/agent_selfwatch.bats tests/test_inbox_expiry_supersession.bats
```

exit code = 1 (bats は1件でも FAIL があれば非0 を返す仕様。中身は下記参照)

## 出力 (全逐語・省略なし)

```
1..29
ok 1 TC-FR-001 [RED]: process_unread_once is defined and called on startup
ok 2 TC-FR-002: inotify + timeout fallback is configured
not ok 3 TC-FR-003: get_unread_info routes task/special messages correctly
# (in test file tests/agent_selfwatch.bats, line 124)
#   `"$VENV_PYTHON" - << 'PY' "$output" "$TEST_INBOX"' failed
# Traceback (most recent call last):
#   File "<stdin>", line 11, in <module>
# AssertionError
ok 4 TC-FR-003b: get_unread_info does not consume specials at extraction (W201 fix)
ok 5 TC-FR-004 [RED]: read-update path uses lock/atomic protections
ok 6 TC-FR-005: post-task inbox check rule is documented for ashigaru
ok 7 TC-FR-006 [RED]: metrics hooks are defined (unread_latency/read_count/estimated_tokens)
ok 8 TC-FR-007 [RED]: feature flags for Phase 1/2/3 are defined
ok 9 TC-FR-008 [RED]: normal nudge can be disabled (Phase 2 behavior)
ok 10 TC-FR-009: special command compatibility for codex is preserved
ok 11 TC-FR-016 (W205): busy guard now covers non-/clear commands too
ok 12 TC-FR-017 (W205): idle agent + successful send-keys still delivers /clear
ok 13 TC-FR-018 (W205): Enter delivery verification catches stuck unsent text
ok 14 TC-FR-019 (W205): send-keys failure (rc!=0) is no longer swallowed by || true
ok 15 TC-FR-010 [RED]: summary-first fast path exists (count/summary before full read)
ok 16 TC-FR-011 [RED]: send-keys is restricted to final escalation only
ok 17 TC-FR-014 + TC-NFR-002: inbox_write IF and schema remain backward compatible
ok 18 TC-NFR-003 [RED]: no-idle-full-read helper exists
ok 19 TC-NFR-008: test file itself has no skip directives (SKIP=0 guard)
ok 20 LB-01 [general-ashigaru]: plain unread message (no expiry/supersedes) counts as unread
ok 21 LB-02 [codex]: expired message excluded from count and marked read on disk
ok 22 LB-03 [command-layer]: supersedes marks the superseded message read on disk
ok 23 LB-04: future expires_at is not expired yet — still counted as unread
ok 24 LB-05: supersedes referencing a nonexistent id is a safe no-op
ok 25 LB-06 [backward-compat]: pre-existing messages without expiry keys work unchanged
not ok 26 LB-07: clear_command special is still consumed exactly once (no regression)
# (in test file tests/test_inbox_expiry_supersession.bats, line 288)
#   `"$VENV_PYTHON" - << 'PY' "$output"' failed
# Traceback (most recent call last):
#   File "<stdin>", line 3, in <module>
# AssertionError: {'count': 0, 'has_task_assigned': False, 'specials': [{'id': 'msg_clear', 'from': 'karo', 'type': 'clear_command', 'content': '/clear'}]}
ok 27 LB-07b: clear_command special survives repeated get_unread_info (W201 fix, no consume-on-extract)
ok 28 LB-08 [stop-hook]: expired message removed from 'read: false' grep count after get_unread_info
not ok 29 LB-09 [inbox_write integration]: expires_at/supersedes env vars round-trip; absent by default
# (in test file tests/test_inbox_expiry_supersession.bats, line 374)
#   `[ "$status" -eq 0 ]' failed
```

## 内訳 = 26 PASS / 3 FAIL

**PASS 26件**: TC-FR-001, 002, 003b, 004, 005, 006, 007, 008, 009, **016, 017, 018, 019**(本工区新設4件),
010, 011, 014+NFR-002, NFR-003, NFR-008, LB-01, 02, 03, 04, 05, 06, **LB-07b**, LB-08。

**FAIL 3件 — 各々が既知である理由 (逐語根拠つき)**:

### ① TC-FR-003 (agent_selfwatch.bats:87-97 に supersede 宣言が実在)

```
# SUPERSEDED (W201, ashigaru3, 2026-08-04, 委員長殿裁可 msg_20260804_191210_11930ef7):
# This test asserts the pre-fix "consume-before-commit" contract — that
# get_unread_info() itself commits read=True for clear_command/model_switch
# the moment they are extracted, before any execution is attempted. ...
# Left intentionally red, not deleted or edited (rule 9: a broken test here
# is the cost of the fix, not a defect — see
# docs/incident_logs/2026-08-04_w201_inbox_watcher_cure_a3.md §5).
# Successor test (asserts the corrected contract): "TC-FR-003b" below.
```

後継 TC-FR-003b は本試験一覧の #4 で PASS 済。この supersede は W201 (2026-08-04・ashigaru3)
由来で本工区 (W205) 着手前から repo 上に存在し、本工区の変更が原因ではない。

### ② LB-07 (test_inbox_expiry_supersession.bats:257-265 に同型の supersede 宣言が実在)

```
# SUPERSEDED (W201, ashigaru3, 2026-08-04, 委員長殿裁可 msg_20260804_191210_11930ef7):
# This test asserts that get_unread_info() ALONE consumes (read=True) a
# clear_command on first call. ...
# Successor test (asserts the corrected contract): "LB-07b" below.
```

後継 LB-07b は #27 で PASS 済。①と同根 (W201)。

### ③ LB-09 — 本工区と無関係の pre-existing 失敗 (git stash による陽性対照で実証済)

`git stash` で本工区の全変更 (scripts/inbox_watcher.sh, tests/agent_selfwatch.bats,
tests/test_inbox_expiry_supersession.bats 他) を退避し、直近 HEAD (commit 50c25a4) 単体で
再測:

```
$ git stash
$ timeout 60 bats --filter "LB-09" tests/test_inbox_expiry_supersession.bats
1..1
not ok 1 LB-09 [inbox_write integration]: expires_at/supersedes env vars round-trip; absent by default
# (in test file tests/test_inbox_expiry_supersession.bats, line 318)
#   `[ "$status" -eq 0 ]' failed
$ git stash pop
```

★HEAD 単体 (本工区の変更ゼロ) でも同一失敗★ = 本工区の変更が原因でない事の実測による証明。
LB-09 は inbox_write.sh の env var round-trip を検証する試験で send_cli_command() とは無関係の系統。

## 実装 diff 要点 (scripts/inbox_watcher.sh)

`git diff --stat scripts/inbox_watcher.sh` = 209 insertions(+), 35 deletions(-) (send_cli_command()
本体 L665- + 新設ヘルパ send_keys_verified() L619-664 + 呼出元 process_unread() の specials 処理
分岐 L1330-1370 付近のみ触接。他ブロックは不触)。

1. **新設 `send_keys_verified(text, enter_gap)`** — テキスト送出→Enter→capture-paneで送出文字列が
   未送出のまま残っておらぬか検証、最大2回リトライ。nudge 送出 (`send_wakeup`) で既に確立していた
   検証パターンをそのまま再利用 (Anti-Duplication・新規手法を発明せず)。

2. **busy guard の一般化** — 従来 `if [[ "$cmd" == "/clear" ]] && agent_is_busy; then return 1; fi`
   ( `/clear` のみ守っていた) を、`send_cli_command()` 冒頭 (shogun除外の直後) の
   `if agent_is_busy; then return 2; fi` へ統合。`/model`・codex `/new`・copilot 再起動を含む
   全コマンド種別が等しく守られる。

3. **`|| true` 除去** — コマンド本体+Enter送出の行 (旧: `tmux send-keys ... "$actual_cmd" || true` /
   `tmux send-keys ... Enter || true`) から `|| true` を除去し、`send_keys_verified()` 内で各
   send-keys の exit status を実際に見る。防御的なキー消去 (`C-u`／`x` dismiss 等、失敗しても
   実害の無い best-effort 操作) は意図して `|| true` を残置 (全除去は過剰と判断)。

## ★実装中に自ら見つけた穴 (finding→即是正)★

busy guard の戻り値を当初 `1` (既存の `/clear` 失敗コードと同じ) にした所、呼出元
`process_unread()` の specials 処理 (L1357付近) は rc!=0 を一律「送信失敗」と読み
`return_message_to_sender()` を呼ぶ設計だった。`return_message_to_sender()` は内部で
`mark_message_processed()` を呼び `read=True` を確定させる — ∴ busy な agent 宛の
model_switch/cli_restart が「延期」のつもりで ★実は消える★ 所であった。これは W201 が
clear_command について直した当の欠陥 (consume-before-commit) を model_switch/cli_restart で
再生産する事に等しい。

是正: busy guard の戻り値を **2** (Enter未確認等の真の失敗=1 と区別) に変更し、
`process_unread()` 側の分岐も rc=2 なら unread のまま continue (通知なし・次サイクル再試行)、
rc=1 のみ `return_message_to_sender` を呼ぶよう対で修正した。`clear_command` は元々
`process_unread()` 内の別の busy guard (L1350 付近) が `send_cli_command()` 到達前に continue
するため、この変更の影響を受けぬ (二重防御・無害)。

## 新設負テスト (tests/agent_selfwatch.bats、TC-FR-016〜019・全4件 PASS)

| ID | 検証内容 |
|---|---|
| TC-FR-016 | busy 中は `/model` もブロックされ (rc=2)、MOCK_LOG に送出テキストが現れぬ事 |
| TC-FR-017 | idle + 送出成功なら `/clear` は従来通り届く事 (回帰無し) |
| TC-FR-018 | capture-pane に送出文字列が残存したままなら検証が失敗し rc=1 を返す事 |
| TC-FR-019 | send-keys 自体が rc!=0 を返した場合、`|| true` で握り潰さず rc=1 で伝播する事 |

## 対工区

無し (探索範囲=queue/tasks/*.yaml, queue/inbox/ashigaru*.yaml 目視)。

## commit/push

未実施 (家老second権限・PASS後の慣例に従う・本 file も未commit)。
