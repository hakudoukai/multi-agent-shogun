# Gate3 semantic transition A-E reachability matrix — 新target 引き直し・動的検証（独立・足軽4号）

- 令: `current_order_11_20260807_015000_MATRIX_ON_NEW_TARGET`（家老second 発 2026-08-07T01:50、msg_20260807_015021_0c9cb6a0）
- 測時: 2026-08-07T02:10:17+09:00（本票筆記完了の実測時刻・`date -Iseconds`）
- target: `4a0e9036ed94022d79baa4a1e2cf88d5827eec12`（当職 己の手で `git rev-parse HEAD` 実測・写さず）
- worktree: `/tmp/resimg-verify4-cycle2-matrix2-20260807`（`git worktree add --detach` で当職が新規に立てた別木・a1の木 `/tmp/resimg-cycle2-f123-clean-20260806` は一度も書込んでおらぬ）
- HEAD不変証明: 本票作成の全操作後 `git rev-parse HEAD`=`4a0e9036ed94022d79baa4a1e2cf88d5827eec12`（不変）・`git diff --stat`=空（tracked file 変更0）・`git status --short`=untracked 2件のみ（下記§5列挙・commit 0）
- mode: 実装fix 0・commit 0・push 0・merge 0。動的検証の為にのみ、一時的に tracked file を親commit版へ上書き→RED実測→`git checkout --`で復元、という手順を1回行った（下記§2-1・a1が「git stash」と称した手法と同型。復元後 diff 空を確認済）。

## §0 前回票との関係・母集団の再宣言

前回票（`2026-08-07_gate3_reachability_matrix_transitions_a-e_a4.md`、base=`e88e7582`）から本票の間に **10 commit** が同一ファイル群へ入っており（`git log --oneline e88e7582..4a0e9036 -- backend/api/appointment_detail.py backend/api/booking_manage.py backend/services/diagonal_service.py backend/services/appointment_service.py backend/services/appointment_lifecycle.py` で実測）、旧票の C-4/C-5/C-6（未委譲）判定は **現行 target ではもはや成立せぬ**。∴ 令の通り「引き直す」＝旧票の結論を継がず、母集団から取り直した。

母集団＝`/usr/bin/grep -rn -i "UPDATE appointments" backend --include="*.py"`（tests/__pycache__/_archive 除く、23 hit・全件目視で occupancy/status/metadata 何れの列を触るか分類）＋ gate3 detector（当職の既製作、今回は本worktreeへ**未追跡ファイルとして**複製し実行のみ・commitせず）の再走・突合。

## §1 定義（変更なし・前回票と同一）

```
A: active   -> inactive                                = release
B: inactive -> active                                  = claim
C: active   -> active, occupancy fields changed         = atomic reassign
D: active   -> active, occupancy fields unchanged        = no slot-op
E: inactive -> inactive                                  = no slot-op
```
active/inactive の実体＝`ACTIVE_SQL = "status NOT IN ('cancelled','no_show')"`。occupancy fields = {clinic_id, unit_id, start_time, end_time, duration_minutes}。当職の gate3 detector（既製作）はこの occupancy fields のみを述語とし、**status 列のみの変化は検出圏外**（設計上の scope・欠陥ではない）——本票 §3 で言う「射程外」の実体はこれ。

## §2 gate3 detector 再測（陽性対照）

```
[gate3-detector] scanned 458 files under backend
[gate3-detector] UNDELEGATED occupancy-relevant mutation sites: 1
  - backend/api/email_parser.py:108 [_create_appointment_from_parsed] INSERT ...
[gate3-detector] RESIDUAL raw SQL: 7
  - appointment_detail.py:116 / appointment_grid.py:768 / booking_manage.py:278 /
    next_appointment.py:69 / diagonal_service.py:276,300 / web_reservation/booking_service.py:408
[gate3-detector] RESULT: RED
```
（実行=2026-08-07T02:0x、exit=1）。a1 の commit メッセージが申告した「未委譲1・residual7・本commit前と同値」と **当職の独立再測で一致**（数値の丸写しではなく、当職が己の detector を己の手で再実行した結果）。

## §2-1 E-3 guard の動的検証（★静的な語の有無でなく、動かして測った★）

