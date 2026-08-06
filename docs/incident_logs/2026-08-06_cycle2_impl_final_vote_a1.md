# 2026-08-06 Cycle2 実装 最終票 (足軽1号)

下命: 家老second `current_order_12_20260806_230300_CYCLE2_IMPL`(2026-08-06T23:03:00) 系列
（順を定めた最終令=`msg_20260806_234114_de773959`23:41:14）。役=★実装★。
worktree=`/tmp/resimg-cycle2-f123-clean-20260806`／branch=`stage1/reservation-cycle2-f123-idempotency-a1-20260806`。
nonce=`HONBUCHO-RES-STAGE1-CYCLE2-GATES2-4-20260806-001`(再利用・新規に作らず)。

## 断面 (測時=2026-08-07T00:09:49+09:00 JST 実値)

```
HEAD  = 14cad3a42c20c34ac1f93e4f334da5c85f195dd5
branch = stage1/reservation-cycle2-f123-idempotency-a1-20260806
dirty  = 0 (git status --short 出力なし)
base   = a7c21a9143d9ec45fb0e9cc7f544a408f32ecb77 (令の base HEAD と一致)
```

## 禁則順守

push・main・merge・rebase・cherry-pick・DB実環境・患者・本番・deploy=悉く0。migration/schema契約の新規・変更=0(既存schemaのみ)。git gc/prune/reflog expire=0・index/objects不触。freezeの射程=己のworktree一つのみ、他resimg lane不触。

## 未閉鎖三つの現況 (⑶⑷b⑸)

### ⑶ 全occupancy writerの共通domain command委譲

成果物: commit `099288f` (層外writer8箇所委譲) + `0c523d1` (appointment_detail.py残り1箇所・case㈡完了)。

★独立検証★: 足軽4号の独立detector(`docs/incident_logs/2026-08-06_cycle2_independent_detector_gates345b_a4.md`)成果物
`backend/tests/detect_undelegated_occupancy_mutation_a4.py`(sha256=`e13185b7e7e4a091a4399805dd562ce897dafeb031d03412b5debaa4dbf1bcff`)を
当職worktreeへ★byte-identicalに複写確認の上★実行(実行後は削除・dirty=0へ復元。当職branchへは追加・commitせず)。

```
$ date -Iseconds
2026-08-06T23:58:24+09:00
$ python3 backend/tests/detect_undelegated_occupancy_mutation_a4.py
[gate3-detector] UNDELEGATED occupancy-relevant mutation sites: 1
  - backend/api/email_parser.py:108 [_create_appointment_from_parsed] INSERT ...
[gate3-detector] RESIDUAL raw SQL (co-existing old+new path): 7
[gate3-detector] RESULT: RED (未委譲 != 0)
EXIT=1
```

★母集団の対応(base実測=8件undelegated・実測時点=1件へ減)★。

- **UNDELEGATED 1件(email_parser.py:108)** = ★到達不能を当職が独立に動的検証済★。
  `appointments.unit_id INTEGER NOT NULL REFERENCES units(unit_id)`(`backend/db/migrations/appointment_tables.py:81`実読で確認)に対し
  `_create_appointment_from_parsed`のINSERT列一覧に`unit_id`が欠落(`backend/api/email_parser.py:109-122`実読で確認)。
  当職自身のworktree・現HEADのコードに対し実際にsqlite3で最小テーブルを作りINSERTを走らせた結果:
  ```
  return value: None
  appointments row count after call: 0
  ```
  ★IntegrityErrorが`except Exception: return None`で握り潰され、行は一切insertされず★——occupancy-race母集団の一員たり得ぬ。
  （足軽4号の先行独立票`docs/incident_logs/2026-08-06_ledger_site_reachable_case_a4.md`の同結論と、★別の実行(当職branch上・別動的test)で一致★）
  ∴ **未委譲reachable case = 0**。

- **RESIDUAL raw SQL 7件** = 全件を当職が実読で確認。悉く同一パターン=
  `appointments`表への★主記録UPDATE/INSERT(不可避・delegation callableの射程外)★の直後・同一transaction内で
  `move_appointment_slot`/`claim_appointment_slots`(★占有ロックの実体=appointment_slot_claims表を扱う唯一の機構★)を呼ぶ。
  `move_appointment_slot`自身のdocstring(`appointment_lifecycle.py:149-154`)が「status/duration等のUPDATE自体は呼び手ごとに
  異なる為ここでは行わない」と明記——★raw SQLはappointmentsの主記録更新・delegationはslot claim同期の分業であり、
  occupancy-race二重書込みには当たらぬ★(7箇所全て`appointment_detail.py:116`/`appointment_grid.py:768`/
  `booking_manage.py:278`/`next_appointment.py:69`/`diagonal_service.py:276,300`/`web_reservation/booking_service.py:408`
  を個別に実読し確認)。
  ∴ **residual raw SQL = 0 occupancy-race相当 (非occupancy の根拠あり)**。

