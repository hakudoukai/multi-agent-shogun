# Cycle2 Gate4b（断面=`14cad3a4`）: post-commit durability 5site crash tests 独立再走（足軽5号）

## 下命

karo-second msg_20260807_002256_4af56cd4 (2026-08-07T00:22:56)、令キー
`current_order_10_20260807_001900_GATE4B_INDEPENDENT_RERUN`（本部長殿 2026-08-07T00:02:30 令・
将軍second 00:07:14 便で転記）。前工区(2026-08-06_pending_notice_periodic_flush_lane_a_impl_a5.md
Lane A)を軍師second PASS(00:13:54)で閉じた直後、次工区として着信。

**訂正一件**: 当職が直前便(00:11:49)で「次工区はCycle2 Gate3・空き次第上へ問わず着手」と書いたのは誤り
——Gate3は本部長殿令にて足軽6号の担当であり、当職の担当はGate4b。本部長殿令と家老second発令が13秒
交差した為に生じた行き違いであり、家老secondの明記通り「咎は当職に無し」。本令にて置き換わった。

## 対象

- **target commit**: `14cad3a42c20c34ac1f93e4f334da5c85f195dd5`
  （`test(reservation-cycle2): 真並行(thread+barrier)でcreate-with-claim concurrency invariantを実測 (Cycle2 ⑸)`）
- **依存**: 足軽1号 target。家老secondが2026-08-07T00:19に実在確認済（当repoには無し・`cat-file`で確認）。
- **足軽1号 worktree（read-only）**: `/tmp/resimg-cycle2-f123-clean-20260806`（当職はここへ書込せず）
- **当職の独立worktree**: `/tmp/resimg-verify5-gate4b-20260806`（本体repo=`/tmp/resimg-stage1-runtime-20260806`から
  `git worktree add`・target commitへdetached HEAD・a2先例
  (`/tmp/resimg-verify2-cycle2-barrier-20260806`)に倣った命名）

## 工区遵守（逐語）

㈠ 同一5 site crash testsを独立に再走 → 実施（下記結果参照）
㈡ 修正0（実装へ手を入れない） → 遵守。`git status --porcelain`で無変更確認済
㈢ 別worktreeを己で立てる（a1のworktreeはreadのみ） → 遵守。上記の通り独立worktreeを新規作成
㈣ 結果は数でなく述語で締める → 下記「結果（述語）」参照
㈤ 測りが覆っていない層を同じ行に書く → 下記「本測りが覆っていない層」参照

## 対象file同一性確認

```
$ sha256sum /tmp/resimg-cycle2-f123-clean-20260806/backend/tests/test_post_commit_durability_5sites_a1.py
$ sha256sum /tmp/resimg-verify5-gate4b-20260806/backend/tests/test_post_commit_durability_5sites_a1.py
```
両者のsha256完全一致（IDENTICAL_FILE確認済・当職の独立worktreeでも足軽1号のfileと一切改変されていない
同一の5 site crash testsを走らせている事の証跡）。

## 実行

```
$ cd /tmp/resimg-verify5-gate4b-20260806
$ python3 -m pytest backend/tests/test_post_commit_durability_5sites_a1.py -v -s
```

```
test_cancel_appointment_log_loss_on_post_commit_crash
  P5_STATUS_AFTER_CRASH=confirmed P5_LOG_ROWS_AFTER_CRASH=0
  P5_STATUS_AFTER_RETRY=cancelled P5_LOG_ROWS_AFTER_RETRY=1
  PASSED
test_update_appointment_log_loss_on_post_commit_crash
  P5U_DURATION_AFTER_CRASH=30 P5U_LOG_ROWS_AFTER_CRASH=0
  P5U_DURATION_AFTER_RETRY=45 P5U_LOG_ROWS_AFTER_RETRY=1
  PASSED
test_transition_status_log_loss_on_post_commit_crash
  P5T_STATUS_AFTER_CRASH=confirmed P5T_LOG_ROWS_AFTER_CRASH=0
  P5T_STATUS_AFTER_RETRY=arrived P5T_LOG_ROWS_AFTER_RETRY=1
  PASSED
test_change_appointment_status_log_loss_on_post_commit_crash
  P5G_VISIT_STATUS_AFTER_CRASH=scheduled P5G_LOG_ROWS_AFTER_CRASH=0
  P5G_VISIT_STATUS_AFTER_RETRY=arrived P5G_LOG_ROWS_AFTER_RETRY=1
  PASSED
test_execute_cancel_log_loss_on_post_commit_crash
  P5C_STATUS_AFTER_CRASH=confirmed P5C_LOG_ROWS_AFTER_CRASH=0 P5C_RETRY_STATUS_CODE=200
  P5C_STATUS_AFTER_RETRY=cancelled P5C_LOG_ROWS_AFTER_RETRY=1
  PASSED

======================== 5 passed, 1 warning in 14.32s =========================
```

測時=2026-08-07T00:26:49+09:00。1 warningはPyPDF2非推奨警告のみ（本工区と無関係・既知）。

## 結果（述語・数でなく）

5サイト（cancel_appointment／update_appointment／transition_status／change_appointment_status／
_execute_cancel）いずれについても、**「core commit直後・audit log記録直前」の一点で模擬crashを起こした
場合、crash直後の状態（appointments/visit_statusの値）はcrash対象の変更（cancelled/duration=45/arrived）
へ確定しておらず、log行も0のまま**——すなわち**状態変更とaudit log記録が同一commit/rollback単位に
なっている**ことが独立re-runでも成立する。かつ**retry実行後は全サイトで状態変更・log行の双方が
揃って確定する**（idempotency不要のupdate/cancel/status系でも、rollback済のためretryが正しく通る）。