### GREEN（現行 target・当職が己で再実行、a1の申告を鵜呑みにせず）
```
backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py::test_move_appointment_slot_rejects_inactive_appointment[cancelled] PASSED
backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py::test_move_appointment_slot_rejects_inactive_appointment[no_show] PASSED
backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py::test_move_appointment_slot_still_allows_active_appointment PASSED
backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py::test_booking_manage_change_booking_blocks_move_of_cancelled_appointment PASSED
4 passed in 12.73s
```

### RED（陽性対照・当職が独立に作った・guard を親commit版へ差し戻して再測）
`git show HEAD^:backend/services/appointment_lifecycle.py > backend/services/appointment_lifecycle.py`（guard 19行を除去した親版で working tree を上書き・git diff で確認済）→ 同一4 testを再実行:
```
test_move_appointment_slot_rejects_inactive_appointment[cancelled] FAILED (DID NOT RAISE ValueError)
test_move_appointment_slot_rejects_inactive_appointment[no_show]   FAILED (DID NOT RAISE ValueError)
test_move_appointment_slot_still_allows_active_appointment         PASSED（陽性対照=guardがactive予約を巻き込んでおらぬ事も確認）
test_booking_manage_change_booking_blocks_move_of_cancelled_appointment FAILED (DID NOT RAISE ValueError)
3 failed, 1 passed in 19.75s
```
→ 直後 `git checkout -- backend/services/appointment_lifecycle.py` で復元、`git diff --stat`=空・HEAD不変を確認。

★結論★: E-3 guard は **動的に RED→GREEN が当職独自の再測で成立**。a1 の申告（280 passed/0 failed 等）を鵜呑みにせず、当職は E-3 に絞って独立に RED を再現した。

## §3 貴殿の器（occupancy field のみ）の射程外に何が残るか（★令②★・消さず維持）

E-3 guard は `move_appointment_slot` 一箇所への一元化であり、**その関数が呼ばれる経路のみ**を保護する。gate3 detector の述語（occupancy field を touch するか）と E-3 guard の保護範囲は共に「occupancy 変更を伴う経路」に閉じており、**status 列のみを書き換え、occupancy に一切触れず、かつ move_appointment_slot を経由しない経路**は、E-3 fixの後もなお **完全に射程外**のままである。

★現に1件、動的に実在を確認した★（詳細は §4-B）:

- `appointment_grid.py` `change_appointment_status` の "booked" 分岐（`_FRONT_TO_BACK_STATUS["booked"]=("confirmed", None)`）は、対象行の現況を問わず raw UPDATE で `status='confirmed'` へ書き換える。cancelled 行がこの経路で復元されても `move_appointment_slot`/`claim_appointment_slots` の**いずれも呼ばれぬ**——E-3 guard の射程は「move_appointment_slot を呼ぶ経路」ゆえ、そもそも呼ばれぬ経路には効きようがない。★E-3 fix は既存の射程（occupancy 変更経路）を固めたに過ぎず、射程そのものを広げてはおらぬ★（貴殿=当職の器と同型の限界を、fix 自身も引き継いでいる）。

★令の通り、之を『無い』事にはせぬ★。本件は §4-B で dynamic に実測した独立の bug 候補である。

## §4 status-only 3件（旧票 A-4/A-5/B-2）が 述語③の母集団へ移った後どう扱われたか（★令③★）

前回票の行番号は base `e88e7582` 当時のもの。新 target では該当行の位置・実装が変わっている（§0 参照）ので、以下は現在の行番号・現在の実装で再対応させた。

### A. `diagonal_service.py` `cancel_linked_appointment`（旧票A-4・旧base行317）— ★委譲済に移行・GREEN確認済★

現行実装（新target行355）: `cancel_both=True` 分岐内で `appointment_lifecycle.deactivate_appointment` を呼ぶよう改修済（当職が code を実読して確認）。既存test `test_layer_outside_writer_delegation_a1.py::test_diagonal_cancel_both_releases_slot_claims` を当職が再実行:
```
PASSED
```
★動的確認済★: 両方キャンセル後、両appointmentの `appointment_slot_claims` が実際に0件（解放済）。

### B. `diagonal_service.py` `propagate_status`（旧票A-5・旧base行375）— ★直接委譲(release_appointment_slots)に移行・GREEN確認済★

