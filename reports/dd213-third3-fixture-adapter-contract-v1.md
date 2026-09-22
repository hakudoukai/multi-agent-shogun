# DD-213 third3 — fixture semantics + Adapter receipt contract v1

- **owner**: ashigaru-third-3
- **board**: 42baf091-bf2b-49db-9bfa-824a8527d99d（DD-PQ-Third-Design-602）
- **order**: /home/hakudoukai/hermes-departments/handoverdocs/reports/dd213-specialist-work-orders-v1-20260922T1355JST.md（Slice B）
- **scope**: Synthetic/read-only only。live seat dispatch・DB mutation・config/service change・restart・secret・push は0。

## 1. Fixture raw result（実測・synthetic in-memory）

command:
```
cd /mnt/c/DentalBI && python3 scripts/fixtures/lane_dispatch_fixture.py
```
raw stdout（逐語・省略無し）:
```
=== 陽性対照: assignment→accept→close が一巡する ===
  ✅ accept成功
  ✅ work開始
  ✅ close成功
=== (a) accept二重送信 ===
  ✅ (a) 1発目のみ成功・2発目は0行更新で敗北
  ✅ (a) ownerは1人のまま
=== (b) revoke後の旧accept ===
  ✅ (b) revoke成功・旧epoch acceptは敗北
=== (c) timeout回収の直後に旧acceptが着弾 ===
  ✅ (c) 回収成功・遅延acceptは敗北・新epochのacceptだけ成功
=== (d) Commander再送と旧便到着の競合 ===
  ✅ (d) 新epochのacceptのみ成功・旧便は敗北
=== (e) close後のaccept ===
  ✅ (e) close後acceptは0行更新で敗北
=== 履歴保存（全遷移がlane_historyに残る） ===
  ✅ 履歴3遷移が保存されている (実測3行)

★結果★ PASS=10 FAIL=0（全形PASS）
```
**exit code = 0**。fixture は `:memory:` SQLite のみ・file I/O/network/外部副作用0（本文読了で事前確認済）。安全機序=単一行UPDATEのCAS述語 `WHERE assignment_id=? AND epoch=? AND state_version=?`（0行更新=敗北・fail-loud・無言retry無し）。

## 2. Adapter receipt contract v1 — `dispatch_receipt` / `acceptance_receipt`

既存器の実挙動のみに基づく（新規機序は発明せず）。典拠=`/mnt/c/DentalBI/scripts/cc_goal_from_board.py`本文読了。

### 2.1 `dispatch_receipt`（写した事の証）

- **成立条件**: `cc_goal_from_board.py:main()` が `rc=0`（`WROTE`分岐）で終わる ―― すなわち `os.replace(tmp, dst)` によって `queue/goals/<seat>.yaml` が★原子的に★書かれた事。
- **観測可能な形**: 書かれた goal file 自身が receipt。含む欄=`issued`（actor・刻・板id先頭8桁、`build_goal()` L52 逐語書式）、`board_id`、`max_turns`、`turns_used: 0`（初期値、書いた瞬間は必ず0）。
- **排他保証の性質**: `check_exclusive()`（L66-75）は★file存在のみ★で判定する純関数。DB側lockは無い。∴ dispatch_receipt の一意性は「その席の goal file が一個しか無い事」でしか保証されず、DB側の二重発行検知は本器の範囲外。
- **失敗系との対比**: `rc=2`（MEAS_FAIL・接続情報無しまたは板を読めず＝★0件ではない★）／`rc=3`（EXCLUSIVE・生きた goal が既に在る）／`rc=4`（NOROW/NOTSTARTABLE・板の行が無いか着手可status外）―― いずれも goal file を書かない＝dispatch_receipt 不成立。
- **★写した≠読んだ★（原docstring逐語）**: dispatch_receipt は「事業部長が席へ投げた」事の証であって、席がそれを読んだ・着手した事の証ではない。

### 2.2 `acceptance_receipt`（受けた事の証）

- **成立条件**: dispatch_receipt が成立した同じ goal file の `turns_used` フィールドが 0 から増分される事。
- **典拠**: `cc_goal_from_board.py` 自身の docstring 逐語「受入の証は席側の turns_used の更新（goal_stop_hook が書く）であって本器の成功ではない」。増分の実装は `goal_stop_hook.py`（別器）にあり、★本弾では goal_stop_hook.py の本文は未読★＝増分の正確なトリガ条件（何ターン毎か・turn境界の定義）は **UNMEASURED**。
- **本弾での経験的観測（実測・本器の外側で確認済）**: 当職自身が本タスクを受け付けた過程で、`queue/goals/ashigaru-third-3.yaml` の `turns_used` が 0→2 へ増分している事を `Read` で直接確認した（2026-09-22、本報告作成時点）。これは acceptance_receipt が dispatch_receipt とは★別のタイミング・別の書き手★で更新される事の実例であり、両者が同一イベントでない事の直接証拠。
- **dispatch_receipt との非対称性**: dispatch_receipt は書き手＝事業部長側の器（`cc_goal_from_board.py`）が単発で生成する。acceptance_receipt は書き手＝席側の器（`goal_stop_hook.py`）が継続的に（着手後、ターンが進む都度）更新する。∴ 両者を同一の「成功」フラグとして扱う設計は誤り＝本契約が分離を明記する理由。

### 2.3 debounce / debris gate（典拠=`/mnt/c/DentalBI/scripts/pane_notify.sh`本文読了）

