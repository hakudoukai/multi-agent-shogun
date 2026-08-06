# 2026-08-06 Cycle2 独立detector — Gate⑶⑷b⑸ 最終票 (足軽4号)

下命: 家老second msg_20260806_230459_0bb6636b (2026-08-06T23:04:59)。
key=current_order_9_20260806_230300_CYCLE2_DETECTOR。役=★独立detector★(実装せず)。

## 禁則順守

- 足軽1号の実装・worktree(`/tmp/resimg-cycle2-f123-clean-20260806`)・branch(`stage1/reservation-cycle2-f123-idempotency-a1-20260806`)は一度も開いておらぬ。
- push・main・merge・rebase・cherry-pick・DB実環境・患者・本番・deploy=悉く0。
- migration/schema契約の新規・変更=0(既存schemaのみ使用、ephemeral test DBはtmp_path上の使い捨て)。
- freezeの射程=己のworktree一つのみで作業。他の resimg lane(32 dir/file)は不触(読取・書込とも一切行わず)。
- nonce再利用=HONBUCHO-RES-STAGE1-CYCLE2-GATES2-4-20260806-001(新規に作らず)。

## branch / HEAD / dirty (最終断面)

```
$ cd /tmp/resimg-verify4-cycle2-20260806
$ git rev-parse HEAD
63ce0a78a48abe380b13be5cd848e7119d0a7317
$ git status --short
(出力なし = dirty 0)
$ git log --oneline -3
63ce0a7 test(cycle2): gate5 independent RED->target GREEN, true thread concurrency, diagonal booking race, ashigaru4 verify lane
41ef231 test(cycle2): gate4b independent detector (post-commit audit-log static scan), ashigaru4 verify lane
8446000 test(cycle2): gate3 independent detector (function-scoped delegation check), ashigaru4 verify lane
$ date -Iseconds
2026-08-06T23:45:32+09:00
```

branch=`ashigaru4-verify-cycle2-20260806`。着手時base(将軍second殿指定値)=`e88e7582fa2c8d83e4617cec962a5724df8ad695`・dirty=0——着手前に自分で`git status --short`実測して一致を確認済(値の丸写しではない)。以後3commit(gate3/gate4b/gate5)を積んだのみ、production側fileは一切編集しておらぬ(全てtests/配下の新規fileのみ)。

## ★独立の意味の遵守★

三ゲートとも、①「何が満たされておるべきか」を`backend/services/appointment_lifecycle.py`自身のdocstring(委譲先=delegation TARGET、読むのは正当)から立て、②足軽1号の実装ブランチは一切参照せず、③既存の自分の資産(barrier harness・writer/reader ledger)をF2に従い再利用した。

## Gate⑶ — 未委譲0を機械で示す検出

成果物=`backend/tests/detect_undelegated_occupancy_mutation_a4.py`(SHA256=e13185b7e7e4a091a4399805dd562ce897dafeb031d03412b5debaa4dbf1bcff・264行)

方式: AST静的解析。`appointments`テーブルへのUPDATE/INSERT実行箇所を全走査し、occupancy字段(clinic_id/unit_id/start_time/end_time/duration_minutes)に触れる箇所を抽出。★関数単位★で、同一関数内に委譲呼出(`move_appointment_slot`/`create_appointment_with_claim`/`deactivate_appointment`/`reactivate_appointment`/`claim_appointment_slots`/`release_appointment_slots`のいずれか)が在るか判定(当職の初版はfile単位の判定だったが、それでは「同一関数内で新旧併存」を見誤る為、関数単位へ改めた)。