現行実装（新target行410-431）: raw UPDATE で status/visit_status を書いた直後、`target_status == "no_show"` の場合に限り `concurrency_root.release_appointment_slots(conn, linked_id)` を**直接**呼ぶよう改修済（`deactivate_appointment` 経由ではないが、同じ保護 primitive を直接呼んでおり、保護効果としては同等）。既存test `test_diagonal_propagate_no_show_releases_linked_slot_claims` を当職が再実行:
```
PASSED
```
★動的確認済★: no_show 連動後、linked appointment の `appointment_slot_claims` が実際に0件（解放済）。`arrived` 連動時は release 呼出なし（ACTIVE_SQL 上 arrived は active のまま＝D-class・呼ばぬのが正）。

### C. `appointment_grid.py` `change_appointment_status` "booked" 分岐（旧票B-2・旧base行534、新targetでも同一行534）— ★未委譲のまま・GREEN化されておらぬ★

★述語③の母集団（=呼び手側 guard/delegation 一元化の対象）へは移されておらぬ★。E-3 fix の対象4箇所（appointment_service.update_appointment / appointment_detail.api_update_detail / booking_manage.change_booking / diagonal_service.update_linked_appointment）に本経路は含まれておらぬ——之は当職の当て推量ではなく、a1 commit本文に明記された対象4箇所を当職が実際に grep して確認した事による（4箇所とも `move_appointment_slot` 呼出を code 上で確認済・§2 detector residual 出力とも一致）。`appointment_grid.py` の "booked" 分岐は元来この4箇所に含まれておらず、当職が§4-B（下記）で新たに動的実測した。

## §4-B 動的実測（新規発見・令④「証拠は動的に」準拠）

### 陽性対照（正しい経路は claim を作る事の確認）

cancelled 予約へ `PUT /api/appointments/{id}/status` body `{"status":"arrived"}` を送信（`arrived` は `_FRONT_TO_BACK_STATUS` 上 `new_status=None` ゆえ `elif apt["status"]=="cancelled":` 分岐＝`reactivate_appointment` を正しく通る）:
```
PUT_STATUS_ARRIVED_HTTP_CODE=200
AFTER_ROW={'status': 'confirmed', 'visit_status': 'arrived'}
AFTER_CLAIMS=[<2 rows>]
VERDICT=POSITIVE_CONTROL_OK
```
★reactivate_appointment 経由では claim が実際に作られる事を確認★。

### 陰性実測（"booked" 分岐は claim を作らぬ事の確認）

同じ前提（cancelled 予約）へ `PUT /api/appointments/{id}/status` body `{"status":"booked"}` を送信（`booked` は `new_status="confirmed"` が truthy ゆえ、`apt["status"]=="cancelled"` チェックに到達する**前**に `elif new_status:` 分岐で raw UPDATE され、reactivate 分岐を素通りする）:
```
BEFORE_CLAIMS(cancelled)=[]
PUT_STATUS_BOOKED_HTTP_CODE=200
AFTER_ROW={'status': 'confirmed', 'visit_status': None}
AFTER_CLAIMS=[]
VERDICT=B2_STILL_UNGUARDED: status flipped to confirmed via raw UPDATE, NO appointment_slot_claims row created
```
★HTTP 200 で成功応答・status は active('confirmed') に変わるが、`appointment_slot_claims` に対応行が作られぬ★——同一 unit/時間帯が「occupancy 上は空き（claim 無し）だが appointments 表上は active な予約有り」という不整合状態になり得る（二重予約防止が claim table を根拠にしている箇所があれば、そこがすり抜ける可能性——この帰結自体は本票の射程外につき裁定せぬ・第四値として明記するに留める）。

★原因（code 上の事実、推測でない）★: `appointment_grid.py` の `change_appointment_status` は分岐順序が `if new_status=="cancelled" / elif new_status and new_visit_status / elif new_status / elif apt["status"]=="cancelled" / else` であり、`booked`（`new_status="confirmed"` truthy・`new_visit_status=None`）は3番目の `elif new_status:` に必ず捕まり、4番目の「cancelled からの復元」分岐へは**到達し得ない**（新 target でも旧 target でも同一構造・E-3 fix はこの関数に一切触れておらぬ＝git diff で確認済）。