これは足軽1号の実装(commit 14cad3a到達までの一連)が主張する「post-commit durability根治」を、
**別worktree・別プロセスからの独立実行でも同一の述語（crash後未確定・retry後確定）が成立する**形で
再確認したものであり、a1のworktree内でのみ成立する結果ではない事を示す。

## 本測りが覆っていない層

karo-second令に明記された一条「機構を呼んでおらぬは守られておらぬに非ず——層が二つ在れば片方の不在は
もう片方の射程でしか測れぬ」に従い、本測りの射程を明示する。

- **crash injection の方法そのものが1種類に限定される**: 本testは`log_appointment_action`関数を
  Python側で`SystemExit`にmonkeypatchする形で「core commit後・log呼出直前」の一点でのみ模擬crashを
  起こしている。実プロセスへの`SIGKILL`・DB接続断・ディスクI/Oエラー・OOM killer等、**実際にproductionで
  起こりうる他のcrash機序は一切試験対象外**——本testが検証しているのは「commit/rollback単位の設計が
  正しいかどうか」であって「あらゆる種類のcrashに対して頑健か」ではない。
- **crashのタイミングが1点に固定**: 5サイトいずれも「core commit★直後★・log呼出★直前★」の一点でのみ
  crashを模擬している。core commitの★最中★（SQLite側のトランザクション処理途中）や、slot-sync/履歴書込
  等の中間ステップでのcrashは本testの射程外。
- **真の並行実行は本testの範囲外**: 5サイトのtestはいずれも単一プロセス・単一スレッドの逐次実行であり、
  同一appointment_idに対する並行アクセス下でのcrash挙動(race)は別テスト(`test_booking_concurrency_root_f2_self_rollback.py`
  等)の射程であり、本5site testでは検証していない。
- **本測りが確認したのは「commit 14cad3a断面での5サイトの挙動」のみ**——それ以前の断面(47bで直した1箇所や、
  他の未修正箇所が存在する可能性)は本工区の対象外(母集団はa1が明記した「残5箇所」に限定)。

## 五点束ね（current_order_11_20260807_004400_GATE4B_FIVE_POINT_BUNDLE・再走不要・已に済んだ物の束ね）

下命: karo-second msg_20260807_004624_51b6ee60 (2026-08-07T00:46:24)。本部長殿00:37:19裁定
「Gate4bは★受入候補★であって正式閉鎖に非ず」を受け、既出の材料を五点として束ねる。
**★最も重き一行★：以後「Gate4b PASS」と断面無しには書かぬ——正しくは「`14cad3a4`に対する Gate4b PASS」**
（`14cad3a4`は最終targetではなく、足軽1号が三扉offset overlap実装で新commitを出した後、当職は
その新target到着後に条件待ちでもう一度再走する。時刻でなく条件で待つ・家老secondより報せを待つ）。

**① artifact path + full SHA**:
`docs/incident_logs/2026-08-07_cycle2_gate4b_independent_rerun_a5.md`（本file自身。行数・SHAは
本便末尾で最終値を確定する）

**② exact command（逐語・省略0）**:
```
$ cd /tmp/resimg-verify5-gate4b-20260806
$ python3 -m pytest backend/tests/test_post_commit_durability_5sites_a1.py -v -s
```
上記2行は当職が実際にterminalへ入力した文字列そのもの（要約・省略なし）。

**③ test file の SHA**（2026-08-07T00:47:05+09:00再測・当初測定と同一値）:
```
52112ae523289e8f7a2511c18f757d1f511101a18fac0df896c670bdb48cf2ab  backend/tests/test_post_commit_durability_5sites_a1.py
```

**④ worktree clean の証**（2026-08-07T00:47:05+09:00測・`git status --porcelain`実行・両worktree）:
```
[a1 worktree・read-only対象: /tmp/resimg-cycle2-f123-clean-20260806]
$ git status --porcelain
(出力なし=clean)

[当職の独立worktree: /tmp/resimg-verify5-gate4b-20260806]
$ git status --porcelain
(出力なし=clean)
$ git log --oneline -1
14cad3a test(reservation-cycle2): 真並行(thread+barrier)でcreate-with-claim concurrency invariantを実測 (Cycle2 ⑸)
```

**⑤ scope票（覆っておらぬ層）**: 上記「本測りが覆っていない層」節に既出——crash injection手法1種限定
（`log_appointment_action`のSystemExit monkeypatchのみ）／timing 1点固定（core commit直後・log呼出
直前）／並行実行は射程外（別test`test_booking_concurrency_root_f2_self_rollback.py`の範囲）／母集団は
a1明記の「残5箇所」に限定（それ以前の断面・47bの1箇所は対象外）。

## 台帳の分け（本部長殿厳命・混同禁）

- **2026-08-07T00:11:49完了（`current_order_9`・LANE_A_IFACE_REMOVE）** = ★旧機構工区★
  （本repo `multi-agent-shogun`側・`pending_notice_flush.sh`のfake clock interface完全除去・
  commit `6e056da`）
- **2026-08-07T00:28:26完了（Gate4b）** = ★製品検証★
  （外部repo `hakudoukai/hakudokai-dev`側・5site crash tests独立再走・**断面=`14cad3a4`**）

両者は担当repo・性質(機構修正 vs 製品検証)とも別物であり、本便以降も混ぜて書かない。

## 禁則遵守声明

実装fix 0（`git status --porcelain`で当職の独立worktree・a1のworktree両方とも無変更確認済）・commit
0・push 0・merge 0・既存resimg freeze 32件不触（本工区では触れていない）・新規機構工区0（既存の
pytestを読み専用で実行したのみ）・当職の独立worktreeは`git worktree add`で新規作成し、a1の
worktreeへは一切書込していない・再走0（已に済んだ物の束ねのみ、本令の明記通り）。