実行結果(測時2026-08-06T23:24:31+09:00):
```
$ python3 backend/tests/detect_undelegated_occupancy_mutation_a4.py
[gate3-detector] scanned 458 files under backend
[gate3-detector] UNDELEGATED occupancy-relevant mutation sites (function calls NO delegation callable): 8
  - backend/api/appointment_detail.py:106 [api_update_detail] UPDATE ['duration_minutes','start_time','unit_id'] (dynamic-schema-derived)
  - backend/api/booking_manage.py:278 [change_booking] UPDATE ['end_time','start_time']
  - backend/api/email_parser.py:108 [_create_appointment_from_parsed] INSERT ['clinic_id','duration_minutes','end_time','start_time']
  - backend/routers/next_appointment.py:69 [book_next_appointment] INSERT ['clinic_id','duration_minutes','end_time','start_time','unit_id']
  - backend/services/diagonal_service.py:116 [create_diagonal_appointment] INSERT ['clinic_id','duration_minutes','end_time','start_time','unit_id']
  - backend/services/diagonal_service.py:145 [create_diagonal_appointment] INSERT ['clinic_id','duration_minutes','end_time','start_time','unit_id']
  - backend/services/diagonal_service.py:260 [update_linked_appointment] UPDATE ['end_time','start_time']
  - backend/services/diagonal_service.py:275 [update_linked_appointment] UPDATE ['end_time','start_time']
[gate3-detector] RESIDUAL raw SQL (function ALSO calls a delegation callable): 2
  - backend/api/appointment_grid.py:761 [move_appointment] UPDATE ['end_time','start_time','unit_id']
  - backend/services/web_reservation/booking_service.py:408 [update_booking] UPDATE ['clinic_id']
[gate3-detector] RESULT: RED (未委譲 != 0)
EXIT=1
```

★RED = 8件(現在のbase HEAD e88e758時点)★。副次発見=`email_parser.py:108`の検出結果に`unit_id`が含まれぬ事を機械的に確認——これは当職の以前の独立票(`docs/incident_logs/2026-08-06_ledger_site_reachable_case_a4.md`§2-1、`unit_id`列がINSERT列一覧から欠落しIntegrityErrorで恒常的に到達不能、との手動実読による発見)と、★全く別の方法(AST走査)で一致★した。ただし到達可能性=0かの動的裏取り(実行してIntegrityErrorを確認)は本gateの静的検出の射程外であり、別途要。

## Gate⑷b — post-commit durability の検出

成果物=`backend/tests/detect_post_commit_audit_log_a4.py`(SHA256=a6e40bd115fc497551bbf0de21d5a08eed5344e3ba832c5e08d1f651a0640d56・146行)

方式: AST静的解析。関数内でcommit(`.commit()`メソッド、または`conn.execute("COMMIT")`の生SQL両形式)より★後の行★に監査ログ呼出(`log_appointment_action`/`log_audit`)が在るかを判定。`appointment_lifecycle.py`自身の`create_appointment_with_claim`docstring(194-205行)が明文化する「on_persistedは commit★前★に呼ばれるフック——post-commitだとcrash時に副作用が恒久欠落する」契約に対する違反候補を機械抽出する。

実行結果(測時2026-08-06T23:30:22+09:00):
```
$ python3 backend/tests/detect_post_commit_audit_log_a4.py
[gate4b-detector] scanned 459 files under backend
[gate4b-detector] functions with commit-before-audit-log (candidate durability gap): 9
  - backend/api/appointment_grid.py [change_appointment_status] commit@L620 then audit-log@L[629]
  - backend/api/appointment_grid.py [_execute_cancel] commit@L865 then audit-log@L[876]
  - backend/api/documents.py [update_document_status] commit@L460 then audit-log@L[480]
  - backend/api/documents.py [finalize_document] commit@L1490 then audit-log@L[1494]
  - backend/api/documents.py [void_document] commit@L1584 then audit-log@L[1588]
  - backend/api/documents.py [approve_proxy_input] commit@L1647 then audit-log@L[1651]
  - backend/services/appointment_service.py [update_appointment] commit@L484 then audit-log@L[498]
  - backend/services/appointment_service.py [cancel_appointment] commit@L586 then audit-log@L[592]
  - backend/services/appointment_service.py [transition_status] commit@L645 then audit-log@L[708]
[gate4b-detector] RESULT: RED (post-commit audit-log candidates != 0)
EXIT=1
```

