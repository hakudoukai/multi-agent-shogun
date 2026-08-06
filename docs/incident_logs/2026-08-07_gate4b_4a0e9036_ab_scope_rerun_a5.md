# Gate4b `4a0e9036` ⒜⒝断面 独立再走（足軽5号）

## 下命

karo-second msg_20260807_015857_77cae3f6 (2026-08-07T01:58:57)。本部長殿 01:56:12 令、exactly-once。

target = `4a0e9036ed94022d79baa4a1e2cf88d5827eec12`（immutable detached HEAD）
scope = ★⒜E-3一元化 と ⒝move offset barrier の断面のみ★
記録の語 = 「`4a0e9036` の ⒜⒝断面 PASS/FAIL」
禁 = 五述語全体PASSと書くな／②③④⑤は未達expectedゆえ欠陥数へ混ぜるな／実装fix 0・commit 0・push 0・merge 0・a1の木はreadのみ

## 対象commit

```
4a0e903 fix(appointment): E-3根治 — move_appointment_slotへcancelled/no_show guardを一元化 (current_order_13⒜⒝)
```

- ⒜対応file: `backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py`（新規・260行）
- ⒝対応file: `backend/tests/test_true_concurrency_barrier_a1.py`（既存file拡張・move/reschedule経路を追加）
- 併せて `backend/services/appointment_lifecycle.py` に guard実装（19行追加）

## 独立worktree

`/tmp/resimg-verify5-gate4b-4a0e9036-20260807`（`git worktree add --detach` にて
`/tmp/resimg-stage1-runtime-20260806` から新規作成・target commitへdetached HEAD）。

a1のworktree（`/tmp/resimg-cycle2-f123-clean-20260806`）は read のみ（write 0）。

## 対象file同一性確認（★commit blobとの照合★・a1の作業木は現に dirty ゆえ非採用）

a1のworktreeは `git status --porcelain` で dirty（`appointment_lifecycle.py` 等5 file が
本commit以降のa1自身の作業継続で改変中）と判明した為、a1の作業木との単純diffは正しい比較対象で
はない。よって `git show 4a0e9036...:<path>` （commit blobそのもの）と当職の独立worktreeの
working file を照合した。

```
$ git show 4a0e9036ed94022d79baa4a1e2cf88d5827eec12:backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py | sha256sum
23e7fd3a5ec462e214b4ecf0d458f8c7304a2685d64781948851192848b804cb  -
$ sha256sum /tmp/resimg-verify5-gate4b-4a0e9036-20260807/backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py
23e7fd3a5ec462e214b4ecf0d458f8c7304a2685d64781948851192848b804cb  /tmp/resimg-verify5-gate4b-4a0e9036-20260807/backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py

$ git show 4a0e9036ed94022d79baa4a1e2cf88d5827eec12:backend/tests/test_true_concurrency_barrier_a1.py | sha256sum
9971edd94b659766bda3b51f5649473e0d26088d0b8b309a58875503505044cd  -
$ sha256sum /tmp/resimg-verify5-gate4b-4a0e9036-20260807/backend/tests/test_true_concurrency_barrier_a1.py
9971edd94b659766bda3b51f5649473e0d26088d0b8b309a58875503505044cd  /tmp/resimg-verify5-gate4b-4a0e9036-20260807/backend/tests/test_true_concurrency_barrier_a1.py

$ git show 4a0e9036ed94022d79baa4a1e2cf88d5827eec12:backend/services/appointment_lifecycle.py | sha256sum
2ade6cf52b250378fd9aae405529f5a3c1d256c228043ec2aaf682e1f18217d7  -
$ sha256sum /tmp/resimg-verify5-gate4b-4a0e9036-20260807/backend/services/appointment_lifecycle.py
2ade6cf52b250378fd9aae405529f5a3c1d256c228043ec2aaf682e1f18217d7  /tmp/resimg-verify5-gate4b-4a0e9036-20260807/backend/services/appointment_lifecycle.py
```

全3 file完全一致（IDENTICAL_TO_COMMIT確認済）。当職の独立worktreeはtarget commitのblobと
byte-identicalな内容で試験している事の証跡。

## 実行・結果

### ⒜ E-3一元化（`test_move_appointment_slot_inactive_guard_e3_a1.py`）

```
$ cd /tmp/resimg-verify5-gate4b-4a0e9036-20260807
$ python3 -m pytest backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py -v -s
```

