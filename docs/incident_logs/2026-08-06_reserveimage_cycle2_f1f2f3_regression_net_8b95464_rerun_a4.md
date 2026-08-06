# 足軽4号 → 家老second/軍師second: F1/F2/F3 回帰網を 8b95464 に対して 再実走 (七項⑸埋め)

下命: `queue/inbox/ashigaru4.yaml` msg_20260806_150850_c77f9e97（家老second→足軽4号、15:08:50）。
先便: `docs/incident_logs/2026-08-06_reserveimage_cycle2_f1f2f3_regression_net_a4.md`（RED baseline・14:15:48便への応答）。
本便は★実走のみ★（設計不変・実装ファイル一字も変更せず）。

## §0 lane / worktree / commit 基準

- lane owner = 足軽4号（検証 lane。足軽1号の木には触れず・読取すら行わず）
- worktree = `/tmp/resimg-verify4-cycle2-20260806`（先便から継続・新設せず）
- branch = `ashigaru4-verify-cycle2-20260806`
- 対象commit = `8b95464c0ac5177392b0d9956155abda03bbc499`（家老second殿の下命本文で独立検めた断面と同一。当職は`git cat-file -t`で当該commitが自分の木のobject storeから解決可能な事のみ確認——足軽1号の作業木ディレクトリには一切触れていない）。

### §0-1 手法（★己の木で走らせる★の具体的操作）

1. 当職の木は先便時点でRED baseline patch（`.../gate2-4-handoff-20260806.patch`）を作業木未commit状態で保持していた。これを`git stash push -u`で退避（★discard=非★・復元可能なまま保存。`git checkout --`はuser deny ruleに抵触したため使用せず`git stash`へ切替）。
2. `git diff --name-status HEAD 8b95464`で、当職HEAD(`07b1fbe`)と対象commitの差分ファイルを機械的に列挙（手で選ばず）:
   ```
   M  backend/api/appointment_grid.py
   M  backend/api/appointments.py
   A  backend/db/migrations/booking_concurrency_root.py
   M  backend/services/appointment_service.py
   M  backend/tests/test_appointment_api.py
   D  backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py  ← ★当職の自作test file・8b95464側に存在せぬだけ(別branch系統)、削除は適用せず保持★
   ```
3. 上記5件（当職自作test file を除く）を`git show 8b95464:<path> > <path>`で当職の木へ直接materialize（足軽1号の木を読まず、共有object storeから独立取得）。
4. `git diff --cached --stat 8b95464 -- backend`で全backend/が対象commitと一致する事を確認（差分=当職自作test fileのみ）。
5. 上記状態を`sync(cycle2): materialize 8b95464 ...`としてlocal commit予定（★本便執筆時点でclaude-sonnet-5 classifier一時不通によりcommit未完了・後続で再試行・commit失敗時は本便にsha追記で訂正★）。

### §0-2 sha256（当職実測・断面）

```
54872fbb2f77b562b021342d4a36abea123fb19a784d5daac487362009bda831  backend/services/appointment_service.py
a29d71157a5ff9a9b3ea802f14120e4a6426ec82bd2a30e038b858239b07d51e  backend/db/migrations/booking_concurrency_root.py
ce502023007d1c2433b87cefaf14b364b9ea2fb2924f2e04d1ce9aa9c2df297b  backend/api/appointment_grid.py
34f0dfb2144f7600e30ea2b0f4fe38770e09b3c7551f3ffc17bb0e4cba669843  backend/api/appointments.py
60ce0fa885b2da0c7b776b13156b4dd00ec70e9920ae301de10d0d4cce4495dd  backend/tests/test_appointment_api.py
a9a162c6f06cda645abfc2a7ae4a5dd89ece1358e6de9c5085efc435277622da  backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py（当職自作・349行・変更なし継続）
```
`appointment_service.py`のsha=`54872fbb...`は家老second殿の下命本文で独立測定された値と★一致★（当職も同一断面を読んでいる事の相互確認）。
断面刻= `2026-08-06T15:29:31+09:00`（当職実測`date -Iseconds`）。

## §1 回帰網 test_39〜47 実走結果（8b95464、文字通り・脚色なし）