- **debris gate（実装名=残骸検査・判定関数=`residue_verdict()`、`_residue_triage.sh`に分離・「純関数・負テスト13形PASS」と本文コメントに明記、本弾では`_residue_triage.sh`自体は★未読★＝内部ロジック詳細はUNMEASURED）**: pane の❯行残骸を`strip_prompt()`で抽出し、`CLEAN`/`RUNNING`/`DIALOG`/`CTXFULL`/`DEBRIS`/`PENDING`の6値に分類（L279-341で分岐を確認）。
  - `DEBRIS`＝自分（送信器）自身の過去noticeの残骸と判定→`send_csiu_ctrl_u`で消してから進む。消えなければ★中止★（exit 3）。
  - `PENDING`＝他人の未送信の文と判定→★消さずに★`send_csiu_enter`で先に送ってから進む（「他人の便を消すな」が明記の設計理由）。
  - `CLEAN`/`RUNNING`＝素通り。
  - `DIALOG`/`CTXFULL`＝人間裁定が要る／叩くほど悪化＝★中止★。
- **「debounce」という語自体は本文に不在（★確かめて居らぬ★は書かぬ・実際に grep 済＝0件）**。相当する機序は、各 send-keys 操作の直後に必ず `sleep 1` または `sleep 2` を置いてから `capture_current` で再検査する反復パターン（L327-341, L344-400全体）＝端末バッファの更新が非同期である事に対する★整定待ち＋再検証★。本契約ではこの反復パターンを「debounce」の実体として定義する（造語ではなく既存パターンへの命名）。

### 2.4 CSI-u Enter（典拠=同上、逐語行番号付）

- **定義**: `send_csiu_enter() { $TMUXC send-keys -t "$PANE" -H 1b 5b 31 33 75; }`（L267）―― 生byte列 `ESC [ 1 3 u`＝Kitty keyboard protocol の CSI-u 表現による Enter。
- **なぜ生byteか**: 本文冒頭コメント⑧（L13-16）逐語「Hermes TUI v2026.8.3 は Kitty/CSI-u を有効化している。`C-m`/`C-j`/`C-u` や `Escape '[' '1' '3' 'u'` は修飾キーとして届かず、送信済み本文を composer に残した」＝通常の`C-m`送出ではKitty対応TUI相手にEnterとして解釈されず、投入未完了のまま本文が残留する実障害が過去に在った（「壊して直した回数=8」の8番目）。
- **送信後の検証**: `send_csiu_enter`後は`sleep 2`→再captureし、①投入欄に`seq${SEQ}`が残っていないか（残っていれば未達・自分のnotice掃除対象）、②走行中述語（`to interru`/`ruminating`等の短断片、狭いpaneでの切れに備え★短い語で照合★）で相手が現に走り出したかを判定。1回目で自分のnoticeが残っていれば2回目のCSI-u Enterを許容、それでも残れば★未達★（exit 5）。
- **対の操作 CSI-u Ctrl+U**: `send_csiu_ctrl_u() { $TMUXC send-keys -t "$PANE" -H 1b 5b 31 31 37 3b 35 75; }`（L268、生byte `ESC [ 1 1 7 ; 5 u`）＝送信成立後、★自分のnoticeだけ★（`is_own_notice()`で厳密一致検査、L269-274）を掃除する用途に限定。他人の残骸は対象外（PENDING分岐参照）。

## 3. Non-goals（本報告が扱わぬ事の明示）

- 生きた席への実dispatch実行・観測は行っていない（synthetic fixtureのみ）。
- DB（Supabase/`task_tracker`/`pc_handshake`）への書込・接続確認は行っていない（`cc_goal_from_board.py`の`_env()`/`fetch_row()`は読解のみで未実行）。
- `goal_stop_hook.py`本文は未読＝`turns_used`増分の正確なトリガ条件はUNMEASURED（本文2.2に明記）。
- `_residue_triage.sh`本文は未読＝`residue_verdict()`の内部分岐詳細はUNMEASURED（本文2.3に明記）。
- `pc_handshake`のseq/sender照合ロジック（`pane_notify.sh` L203-239）の存在は確認したが、独立検証（実DBへの問合せ）は行っていない。
- lease（PID/state、`cc_goal_from_board.py`docstring L13で「PQ-104のlease表・L3 GO後」と明記された次段機序）は本契約の範囲外＝未設計・未実装。
- config/service変更・process restart・deploy・push・accept・close はいずれも行っていない（発注書冒頭の global boundary、および本タスクのstop_when条項に従う）。
- 本報告はboard 42baf091の受入判定そのものではない（判定は分野の軍師に委ねる、goal file `verify:`欄）。

## 4. 自己点検

材料は全て本弾で自ら開いた一次資料（fixture本文・`cc_goal_from_board.py`本文・`pane_notify.sh`本文・fixture実行の生stdout）のみ。未読箇所（`goal_stop_hook.py`・`_residue_triage.sh`）はUNMEASUREDと明記し、推定で埋めていない。

---
**SHA256（本行追記前の本fileの全内容、二器で一致=`sha256sum`/`python3 hashlib`）**: `cedb3073175f72ce6f8ff34075143900d71bed6379ef1aa9edcf2bae00148300`
（自己言及の性質上、本行自体は上記digest計算の対象外。commit後の最終blob shaはcommitログへ別途記す）