★RED = Cycle2(予約)射程内5件★(change_appointment_status/_execute_cancel/update_appointment/cancel_appointment/transition_status)。`documents.py`の4件は別ドメイン(書類承認)ゆえ★母集団に含めず別記のみ★(検出器は`log_appointment_action`/`log_audit`双方を対象にした為、副産物として拾った——スコープを恣意的に絞り込むより、機械的に拾い足切りは人手で行う方が安全と判断)。`appointment_grid.py:change_appointment_status`(旧606行付近)は`conn.execute("COMMIT")`直後のコード自身のコメントが「操作ログ記録（Phase 0 — トランザクション外）」と明記しており、本gateの検出対象である事を当該コード自身が追認している。

★静的順序ベースの代理指標である事の限界を明記★: 本検出は「commit()より後ろの行にaudit呼出がある」ことのみを見ており、crash-and-replayの実動作までは検証していない(gate⑸のバリア技法とは別の粒度)。

## Gate⑸ — thread/process+barrierの真並行、old exact RED→target GREEN

成果物=`backend/tests/test_diagonal_barrier_concurrency_a4.py`(SHA256=8c94fcca4925d1e5534c7e8c52022bdeb62a21819e1dd1f5840d235f304a5ff3・275行)

新規シナリオ(足軽1号の実装を見ずに、gate⑶自身の発見から独自に立てた): `diagonal_service.py:create_diagonal_appointment`は委譲呼出が皆無(gate⑶で確認済)——★占有字段への並行書込みを止める仕組みが無い★はず、という仮説をbarrierで実証した。既存の`test_reserveimage_cycle2_barrier_concurrency_a4.py`(当職の前工区資産)のharness(`_run_two_barrier_workers`/`_future`)をF2に従い再利用(新設せず)。

### RED (現行未修正コードそのもの)

初稿はworker2体を同一start_timeで走らせたが、実測=success1・IntegrityError(`uq_appointments_active_exact_start`部分UNIQUE index、既存suite既知の「二重guard」現象と同型)——これは既存fileが既に文書化した現象そのものであり、当職はその既知パターンに従いoffset overlap(15分ずれ)へ切替えて再測した。

```
$ python3 -m pytest backend/tests/test_diagonal_barrier_concurrency_a4.py::test_diagonal_RED_true_concurrent_same_slot_both_succeed -v -s
F2BARRIER_DIAGONAL_RED_SUCCESS=2 ERRORS=[]
F2BARRIER_DIAGONAL_RED_ACTIVE=4
PASSED
```

★RED実測=両者成功(success=2・active=4)★。委譲が皆無ゆえ、真の並行下で同一2ユニットへの部分重複が一切止まらぬ事を実証。

### TARGET GREEN (test-local reference、足軽1号の実装ではない)

`_diagonal_create_with_target_claim`(本file内のみに定義、`backend/services/`へは一切適用せず)——同一INSERTロジックを再構築した上で、`appointment_lifecycle.py`の他path全てが使う既存primitive`concurrency_root.claim_appointment_slots`を両レコードに対し呼ぶ。「目標契約が既存primitiveで達成可能である事」の証明であり、足軽1号が実際に何を実装したかへの言及ではない。

```
$ python3 -m pytest backend/tests/test_diagonal_barrier_concurrency_a4.py::test_diagonal_TARGET_GREEN_true_concurrent_same_slot_second_rejected -v -s
F2BARRIER_DIAGONAL_GREEN_SUCCESS=1 INTEGRITY_ERRORS=1 OTHER_ERRORS=0
F2BARRIER_DIAGONAL_GREEN_ACTIVE=2
PASSED
```

★GREEN実測=一方のみ成功(success=1・敗者側=IntegrityError・active=2)★。同一harnessでRED→GREEN対を示した(harnessを変えてGREEN化してはおらぬ)。

### 回帰確認

既存`test_reserveimage_cycle2_barrier_concurrency_a4.py`(5 test)を同断面で再実行、5/5 PASS(退行なし)を確認:
```
$ python3 -m pytest backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py -v
5 passed in 21.89s
```

## 結べぬ物 (推して埋めず)

