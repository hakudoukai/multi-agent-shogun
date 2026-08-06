# 足軽4号 → 家老second/軍師second: barrier方式・真のthread-level並行 陽性対照3種（本務・完了報告）

下命=16:44:02便（本部長令16:35:49・barrier方式で作り直せ）+16:55:06便（同・16:48:01逐語・
台帳単位変更は別途）。★本務（barrier）★を最優先で完遂した結果を報じる。順＝⑴本務→⑵47b→⑶台帳
の指示どおり、⑵は前便で完了済のため本便は⑴のみを扱う（⑶台帳4欄は次便）。

## §0 三sha+worktree欄

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 測定対象=当職独自実装（barrier化は当職のtest fileのみの変更・productionコード不触）
- 提出直前HEAD確認=`git rev-parse HEAD`実測=下記
- 当職の木のHEAD=`990e5ad`

```
$ date -Iseconds
2026-08-06T17:11:57+09:00
$ git rev-parse HEAD
990e5ad4dfde5ad513e64767d051415dc44837bd
```
機械path+sha:
```
5d739167af90778e292439008e353e4553ff6ce4da151b1576cbb37febfa2b46  backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py
```

## §1 設計（下命①②の要求を満たす形）

新設file=`backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py`。
`threading.Barrier(2)`で両workerを同期し、別thread(別connection)で同時解放。
_check_conflict（app層TOCTOU判定）はbarrier到達地点として差し替え、実際の競合停止は
DB制約のみに委ねる（app層の事前判定で片方を落とさせない為）。

## §2 GREEN（現行コード・postgre-root schema）— ★3シナリオ全PASS★

```
$ pytest backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py -v -s
test_web_vs_web_barrier_true_concurrent_second_gets_409_or_integrity_error
  F2BARRIER_WEBVSWEB_SUCCESS=1 CONFLICT_ERRORS=1 OTHER_ERRORS=0
  F2BARRIER_WEBVSWEB_ACTIVE=1 CLAIMS=2 → PASSED
test_web_vs_staff_barrier_true_concurrent_cross_entry_conflict
  F2BARRIER_WEBVSSTAFF_SUCCESS=1 CONFLICT_ERRORS=1
  ERRORS=[HTTPException(status_code=409, detail={'rule': 'double_booking', …})] → PASSED
test_offset_overlap_barrier_true_concurrent_partial_conflict
  F2BARRIER_OFFSET_SUCCESS=1
  ERRORS=[IntegrityError('UNIQUE constraint failed: appointment_slot_claims…')]
  F2BARRIER_OFFSET_CLAIMS=2 → PASSED
```
全て「旧欠陥snapshot＝success2/active2」に対する「修正後＝success1/409×1/active1/claim正数」の
契約を、★2独立connectionの逐次呼出しでなく真のthread-level並行(barrier同期)で★満たした。

## §3 RED（同一harnessでの対）— ★offset overlapで真の再現に成功★

新設fixture`pre_root_db_path`（`apply_booking_concurrency_root`を適用しない素schema）で
同じbarrier harness・同じworker構成のoffset overlap testを走らせた:

```
test_offset_overlap_barrier_RED_on_pre_root_schema
  F2BARRIER_OFFSET_RED_SUCCESS=2 ERRORS=[]
  F2BARRIER_OFFSET_RED_ACTIVE=2 → PASSED（★これがRED★=両者成功=旧欠陥の実測）
```
★GREEN(§2の同名test)とRED(本test)は、barrier位置・worker構成・assertの形が完全に同一で、
差分はfixtureのみ(pre_root_db_path=旧schema／db_path=適用済)★——下命「harnessを変えて
GREENにするは不可」を、fixtureの一点差分のみで満たした。

## §4 自己発見：exact-time Web-vs-WebはRED化できず（★裁定せず記録★）

★当初の想定（claim_appointment_slotsのみをno-op化すればexact-time Web-vs-WebでもRED再現できる）
は誤りだった★。実測=`success=1`（claim_appointment_slots無害化後も競合は止まったまま）。

★真因（実測で特定）★= `apply_booking_concurrency_root`はclaim_appointment_slotsとは
★独立に★appointments table自体へ部分UNIQUE index
(`uq_appointments_active_exact_start` ON appointments(clinic_id,unit_id,start_time)
WHERE status NOT IN ('cancelled','no_show')、`booking_concurrency_root.py`L252-256)も
新設している。exact-time・同一status（本testの2 workerは共にbooking_service.create_bookingを
通るため同一approval mode→同一status）の場合、claim_appointment_slotsを無害化しても
此の部分indexが独立に競合を止める（★二重guard設計★）。

∴ exact-time Web-vs-WebのRED再現は諦め、`test_web_vs_web_barrier_RED_exact_time_blocked_by_independent_guard`
として「無害化しても止まる」事実そのものを固定するtestへ差し替えた（§3のoffset overlap testが
下命の求める「同じharnessでのRED→GREEN対」の本体を担う）。

## §5 KeyboardInterrupt(47d)との関係（既報・再掲なし）

47bの独立再走+KeyboardInterrupt crash-injectionは前便
（`docs/incident_logs/2026-08-06_47b_independent_rerun_and_four_work_items_a4.md`）で完了済。
下命16:44:02④で新たに求められた要素（★別の例外型で測れ★）は同便で既に満たしている
（家老second殿17:03:53便④で確認・賞済）。本便からの追加作業なし。

## §6 c2-detector gate

★OPENのまま（閉じたと書かない）★。本便は陽性対照のharness再構築のみであり、gate自体の
開閉判断は上位裁定事項として関与しない。

## §7 次（下命⑤の順・変わらず）

⑴barrier（本務）=★本便で完了★。⑵47b独立再走=前便で完了済。
⑶台帳4欄（site ID／reachable cases／委譲先／test）＝16:48:01裁で単位が変わったため次便で作り直す
（「11」は上限とも分母とも書かない・現断面のcandidate site数として扱う）。
分類=productively_assigned。実装未着手（役の境）。

## §8 禁則遵守

新設testはproductionコードを一切変更していない(test fileのみ)。push/PR/main/本番=一切なし。
queue/*の行数/sha引用なし。

★札★
```
$ date -Iseconds
2026-08-06T17:11:57+09:00
$ git rev-list --count --since='2026-08-06 00:00' HEAD
101
$ git rev-list --count HEAD
646
```