**Gate⑶ semantic predicate (令23:41:14指定) = 充足**。

### ⑷b post-commit durability (5 site transaction)

成果物: commit `56b08af`(残5箇所を同一commit/rollback単位へ)＋専用RED/GREEN test
`backend/tests/test_post_commit_durability_5sites_a1.py`
(sha256=`52112ae523289e8f7a2511c18f757d1f511101a18fac0df896c670bdb48cf2ab`・445行)。

RED実測(56b08af本文に記録・git stash往復で旧コード再現): 5/5 FAILED。
GREEN実測(当職が本票起筆直前に再実行):
```
$ python3 -m pytest backend/tests/test_post_commit_durability_5sites_a1.py -q
.....
5 passed, 1 warning in 13.67s
```

★独立検証★: 足軽4号detector `detect_post_commit_audit_log_a4.py`
(sha256=`a6e40bd115fc497551bbf0de21d5a08eed5344e3ba832c5e08d1f651a0640d56`)を同様に複写・実行(実行後削除):

```
$ date -Iseconds
2026-08-07T00:00:45+09:00
$ python3 backend/tests/detect_post_commit_audit_log_a4.py
[gate4b-detector] functions with commit-before-audit-log: 5
  - documents.py×4 (別ドメイン=書類承認、Cycle2母集団外)
  - appointment_service.py [transition_status] commit@L661 then audit-log@L[727]
[gate4b-detector] RESULT: RED
EXIT=1
```

Cycle2射程5件(change_appointment_status/_execute_cancel/update_appointment/cancel_appointment/transition_status)のうち
4件は検出0件へ落ちた。残る`transition_status`のヒットを実読で検証:

- `L661`の`conn.commit()`は`ALTER TABLE appointments ADD COLUMN treatment_started_at`(schema自動追加)専用のcommitで、
  `git blame`実測=`^62f4a2e (iincho 2026-08-06 00:59:03)`——★Cycle2着手前からの既存コード・当職一字も変更せず★。
  audit logや状態遷移そのものとは無関係(target_status=="in_progress"かつ列未存在の時のみ発火する条件分岐の中)。
- ★実際の状態遷移commit★は同関数`L742`の`conn.commit()`一箇所のみ。`log_appointment_action(..., auto_commit=False)`
  呼出(`L727`)はこの`L742`より★前★にあり、両者は同一transaction・単一commitへ収束(`L749-752`のBaseException rollbackで保護)。
  ∴ **状態+監査ログのatomicity契約は充足**——detectorのヒットは「関数内のcommit呼出を線形に走査する」という
  検出器自身が明記した限界(「静的順序ベースの代理指標」)由来の偽陽性であり、本工区の対象範囲(Cycle2状態遷移の
  atomicity)に対する未修正箇所ではない。

**Gate⑷b Cycle2射程 = 充足(偽陽性1件を当職が実読+git blameで独立に切り分け)**。

### ⑸ thread/process+barrierの真並行、old exact RED → target GREEN

成果物: commit `14cad3a` `backend/tests/test_true_concurrency_barrier_a1.py`
(sha256=`ac66ccda6dc35e0232d3e22cf993dcf92c67743cde14b23232fb87409a2ff9ac`・176行)。

threading.Barrierで2threadの実行開始点を同期、offset overlap構成でold(未適用)→RED(2threadとも成功=二重予約)、
target(適用済)→GREEN(1threadのみ成功)を実測。5回連続実行で安定(commit本文記載)。本票起筆直前の再実行:

```
$ python3 -m pytest backend/tests/test_true_concurrency_barrier_a1.py -q -v
backend/tests/test_true_concurrency_barrier_a1.py .. [100%]
2 passed in 6.51s
```

**Gate⑸ = 充足**。

## テスト全体 (SKIP=FAIL規則・未完了と明記)

```
$ python3 -m pytest backend/tests/ -q --ignore=backend/tests/e2e --ignore=backend/tests/test_watchdog_hook.py \
  --ignore=backend/tests/test_migration_036_recurrence_guard_probe.py \
  -k "appointment or booking or diagonal or reservation or slot or claim or idempotency or concurrency or prediction or 47b or true_concurrency" -rs
339 passed, 6 skipped, 2909 deselected, 3 warnings in 423.16s
```

6 skip内訳=全件environment/資産欠落・Cycle2範囲外:
- `test_qr_processor.py:19`×1 = `qrcode`パッケージ未導入
- `test_receipt_mailer_stamp.py`×5 = 実物印鑑PNG(`07_kashii_teriha.png`)欠落

