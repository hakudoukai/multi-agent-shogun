# 足軽4号 → 家老second/軍師second: 47b独立再走(GREEN確認)+KeyboardInterrupt追加測定+工区四つ(㈠〜㈣)

下命=16:39:43便（分類訂正=待機は憲章語に非ず／工区四つ／47b着手の独立再走要請／欄の改め再掲）。
本便は★実装せず★（役の境）、a1殿の47b根治(2fe4ed9)を自分の木へ独立に材料化して測定した結果を報じる。

## §0 三sha+worktree欄（下命⑤の様式・機械出力そのまま）

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 測定対象sha=`2fe4ed90b128eb3226f37465a7ef22c986ba0d79`（a1殿commit・出所=別worktree
  `/tmp/resimg-cycle2-impl-20260806`、`git show 2fe4ed9:<path>`で3production fileのみ独立材料化。
  a1殿自身のtest file(`test_appointment_log_same_transaction_47b.py`)は当職の木に取り込んでいない
  =当職は★自分のtest_47b★で再走した、独立性を保つ為）
- 提出直前HEAD確認=`git rev-parse HEAD`実測=下記
- 当職の木のHEAD=`411368c`（sync commit`7f49218`+test commit`411368c`）
- 一致or差分=★sync commit`7f49218`が2fe4ed9の3 production fileと内容一致（git show比較済）★

```
$ date -Iseconds
2026-08-06T16:59:10+09:00
$ git rev-parse HEAD
411368c5f4d3fc6ba5b93a8e365b34bb21da6f7a
```

★機械path+shaの並び★（下命⑤の型・`git show --name-only --format='' <sha> | while read -r f; do
echo "$(git show <sha>:"$f" | sha256sum | cut -d' ' -f1)  $f"; done`の出力そのまま）:
```
sync commit 7f49218（3 production file・2fe4ed9材料化分）:
cc6efda4e0a42f91319e20cdbbb6ad002bb6df423b1f22996065a53bc090461d  backend/services/appointment_lifecycle.py
f60ae813491f6dc63db9265d658e4f434d6d0f499263dd061f9ceac33df0856f  backend/services/appointment_log_service.py
c19c3c6a032b39d9c5eb66f14821720125244712b8c91998cc81085ed33426af  backend/services/appointment_service.py

test commit 411368c（当職test file・test_47d新設）:
b1b6449a8477990d198d91b250ec69aaf859ceb4c62e9ff14359c63f66db1ddb  backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py
```

## §1 ③ 47b 独立再走 — ★GREEN確認（当職独立測定）★

当職自身の`test_47b_f1_post_commit_crash_then_replay_loses_audit_log_red`
（a1殿のtest fileでなく当職の既存test、書き換えなし・SystemExit注入・assert文言不変）を
2fe4ed9材料化断面で再走：

```
$ /tmp/resimg-stage1-runtime-venv/bin/python -m pytest \
    backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py::test_47b_f1_post_commit_crash_then_replay_loses_audit_log_red -v -s
F1_PC_CRASH_APPT_EXISTS=1 F1_PC_CRASH_AUDIT_LOG_ROWS_AFTER_REPLAY=1
PASSED
```
★同一test・同一assert文言が、断面の違いだけでRED(55ba5a7)→GREEN(2fe4ed9)に転じた事を
当職が独立に確認した★（a1殿の主張の丸写しでない、当職自身のoracle・当職自身の実行）。

## §2 下命③後半 — ★KeyboardInterrupt crash-injection 追加測定（新設test_47d）★

★理由（下命の指摘への直接応答）★: SystemExitは元々`except Exception`のMROに含まれず、
Exception捕捉でも既に捕捉不能。∴ SystemExitでのGREEN確認だけでは「except Exception→
except BaseException」への拡張が★実際に何を追加で救っているか★を識別できない。
KeyboardInterruptもBaseException直属の別系統であり、同じ穴を突く独立した型として選定した。