- gate⑶の8件のうち`email_parser.py:108`が「真に到達可能か(occupancy-race母集団の一員か)」は静的検出の射程外(動的裏取り要)。
- gate⑷bは順序ベースの代理指標であり、9件(Cycle2射程5件+documents.py 4件)いずれも「crashで実際に副作用が失われる」事の実行時証明はしていない(gate⑸相当のcrash-and-replay proofが要る、47b修正時の`test_47a/b/c`と同型の技法が既に存在する事は把握しているが、本工区では新規に書いていない)。
- gate⑸のTARGET GREENは当職独自の参照実装であり、足軽1号の実装が同じ結果を出すかは★別途・実装完了後に成果物同士を突合すべき事項★(本票の射程外、実装を読まぬ禁の順守)。

## 己の手で為した事

- `/tmp/resimg-verify4-cycle2-20260806`のHEAD/dirtyを着手前に`git rev-parse HEAD`/`git status --short`で自分で確認(値が令と一致)。
- `backend/services/appointment_lifecycle.py`全文を読み、委譲先4関数+2 primitiveの正確な名前・シグネチャ・docstringの契約(on_persistedフック=commit前呼出)を確認。
- `backend/api/appointment_detail.py`を読み、動的UPDATE(dynamic SET clause)とPydantic Request modelのfield一覧を実読で確認。
- gate⑶検出器を作成、初版(file単位)の欠陥に気付き関数単位(function-scoped)へ自ら改修、実行して8件+residual2件を実測。
- `backend/services/diagonal_service.py`全文を読み、`update_linked_appointment`/`create_diagonal_appointment`に委譲呼出が一切無い事を`grep`で確認(claim_appointment_slots等6callable、いずれも0 hit)。
- gate⑷b検出器を作成、実行して9件を実測、うち5件がCycle2射程・4件が別ドメインである事を`documents.py`該当行を実読して判別。
- gate⑸ test新設、初稿の欠陥(exact-time二重guardによる偽陰性)を実測で発見し自己訂正、offset overlapへ切替えて再実測、RED(success=2)→target GREEN(success=1)対を実証。
- 既存barrier suite 5 testを同断面で再実行し回帰なしを確認。
- 3回のlocal commit(push無し)。全成果物のsha256sumを自分で実測(下記)。

## 令⑥ (監査発注三行)

- 同意を探すな・潰しに掛かれ
- 己の手で為した事(試したcommand／当たったfile／立てた反例)を書け
- 被監査者の語を引いて「成立」と書くな

## 成果物 (full path + 64桁SHA)

- `/tmp/resimg-verify4-cycle2-20260806/backend/tests/detect_undelegated_occupancy_mutation_a4.py`
  sha256=e13185b7e7e4a091a4399805dd562ce897dafeb031d03412b5debaa4dbf1bcff・264行
- `/tmp/resimg-verify4-cycle2-20260806/backend/tests/detect_post_commit_audit_log_a4.py`
  sha256=a6e40bd115fc497551bbf0de21d5a08eed5344e3ba832c5e08d1f651a0640d56・146行
- `/tmp/resimg-verify4-cycle2-20260806/backend/tests/test_diagonal_barrier_concurrency_a4.py`
  sha256=8c94fcca4925d1e5534c7e8c52022bdeb62a21819e1dd1f5840d235f304a5ff3・275行
- branch=`ashigaru4-verify-cycle2-20260806`・HEAD=`63ce0a78a48abe380b13be5cd848e7119d0a7317`・dirty=0(local commitのみ、push無し)
- 本報告書: `docs/incident_logs/2026-08-06_cycle2_independent_detector_gates345b_a4.md`(主repo、git管理下)

## 測時・器・範囲

測時=2026-08-06T23:04:59(下命受領)〜23:45:32(本票起筆)JST／
器=git worktree(既存・新設せず)・AST(python3 ast module)・pytest・sha256sum・grep(claim/release/move/create/deactivate/reactivate呼出確認)／
範囲=`backend/**/*.py`(458〜459ファイル、gate毎に対象module除外あり、本文記載の通り)。
足軽1号の実装・worktree・branchは一度も開いておらぬ。読めぬ物(足軽1号の成果物)につき「以上」。