```
$ /tmp/resimg-stage1-runtime-venv/bin/python -m pytest backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py -v --tb=short
test_39_f1_staff_retry_returns_409_not_same_id_red                          PASSED (documentary)
test_40_f1_staff_retry_should_return_same_id_red                            FAILED
test_45_f1_idempotency_key_interface_absent_red                             FAILED
test_46_f1_mid_sequence_failure_rolls_back_appointment_insert_too           FAILED
test_47_f1_post_commit_side_effects_outbox_unmeasured                       SKIPPED
test_41_f2_fk_check_failure_leaves_schema_committed_red                     FAILED
test_42_f2_dangling_row_survives_failed_migration_documents_defect          PASSED (documentary)
test_43_f3_keyless_replay_should_409_not_silently_succeed_red               PASSED
test_44_f3_keyless_replay_actual_behavior_documents_conflict_with_a1        FAILED
5 failed, 3 passed, 1 skipped
```

★以下、下命が名指した3件（test_40=F1／test_41=F2／test_43=F3）を軸に、
一件ごとに「文字通りの結果」と「その意味（当職の独立追加検証つき）」を分けて記す。
★裁定せず・咎めず。だが『FAILED=未修正』と読むには危険な物が混じっているため、
そのまま丸めずに開いて示す（下命⑸の禁則「仮埋めするな」に従う）★。

## §2 test_40 (F1・下命名指し) — 文字通りFAILED。★然れど別の呼出し形では独立にGREEN確認★

### §2-1 文字通りの結果
```
backend/services/appointment_service.py:268: in create_appointment
    raise HTTPException(status_code=409, detail={..., 'rule': 'double_booking', ...})
```
test_40は`idempotency_key`引数を渡さず`create_appointment`を2回呼ぶ。この形では
`double_booking`(slot claim PK衝突)が先に発火し、依然409で終わる。★これは先便のRED baselineと同一挙動★。

### §2-2 当職の独立検証（★下命の禁則「仮埋めするな」に従い、コード実読で見つけた事実を測る★）
`appointment_service.py`実読（L156-160, L216-321）で、8b95464は`create_appointment`に
`idempotency_key: Optional[str] = None`引数を新設し、渡された場合のみ
`concurrency_root.acquire_idempotency`/`complete_idempotency`(既存booking_concurrency_root.py再利用)
経由でF1のidempotency処理を行う事を確認。★test_40はこの新引数を一切渡していない★
（先便§2-1執筆時点=8b95464登場前にはこの引数自体が存在せず、test_40の呼出し形が
「唯一の呼出し方」だったが、8b95464でinterfaceが増えた事によりtest_40は
★「keyを渡さない場合の挙動」という別の観点の測りに変わった★）。

★独立検証スクリプト実走（当職作成・repo未commit・報告目的の一回性script）★:
```python
first = appointment_service.create_appointment(conn, dict(data), operator="staff-A", idempotency_key="KEY-TEST-1")
retry = appointment_service.create_appointment(conn, dict(data), operator="staff-A", idempotency_key="KEY-TEST-1")
```
実測出力:
```
FIRST: 1 confirmed
RETRY: 1 confirmed SAME_ID= True
ACTIVE_COUNT: 1
```
★F1の4点oracle（first=success/retry=same ID/active=1/409をGREENと数えぬ）は
idempotency_keyを渡す形では成立する★（本部長裁定oracleの想定呼出し形と当職は判ずる。
但し★裁定はせぬ★——「渡さない場合にどうあるべきか」はF1本来のscope外の論点として
軍師second/家老second殿の判断に委ねる）。

### §2-3 結論（⑸GREENの記入）
`test_40`（文字通り・key無し呼出し）= ★FAILED継続（RED）★。
`idempotency_key`を渡す呼出し（本部長oracleが想定する形と当職は解する）= ★GREEN（独立検証済）★。
★両者は別の入力に対する別の観測であり、どちらか一方を「正しいtest_40の答」と当職が決めるのは越権ゆえ、両方を併記する★。

## §3 test_41 (F2・下命名指し) — ★FAILED継続。欠陥は現に存在★（裁定不要・明確）

```
E   AssertionError: F2: fk_check失敗時点でbooking_idempotency/appointment_slot_claimsが
    commit済のまま残った(自己rollback欠如の実測)
E   assert not True
E    +  where True = root_tables_present(<sqlite3.Connection object at ...>)
```
先便§2-2のRED実測（`root_tables_present(conn) == True`が期待に反する）と★完全同一★。
8b95464は`appointment_service.py`にF1のidempotency配線を加えたが、
`booking_concurrency_root.py`自体のfk_check失敗時ロールバック処理には手を加えていない
（当職が §0-1 で機械列挙した diff にも`apply_booking_concurrency_root`本体の変更は現れず）。
`test_42`（欠陥の実在を記録するdocumentary test）も継続PASS=欠陥がなお実在する事の直接証拠。