```
test_move_appointment_slot_rejects_inactive_appointment[cancelled]  PASSED
test_move_appointment_slot_rejects_inactive_appointment[no_show]    PASSED
test_move_appointment_slot_still_allows_active_appointment          PASSED
test_booking_manage_change_booking_blocks_move_of_cancelled_appointment  PASSED
4 passed, 1 warning in 19.64s
```

1 warningはPyPDF2非推奨警告のみ（本工区と無関係・既知）。

### ⒝ move offset barrier（`test_true_concurrency_barrier_a1.py`）

```
$ python3 -m pytest backend/tests/test_true_concurrency_barrier_a1.py -v -s
```

```
test_true_concurrency_RED_without_concurrency_root_double_books        PASSED
test_true_concurrency_GREEN_with_concurrency_root_prevents_double_booking  PASSED
test_true_concurrency_move_RED_without_concurrency_root_double_books       PASSED
test_true_concurrency_move_GREEN_with_concurrency_root_prevents_double_booking  PASSED
4 passed in 19.76s
```

真並行(barrier)系ゆえ再現性確認で追加2回再走（計3回連続）:

```
run2: 4 passed in 17.60s
run3: 4 passed in 19.66s
```

3回連続 ALL PASS（flakiness不在）。

## 結果（述語・断面明記）

**`4a0e9036` の ⒜⒝断面 PASS**。

- ⒜: move_appointment_slotの一元化guardは、cancelled/no_show状態のappointmentに対する
  move操作を全経路（直接呼出2件・実呼び手経路booking_manage.change_booking）で確実に拒否する
  （ValueError発生・claims不変）。active状態のappointmentに対するmove操作は引き続き許可される
  （positive control）ことも同時に確認。
- ⒝: 15分ずれpartial overlapの真並行(thread+barrier)実測が、既存create経路
  （RED=旧断面で二重成功／GREEN=新断面で一成功・一IntegrityError conflict）に加え、
  move/reschedule経路でも同一の述語（RED=二重成功／GREEN=一成功・一IntegrityError conflict）
  で成立する。3回連続再現。

## 本測りが覆っていない層・混ぜぬ扱い（②③④⑤＝未達expected）

karo-second令の禁則「②③④⑤は未達expectedゆえ欠陥数へ混ぜるな」に従い明記する。

- 本工区の対象はcommit `4a0e9036` の変更3fileに限定されたⒶ⒝2断面のみ。旧5site crash test
  (`test_post_commit_durability_5sites_a1.py`)や、旧Gate4b(`14cad3a4`)で扱った他の述語群は
  ★本工区の再走対象外★——「本commitで扱っていない」ことは「欠陥」ではなく「scope外」であり、
  未達=expectedとして欠陥数に混ぜていない。
- gate3 detector（未委譲1・residual7）の再走自体は本工区の対象外（a1が281commitの検証内で
  実施済との記載を引用したのみ・当職は独立に再走していない）。
- 真の並行実行は本testの範囲内で確認したが、3スレッド以上・異なるunit間・DBロック粒度以外の
  crash機序（SIGKILL/OOM等）は依然射程外（前回Gate4b報告と同様の限界）。
- a1のworktree自体は現在dirty（本commit以降の追加作業継続中）——当職の測りは
  commit `4a0e9036` の断面のみに対するものであり、a1の現在進行中の未commit変更は対象外。

## ⒜⒝ 事前確認（本便先行事項・karo-second令記載通り）

- ⒜ 外部handoff復元: 済（`/tmp/claude-1000/.../scratchpad/a5_handoff_20260807_0101.md` 読了・
  current_order_12/13系の生きた状態を確認）
- ⒝ auto-clear保護の再確認: 済（`scripts/inbox_watcher.sh` `is_no_auto_clear_agent()` 関数
  （L797-805）に `ashigaru5` が恒久リストとして明記されており、自動contextリセット
  （`send_context_reset`、task_assigned検知時の自動/clear）が抑止される事を実コード読解で確認）

## 禁則遵守声明

実装fix 0（当職の独立worktree・`git status --porcelain`で無変更確認済）・commit 0・push 0・
merge 0・a1のworktreeへの書込0（read のみ）・五述語全体PASSとは書いていない
（「`4a0e9036`の⒜⒝断面PASS」のみ）・②③④⑤を欠陥数へ混ぜていない。