新設test（`test_47d_f1_keyboardinterrupt_crash_injection_baseexception_widening_independent`、
当職の木のみ・commit`411368c`）:
```
$ pytest …::test_47d_f1_keyboardinterrupt_crash_injection_baseexception_widening_independent -v -s
F1_KBDINT_CRASH_ORPHAN_APPT_ROWS=0 (desired=0 if BaseException widening rolled back cleanly)
F1_KBDINT_RETRY_APPT_ROWS=1 F1_KBDINT_RETRY_AUDIT_LOG_ROWS=1
PASSED
```
★KeyboardInterrupt注入時も①例外がそのまま伝播 ②rollbackによりcrash試行のappointment行が
一切残らない(orphan=0) ③retryが新規acquireから完走しappointment/audit logともに1件ずつ生成、
の3点を当職が独立に実測した。∴ BaseException拡張はSystemExit固有でなく★型非依存に効いておる★
事をSystemExit以外の型で示せた（下命の要求を満たす）。

## §3 全体再走（退行なきことの確認・55ba5a7断面からの差分）

```
$ pytest backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py -q --tb=no
.FFF........  [100%]
FAILED test_40_f1_staff_retry_should_return_same_id_red（既知=当職test固有の陳腐化、先便から不変）
FAILED test_45_f1_idempotency_key_interface_absent_red（既知・同上）
FAILED test_46_f1_mid_sequence_failure_rolls_back_appointment_insert_too（既知・同上）
3 failed, 9 passed in 3.75s
```
55ba5a7断面（前便）は「4 failed, 7 passed」（11件、test_47b含む・test_47d未設）。
本便は「3 failed, 9 passed」（12件）＝★test_47bがFAILED→PASSEDへ転じ(-1 failed)、
test_47dを新設しPASSED(+1 passed)★の差分のみで、他9件は不変（当職実測で件数の算術を検算済）。

## §4 writer回帰baseline（2fe4ed9・退行なし）

```
$ pytest backend/tests/test_appointment_api.py backend/tests/test_appointment_service.py \
    backend/tests/web_reservation/test_phase2_2_booking.py backend/tests/test_appointment_grid_slot_sync.py \
    backend/tests/test_create_with_claim_cross_entry.py backend/tests/test_booking_concurrency_root_f2_self_rollback.py \
    tests/test_booking_validator.py -q
121 passed, 2 warnings in 231.40s
```
55ba5a7断面（前便§3）と★同じ121 passed・0 failed★（当職独立実測、a1殿自身のtest file
`test_appointment_log_same_transaction_47b.py`は本baselineに含めていない=前便から不変の
母集団を保つ為、意図的に対象外とした事を明記）。

## §5 ㈣ 母集団の取り直し（4軸目・2fe4ed9断面での再検算）

```
$ grep -rniE "(insert into appointments|update appointments|delete from appointments)" \
    backend --include="*.py" | grep -v "/tests/" | grep -v -E "migrations/" | wc -l
31
```
★件数=31（不変・母集団の増減なし）★。ただし`appointment_service.py`内の行番号は
a1殿の差分(+66/-32行、うち`_write_audit_log`closure新設分)により以下の通り移動した
（当職実測・地点そのものの意味は不変）:

| 用途 | 55ba5a7時点 | 2fe4ed9時点 |
|---|---|---|
| create(INSERT委譲) | L301 | L335 |
| update_appointment(UPDATE) | L463 | L471 |
| modification_count(UPDATE・除外) | L516 | L524 |
| transition_status(UPDATE) | L671 | L679 |

`appointment_lifecycle.py`のL83/L125(共通層本体)は★行番号も内容も不変★
（a1殿の変更はL160以降のdocstring+on_persistedフック新設で、既存のUPDATE文2箇所は不触）。
∴ Ledger A/B(§2区分・31文中GAP11)の★件数・区分は2fe4ed9でも不変★、行番号のみ表を更新要
（本便§5の対応表を今後の引用時の正本とする）。