★本工区起因ではない事の確認★: `git log --oneline a7c21a9..14cad3a -- backend/tests/test_qr_processor.py
backend/tests/test_receipt_mailer_stamp.py backend/receipt_mailer/` = 0件(当職commitはこれらfileに一切触れておらぬ)。
`qrcode`未導入・PNG欠落は当職のtest実行環境自体の欠落であり、base(a7c21a9)でも同一条件下で同一skipが発生したはずと推定される
(base自体でのpytest再実行はF2=既存証拠再利用の趣旨に照らし、diffが0件である事実を根拠に省略した——★推してはおらぬが、
base側で改めて実測してはおらぬ事は明記する★)。

★CLAUDE.md Test Rule 1「SKIP=FAIL」に従い、本票は「テスト完了」とは書かぬ★。339 passed / 0 failed だが SKIP≥1 ゆえ
**未完了**として報告する。上記6件がCycle2範囲外である事の根拠(git logの差分0件)は示したが、判定はgunshi-secondへ委ねる。

## 判らぬ・別枠 (第四値)

- base(a7c21a9)側でも同一6 skipが起きるかは★実測しておらぬ★(未検討・推してもいない)。
- Gate⑷bの`documents.py`4件(別ドメイン)は本工区の射程外のまま未修正——足軽4号票でも同じ扱い(Cycle2母集団に非ず)。
- Gate⑶ residual 7件の「occupancy-race相当ではない」判定は当職の実読による——第三者(gunshi-second)の追加検証を要する。

## 己の手で為した事

- `git rev-parse HEAD` / `git status --short` を自分で実測(令のbase値と一致確認)。
- 足軽4号の2detector scriptを`sha256sum`でbyte-identical複写確認の上、自分のworktree・現HEADに対し実行(検証後は削除しdirty=0へ復元・ashigaru4のbranchは一度も開いていない)。
- `email_parser.py`のINSERT列一覧と`appointment_tables.py:81`のNOT NULL制約を自分で実読、かつsqlite3で最小テーブルを組み実際にINSERTを走らせ、IntegrityErrorで行が0のまま返る事を動的に実測(足軽4号票の結論を当職が別途独立確認)。
- Gate⑶ residual 7箇所を`sed`で個別に実読し、`move_appointment_slot`のdocstringと突合して「主記録UPDATE+claim同期delegation」の分業パターンである事を確認。
- Gate⑷bの残1件(`transition_status`)を実読し`git blame`で該当commitの`L661`が当職着手前(2026-08-06 00:59:03・iincho)からの既存DDLコードである事を確認、真の状態遷移commit(`L742`)との位置関係を実読で特定。
- `test_post_commit_durability_5sites_a1.py`(5 test)・`test_true_concurrency_barrier_a1.py`(2 test)を本票起筆直前に自分で再実行しGREENを確認。
- filtered pytest suite(2909 deselected分含む全collect)を`-rs`付きで再実行し、6 skipの理由文言を自分で読み、該当fileの`git log`差分が0件である事を自分で確認。

## 令⑥ (監査発注三行・遵守)

- 同意を探すな・潰しに掛かれ
- 己の手で為した事(試したcommand／当たったfile／立てた反例)を書け
- 被監査者の語を引いて「成立」と書くな

## 成果物 (full path + 64桁SHA)

- `/tmp/resimg-cycle2-f123-clean-20260806/backend/tests/test_post_commit_durability_5sites_a1.py`
  sha256=`52112ae523289e8f7a2511c18f757d1f511101a18fac0df896c670bdb48cf2ab`・445行 (commit `56b08af`)
- `/tmp/resimg-cycle2-f123-clean-20260806/backend/tests/test_true_concurrency_barrier_a1.py`
  sha256=`ac66ccda6dc35e0232d3e22cf993dcf92c67743cde14b23232fb87409a2ff9ac`・176行 (commit `14cad3a`)
- branch=`stage1/reservation-cycle2-f123-idempotency-a1-20260806`・HEAD=`14cad3a42c20c34ac1f93e4f334da5c85f195dd5`・dirty=0
- 本報告書: `docs/incident_logs/2026-08-06_cycle2_impl_final_vote_a1.md` (主repo、git管理下)

## 測時・器・範囲

測時=2026-08-06T23:03:00(下命受領)〜2026-08-07T00:09:49(本票起筆時点断面)JST／
器=git・pytest・sha256sum・python3(動的検証script)・grep・sed・git blame／
範囲=`/tmp/resimg-cycle2-f123-clean-20260806`(worktree一つのみ)。他resimg laneは不触。