★⑸GREEN = 該当なし（未修正・零）★。零を零と記す。

## §4 test_43 (F3・下命名指し) — ★文字通りPASSEDだが、★F3が修正された証には成らぬ★（重要・要注意）

### §4-1 文字通りの結果
PASSED。当職が先便§2-3で書いた「現状=早期return成功」のRED期待と逆に、
`booking_service.create_booking`を同一内容で2回呼ぶと2回目は`BookingConflictError`(409)が上がった。

### §4-2 ★然れど、これはF3(idempotency)の修正ではない★
- `git diff --name-status HEAD 8b95464`（§0-1参照）に`backend/services/web_reservation/booking_service.py`
  は★一件も現れない★＝8b95464はweb予約経路(F3)に一切手を加えていない。
- `booking_service.py`を実読（L168-234）した所、`create_booking`にはidempotency判定・
  `existing`早期return・`idempotency_key`引数のいずれも★存在しない★。ある物は
  `_check_conflict`（同clinic・同時間帯の重複を機械的に409拒否する、通常のダブルブッキング防止check）のみ。
- ∴ test_43が拾った「2回目は409」は、★同一内容の再送を idempotent に扱うロジック★ではなく、
  ★同じ時間帯への2件目の予約を無条件に拒む、既存の通常競合checkが偶然一致した結果★である。
  この2つは区別できない状態にある＝★「同一client の意図的retry」と「別clientが同slotを狙った衝突」を
  test_43は見分けていない★（本来のidempotency＝前者はエラーにせず後者はエラーにする、が未実装のまま）。

### §4-3 併せて test_44 の失敗について（先便§2-3の当職自身の記述の訂正）
test_44は先便§2-3で「a1の既存test`test_exact_request_replay_returns_same_appointment_id`が
現状の早期return挙動をGREENで固定している」と当職が書いた前提の上に立ち、その挙動を
再現しようとして書かれたが、★実測=`grep -n "def test_exact_request_replay" backend/tests/web_reservation/test_phase2_2_booking.py` → 0件★（★該当testは当職の木のHEAD・8b95464いずれの正本にも存在しない★）。
∴ ★先便§2-3の当職の記述は、a1の未commit作業木(`/tmp/resimg-cycle2-impl-20260806`)を参照して書かれた物であり、
正本(git commit履歴)には該当挙動が一度も存在しなかった可能性が高い★。当職の落度として明記する
（隠さず・咎めを求めず、以後は正本commitのみを断面として引く）。
実際、当職が§0-1で先便のWIP patchを`git stash`退避した後の`booking_service.py`（HEAD＝正本）は
上記§4-2の通り「early-returnなし・通常conflict checkのみ」であり、早期return挙動自体が
当職の記憶／未commit木に由来する幻影だった可能性が高い。

★⑸GREEN = 該当なし（F3は8b95464の対象外・test_43のPASSは偽陽性risk・裁定はせぬ）★。

## §5 test_45/46（F1付随・当職自作test固有の陳腐化。実装の欠陥ではない）

- `test_45`（idempotency_key引数が存在せずTypeErrorになる事を期待）= ★FAILED（DID NOT RAISE）★
  → 理由=8b95464で引数が実装された（§2-2参照）。★これは「直った」方向のFAILEDであり、退行ではない★。
- `test_46`（`appointment_service.claim_appointment_slots`をmonkeypatchして中断注入）= ★FAILED（AttributeError）★
  → 実測=`grep -n "^def \|claim_appointment" backend/services/appointment_service.py`→
  `claim_appointment_slots`は`appointment_service`直下には無く、`concurrency_root.claim_appointment_slots`
  （`backend.db.migrations.booking_concurrency_root`モジュール側）として呼ばれる形に構造変更されていた。
  ★monkeypatch対象の参照先が古いだけで、atomicity(㈣)そのものは未検証★（当職の今後の課題として残す。
  仮埋めせず「測れていない」とここに明記する）。

## §6 test_47（下命の直接の問い＝⑸post-commit副作用、acquire/complete配線後に実走し得るか）

★実走し得た★（下命の問い「為し得ぬなら理由を書け」に対し＝★為し得た★ので理由でなく結果を記す）。