### E-1（`appointment_detail.py` `api_update_detail`）の rollback atomicity 動的検証（追加・任意）

旧票では E-1 を「raw・未委譲」としていたが、新targetでは `occupancy_changed` 時に `move_appointment_slot` を呼ぶよう改修済（新target行128）。ただし raw UPDATE（行117）が `move_appointment_slot` 呼出（行128）より**先に実行**される同一関数内の順序ゆえ、「guardが弾いた後も raw UPDATE だけ残る」部分書込みの懸念を当職が独立に動的実測した:
```
cancelled 予約へ PATCH .../detail (start_time+unit_id変更) → HTTP 500
AFTER_ROW: start_time 変更前と同一値・version 変更前と同一値（1のまま）
AFTER_CLAIMS: []
VERDICT=E1_ROLLBACK_ATOMIC_OK: raw UPDATE was undone, guard fully closed E-1
```
★confirmed: 同一関数内の `except BaseException: conn.rollback(); raise` により、guard発火時の raw UPDATE は正しく巻き戻される（部分書込みバグは無し）★。ただし HTTP 応答が 500（未捕捉例外・素の ValueError 伝播）であり 4xx 整形はされておらぬ——之は API 設計/UX の話であり本票（reachability の話）の射程外につき裁定せぬ。

## §5 禁則順守申告

- code 編集 0 / commit 0 / push 0 / merge 0。tracked file への一時上書き（§2-1）は復元後 `git diff --stat`=空・HEAD不変を確認済。
- 別 worktree を当職自身が新規に立てた（`/tmp/resimg-verify4-cycle2-matrix2-20260807`）。a1 の worktree/branch は一度も開いておらぬ。
- 本票作成中に untracked のまま残した file 2件（commit せず・repo外相当）:
  - `backend/tests/detect_undelegated_occupancy_mutation_a4.py`（当職の既製作を複製・§2 で実行のみ）
  - `backend/tests/verify_b2_status_only_a4_ephemeral.py`（§4-B 陰性実測用・本票用に新規作成・実行のみ）
- migration/schema 変更 0。DB実環境・患者・本番 0。
- 母集団を手で列挙せず、`grep -rn` の全件出力・gate3 detector の全件出力をそのまま基礎とした。
- 判らぬ物: `appointment_grid.py:525-531`（両要素truthyの dead code 分岐）が将来 `_FRONT_TO_BACK_STATUS` にエントリが追加された場合に到達可能へ転じ得るか否かは、現行7エントリの実読でのみ判じており、将来変更への耐性は未確認のまま「未確認」と書く。

## §6 結論（述語形式）

1. `reachable(A)=True`（5 site）。`undelegated(A)=∅`（旧A-4/A-5とも §4-A/B で GREEN 確認・移行済）。
2. `reachable(B)=True`（2 site）。`undelegated(B)={appointment_grid.py:534 "booked"}` ≠ ∅（★§4-C/§4-B で動的確認・E-3 fix の射程外・未だ根治されておらぬ★）。
3. `reachable(C)=True`（6 site）。`guarded(C-1..C-6)=True`（★全6箇所が guard済に移行——旧票では C-3〜C-6 の4箇所が未guardだったが、新targetでは全て move_appointment_slot 経由の一元guard、または独自guard、または両方の defense-in-depth になっている事を code 実読で確認済★）。
4. `reachable(D)=True`（2 site、predicate対象外）。`appointment_grid.py:525-531`=dead code（新旧target で同一7エントリ・変化なし）。
5. `reachable(E)=True`（E-3 は §2-1 で動的 RED→GREEN 確認。E-1 は §4-B で rollback atomicity 動的確認。E-2〔diagonal update_linked_appointment〕は §4-A の陽性testで active な連動先について確認済だが、**連動先自体が inactive な場合の挙動は当職未実測=未確認のまま明記**)。
6. 全5遷移(A-E)はなお少なくとも1経路で到達可能。E-3 fix により C 系の未委譲は解消されたが、**B系の未委譲(booked分岐)は解消されておらぬ**——これが当職の器の射程外に残る具体的な残存risk。

report_to: karo-second