## §6 ㈡ 最終統合HEAD全対再走の手順（組むのみ・走らせぬ）

1. a1殿の最終統合commit（本便時点でF2=55ba5a7、47b=2fe4ed9、他未確定）のHEAD shaを
   `git log --all --author=ashigaru1-stage1 --format='%h %cI %s' -1`で確定し、本便§0と同型の
   三sha欄を記録。
2. 当職の木へ production file 全件を`git show <HEAD>:<path>`で materialize
   （個別3fileでなく`git show --name-only --format='' <HEAD>`で変更全fileを機械列挙してから行う、
   下命⑤の型を踏襲）。
3. 当職test file全件（`test_reserveimage_cycle2_regression_f1f2f3_a4.py`）を無変更のまま再走し、
   F1/F2/F3/㈤(47b/47d)の全oracleを一括で見る（個別実行でなく`pytest <file>`一括、
   §3の「9/12」を最終形の分母と揃える）。
4. writer回帰baseline（§4の7 file・121件）を再走、退行なきことを確認。
5. Ledger A/B（§5対応表）を最終HEADで再検算（grep母集団31件が不変か・区分11/8/10/2が不変か）。
6. 上記5点を一便にまとめ、supersedes欄に本便+CORRECTION_gap11便のsha256を機械出力で明記して提出。

★組むのみで走らせぬ理由=a1殿の最終統合commitが本便提出時点で未確定（下命②の指摘どおり
commitの度に断面が動く）ため。手順を先に固定し、確定後は手順の再考なしに即実行できる状態にする★。

## §7 ㈢ 47bの対の受入条件（★後付け・已に修正を見た後である事を明記★）

★断り（条を曲げず）★: 下命は「実装前に受入条件を決めるが筋」としたが、47bは已に着き申した
(§1で確認済)ため、★本節は当職が已に修正結果(GREEN)を見た後に書く後付けの受入条件★である。
先見の証にはならない事を明記する。

- 受入①=当職自身のtest_47b（SystemExit注入・書き換えなし）がRED→GREENへ転じる事 → ★満（§1）★
- 受入②=SystemExit以外の型（少なくとも1種）でも同じくGREENである事 → ★満（§2・KeyboardInterrupt）★
- 受入③=crash試行のappointment行がorphanとして残らない事（rollback完全性） → ★満（§2実測=orphan 0）★
- 受入④=retry後、appointment/audit logともに1件ずつのみ生成される事（重複でも欠落でもない） → ★満（§1,§2）★
- 受入⑤=既存writer回帰に退行がない事 → ★満（§4=121 passed不変）★
- 受入⑥=母集団31文の区分（層内2/委譲済10/除外8/GAP11）が2fe4ed9でも不変である事 → ★満（§5）★

## §8 ⑵・母集団三項の状況（不変・追加作業なし）

- ⑵=已に満（`f1bcfd1`・軍師second PASS 16:27:48）。当職から追加作業なし。
- ㈠(台帳の行分け)=`5460a02`が已に満（前便§2で逐語確認済）、本便§5で2fe4ed9断面でも件数不変を確認。
- ㈤(test_47b/47d)=本便§1・§2で★GREenへ転じた事を独立確認、RED解消★。

## §9 現状（下命①=分類語の訂正を継承）

★分類=productively_assigned★（「待機」の語は用いぬ）。
a1殿の最終統合commit確定を待つ間、§6の手順（組み済）を保持し、確定次第§6の手順通り即実行する。
実装（同transaction化の他5箇所や⑷b以外）には手を付けない（役の境）。

## §10 禁則遵守

実装ファイルは`git show <sha>:<path>`によるmaterializeのみ（a1殿の作業ディレクトリ・test fileは
不触）。push/PR/main/本番=一切なし。queue/*の行数/sha引用なし（下命①順守）。

★札★
```
$ date -Iseconds
2026-08-06T17:00:45+09:00
$ git rev-list --count --since='2026-08-06 00:00' HEAD
100
$ git rev-list --count HEAD
645
```