`appointment_service.py`実読（L241-244）＝`if idem_outcome == "completed": return cached_response`が
INSERT/履歴記録/`log_appointment_action`呼出しより★前段★に位置する事を確認。
∴ 構造上、replay(2回目以降の同一idempotency_key呼出し)は post-commit副作用のコードパスへ
★到達しない★はず、という仮説を当職独立scriptで実測した:

```python
# backend.services.appointment_log_service.log_appointment_action をカウントpatch
first  = appointment_service.create_appointment(conn, dict(data), operator="staff-A", idempotency_key="KEY-PC-1")
retry  = appointment_service.create_appointment(conn, dict(data), operator="staff-A", idempotency_key="KEY-PC-1")
```
実測出力:
```
calls_to_log_appointment_action (module-level count via patched module): 1
SAME_ID: True
```
★first+retry計2回呼んでも`log_appointment_action`は1回しか実行されない=post-commit副作用は
replayで重複しない★（早期returnがpost-commit codeより前段にある構造がそのまま効いている）。
∴ 裁定㈤の懸念（post-commit副作用が retry で重複するのでは）は、当職の実測範囲では
★解消済（重複零）★。ただし本測りは`log_appointment_action`1関数のみを対象とし、
`diagonal_service`/`prediction_service`等の他の後続副作用は個別に確認していない
（同じ早期returnより後段に位置する事はコード読みで確認済のため理屈上は同様のはずだが、
★当職は実測していない物を実測したと書かぬ★——未測のまま残す）。

## §7 writer全数回帰（下命③・既存baseline再走）

```
$ /tmp/resimg-stage1-runtime-venv/bin/python -m pytest \
    backend/tests/test_appointment_api.py \
    backend/tests/test_appointment_service.py \
    backend/tests/web_reservation/test_phase2_2_booking.py \
    tests/test_booking_validator.py -q
108 passed, 2 warnings in 203.84s
```
★退行なし★（先便baselineの113件から108件への減少は、母集団側の変化ではなく
`test_booking_concurrency_root_migration.py`(6件相当)が当職の木のHEAD・8b95464いずれにも
★存在しない事が判明した★ため=`git ls-tree -r 8b95464 --name-only | grep test_booking_concurrency_root_migration`
→ 0件、`git ls-tree -r HEAD` も同様に0件。先便でこのfileを「既存test」として含めていたのは
§4-3と同根の誤り＝a1の未commit木由来。以後の母集団からこのfile名は外し、
★『file不在』を『実装側の欠落』と混同しないよう記す★）。
`test_06_cancelled_slot_reuse`（commit message言及の要修正test）= 個別実行でも★PASSED★確認済。

## §8 七項の埋め（下命⑦形式・本便時点)

⑴ lane owner=足軽4号 ⑵ worktree=`/tmp/resimg-verify4-cycle2-20260806`
⑶ branch=`ashigaru4-verify-cycle2-20260806` ⑷ 修正前RED=先便§2（3 FAILED実測済）
⑸ ★修正後GREEN（8b95464実走・本便）★=
  - F1(test_40)=★文字通りFAILED継続★。ただし idempotency_key を渡す呼出し形では独立検証でGREEN（§2）。
  - F2(test_41)=★FAILED継続・未修正（零のまま）★（§3）。
  - F3(test_43)=★文字通りPASSEDだが偽陽性risk・8b95464はF3に無関係★（§4）。
  - post-commit副作用(㈤/test_47)=★実走できた・重複零を確認（1関数分・限定範囲）★（§6）。
  - writer回帰=108 passed・退行なし（§7）。
⑹ commit=`ce7935b`（当職branch`ashigaru4-verify-cycle2-20260806`内local commit・push零。
   ★classifier一時不通で最初の試行は失敗したが、再試行で完了した事実も併記する（隠さず）★）。
⑺ blob sha=§0-2記載。

## §9 禁則遵守

- 実装ファイルは一字も変更していない（当職の木への`git show 8b95464:<path>`書込みのみ・
  これは対象commitの内容を当職の隔離木へ複製しただけであり、8b95464自体・main・他branchへの書込みは零）。
- 足軽1号の木（`/tmp/resimg-cycle2-impl-20260806`）は一切touchしていない（読取すら行わず）。
- push/PR/main/本番 = 一切なし（local commit止まり、かつ§8⑹の通り本便時点で未完了）。
- `git checkout --`はuser deny ruleに抵触したため使用せず、`git stash`（可逆）で代替した
  旨を§0-1に明記（迂回ではなく別の非破壊的手段への切替）。
