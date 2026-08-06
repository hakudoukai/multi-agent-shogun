# Gate5 述語⑤ — residual raw SQL = 0 ないし 非occupancy の機械根拠（新target・足軽2号）

下命=karo-second current_order_15_20260807_004800_AWAIT_A1_NEW_TARGET（now_run追記・trigger msg_20260807_015020_4f401253、01:50:20）。
本部長殿00:45:53裁定＝述語⑤=residual raw SQL=0 ないし 非occupancyの機械根拠。karo-second msg_20260807_005150_02fd39dc（証拠は文字列の存否でなく機械根拠で）。

測時=2026-08-07T02:00:21+09:00（date -Iseconds実値）。
分離＝測るは当職（足軽2号・DB/コード層射程）・直すは足軽1号。fix=0・commit=0・push=0・merge=0・DDL=0（全順守）。

## 対象target

`4a0e9036ed94022d79baa4a1e2cf88d5827eec12`（足軽1号 current_order_13 E-3根治commit）。
当職の手で実在確認（写さず）＝共通repo `/tmp/resimg-stage1-runtime-20260806` に対し `git cat-file -e` で確認・
`git log -1` で件名/日時とdocs/incident_logs/2026-08-07_three_door_offset_overlap_e3_guard_new_target_a1.md
（sha256=3be349e05f76d7a096b7834f0eabf90ee4321dbd2e4730226ec62302f43ce7fa）の記載と一致。

★境の遵守★＝a1の worktree（`/tmp/resimg-cycle2-f123-clean-20260806`）は一字も書き込まず。当職は
①その common gitdir（`/tmp/resimg-stage1-runtime-20260806`）への `git show`/`git diff` 等★読取専用コマンドのみ★、
②独立scratch dir（`/tmp/resimg-verify2-gate3-rerun-target-a2-20260807`、当職が新設）で試行、の二経路のみを用いた。

## ① 母集団の不動を機械的に確認（差分ゼロ＝旧測定の射程が保たれる根拠）

```
$ git -C /tmp/resimg-stage1-runtime-20260806 merge-base --is-ancestor 14cad3a42c20c34ac1f93e4f334da5c85f195dd5 4a0e9036ed94022d79baa4a1e2cf88d5827eec12
BASE_IS_ANCESTOR_OF_TARGET
$ git -C /tmp/resimg-stage1-runtime-20260806 diff --stat 14cad3a42c20c34ac1f93e4f334da5c85f195dd5 4a0e9036ed94022d79baa4a1e2cf88d5827eec12
 backend/services/appointment_lifecycle.py          |  19 ++
 backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py | 260 +++++++++++++++++++++
 backend/tests/test_true_concurrency_barrier_a1.py  | 164 +++++++++++++
 3 files changed, 443 insertions(+)
```

★機械根拠★＝base(14cad3a)→target(4a0e9036)の差分は3ファイルのみで、7residual siteが在る6ファイル
（appointment_detail.py／appointment_grid.py／booking_manage.py／next_appointment.py／
diagonal_service.py／web_reservation/booking_service.py）は★いずれも差分に現れず★＝バイト同一。
∴ 足軽6号票（docs/incident_logs/2026-08-07_gate3_detector_rerun_vs_a1_target_a6.md、
sha256=0d86cd55de904fe0e7db6b0212a8dadb04287262de61bf010ef3057e81dfaaab）がbase 14cad3aで
検出したresidual 7件の「touches [...]」個別根拠は、★target側でも同一コードに対して有効★
（残存内容が変化していない事の裏付けであり、target固有の未測を無くすものではない＝下記②で
targetに対し直接読み直した）。

## ② 7residual siteをtarget commitへ直接git show（当職自身の手で・a6の出力を鵜呑みにせず読み直し）

各site、`git -C /tmp/resimg-stage1-runtime-20260806 show 4a0e9036...:<path>` で当職自身が該当行±周辺を
読み、㈠OCCUPANCY_FIELDS（当職が検出器本体から独立に確認＝下記④）の列を実際に触れているか
㈡同一関数内でdelegation callable（move_appointment_slot／claim_appointment_slots）を呼んでいるかの
二点を実コードで確認した。

| file:line | 関数 | raw SQLが触れる列 | occupancy列(該当) | 同一関数内のdelegation呼出 |
|---|---|---|---|---|
| appointment_detail.py:116 | api_update_detail | UPDATE appointments SET {updates} | start_time/unit_id/duration_minutes（`occupancy_changed`判定に現れる3列） | ★有★＝`if occupancy_changed: appointment_lifecycle.move_appointment_slot(...)`（条件付・直後） |
| appointment_grid.py:768 | move_appointment | UPDATE appointments SET unit_id,start_time,end_time,version,updated_at | unit_id/start_time/end_time | ★有★＝直後に無条件で`appointment_lifecycle.move_appointment_slot(...)` |
| booking_manage.py:278 | change_booking | UPDATE appointments SET start_time,end_time,version,updated_by,updated_at | start_time/end_time | ★有★＝直後に無条件で`appointment_lifecycle.move_appointment_slot(...)` |
| next_appointment.py:69 | book_next_appointment | INSERT appointments (clinic_id,patient_id,unit_id,provider_id,start_time,end_time,duration_minutes,...) | clinic_id/unit_id/start_time/end_time/duration_minutes | ★有★＝直後に無条件で`concurrency_root.claim_appointment_slots(...)` |
| diagonal_service.py:276 | update_linked_appointment | UPDATE appointments SET start_time,end_time,updated_at | start_time/end_time | ★有★＝直後に無条件で`appointment_lifecycle.move_appointment_slot(...)` |
| diagonal_service.py:300 | update_linked_appointment(別分岐) | UPDATE appointments SET start_time,end_time,updated_at | start_time/end_time | ★有★＝直後に無条件で`appointment_lifecycle.move_appointment_slot(...)` |
| web_reservation/booking_service.py:408 | update_booking | UPDATE appointments SET {updates} | 実測=a6票`touches ['clinic_id']`（当職はupdates動的構築部を読み委譲呼出の存在を確認、列の網羅列挙は当職未実施＝下記「判らぬ」） | ★有★＝`if new_start_time: appointment_lifecycle.move_appointment_slot(...)`（条件付・直後） |

★7件悉く★＝occupancy関連列を触れており（非occupancyの逃げ道は成立せぬ）、かつ7件悉く
同一関数内でdelegation callableへの呼出が現に存在する（=「residual」＝raw SQLの置換ではなく
delegation呼出の横併存、という分類が target commitのコードでも成立）。

## ③ 独立detector再走の試行と失敗（隠さず記す）

a4原本detector script（`/tmp/resimg-verify4-cycle2-20260806/backend/tests/detect_undelegated_occupancy_mutation_a4.py`、
sha256=e13185b7e7e4a091a4399805dd562ce897dafeb031d03412b5debaa4dbf1bcff・当職が現物を再測し一致確認）を
target commitのコードへ★AST走査で機械的に再走★させる事を試みた。

手順＝`git -C /tmp/resimg-stage1-runtime-20260806 archive 4a0e9036... backend` で新設scratch dir
（`/tmp/resimg-verify2-gate3-rerun-target-a2-20260807`・当職が本工区の為に新設・既存資産に非ず）へ
backend/を書き出す方式を採ったが、★`git archive`単体（30秒timeoutで単離試験）が exit=124（timeout）と
なり完走せず★。原因は未特定のまま（当職の推測＝先行して踏んだ`git clone`時の
`lazy fetching disabled; some objects may not be available`警告と同系の可能性はあるが★断定せず★）。
★二度目の試行（迂回・別方式）は行わず、当職自身の手による②のgit show直読へ切替えた★
（門に一度止められたら形を変えて一度だけ通すは可・二度目は止まって上げよ、の条に従い、
本件は一度目の失敗で★独立した別方式（②）に既に成算があった★ため上申を要する停止ではなく
単純に手法を切替えた——但し③自体の失敗は隠さず本節に残す）。

∴ ★AST機械走査による再確認は未完（未測のまま）★。而して②（当職自身の逐語読取・
detector本体のOCCUPANCY_FIELDS/delegation callable定義との照合＝下記④）は
AST走査とは★別の方法★であり、a6のAST出力を鵜呑みにせず収束した独立証拠として成立する。

## ④ 検出器の判定基準そのものを当職が独立に確認（a6の引用を信じず現物を読む）

```
$ grep -n "OCCUPANCY_FIELDS" .../detect_undelegated_occupancy_mutation_a4.py
74:OCCUPANCY_FIELDS = {"clinic_id", "unit_id", "start_time", "end_time", "duration_minutes"}
$ grep -n "move_appointment_slot\|claim_appointment_slots" 同file
132:    "move_appointment_slot",
136:    "claim_appointment_slots",
```

②の表で用いた「occupancy列」「delegation callable」の定義は、当職が検出器本体から独立に
読み取った値であり、a6票の記載を転記したものではない（一致した事を確認したのみ）。

## ㈤ 述語⑤の結論

**述語＝偽（residual raw SQL = 7 ≠ 0、かつ非occupancyの機械根拠は成立せぬ＝7件悉くoccupancy関連列を触れている）**。

target commit（4a0e9036）は7residual siteのいずれのfileも変更していない（①）ため、この結論は
足軽6号がbase(14cad3a)で示した結論と★数値上は同一★だが、当職は②で★target commitのコード自体を
当職自身の手で読み直し★、a6の出力を根拠に据えず収束させた（③の独立AST再走は未完のまま・
これは②の妥当性を損なわない——手法が異なるため）。

★residual=0にはならず、かつ非occupancyの根拠も立たぬ★ ∴ 述語⑤は★不成立が確定★。

## 重複防止

足軽4号のmatrix（元検出器の設計・base e88e7582時点の初回検出）・足軽1号の実装（E-3根治・
appointment_lifecycle.pyへのguard追加のみ、residual 7siteのコードには一字も触れず）とは
★重ならぬ★——当職の測りは「residual 7siteがtarget commitでも占有関連かつdelegation併存で
あるか」という★DB/コード読取層の再確認★であり、足軽4号は検出器の設計・実装、足軽1号は
guard実装（別module）である。足軽6号（app層detector再走・base 14cad3a対象）とも対象commitが
異なる（当職はtarget 4a0e9036、足軽6号はbase 14cad3a）。

## 己の手で為した事

- `git -C /tmp/resimg-stage1-runtime-20260806 cat-file -e 4a0e9036...` でtarget commitの実在を独立確認。
- `git -C ... log -1`／`git -C ... merge-base --is-ancestor`／`git -C ... diff --stat` の3コマンドで
  base→targetの差分ファイル一覧を機械的に取得（母集団の不動を確認）。
- 7residual site全件について `git -C ... show 4a0e9036...:<path>` を実行し、当職自身の目で
  raw SQL文・delegation呼出の有無を読み、上記②の表を作成。
- `grep -n "OCCUPANCY_FIELDS"`／`grep -n "move_appointment_slot\|claim_appointment_slots"` を
  検出器本体へ実行し、判定基準そのものを当職が独立に確認（a6の引用を鵜呑みにせず）。
- `git -C ... archive 4a0e9036... backend -o /tmp/verify2_backend_archive.tar` を30秒timeoutで
  単離試験し、exit=124（timeout）を確認（原因未特定・失敗をそのまま記録）。
- a1のworktree（`/tmp/resimg-cycle2-f123-clean-20260806`）に対しては`git log -1`／`git status --porcelain --branch`
  のみ実行（読取専用）——この際、当職の操作以外の理由で当該worktreeにdirtyな未commit差分
  （appointment_detail.py／appointment_lifecycle.py／appointment_service.pyがM表示）が存在する事を
  検出したが、★当職はこれを触れず・本工区の対象はcommit済のtarget SHA自体のみであり、
  worktreeの現在のdirty状態は本工区のscope外として、事実のみ記録し裁定はしない★
  （下記「判らぬ」参照）。
- a4原本detector scriptの現物へ`sha256sum`を実行し、a6票記載値との一致を確認。

## 判らぬ・別枠

- ★AST機械再走が未完（③）★——git archiveの timeout原因は未特定。再試行（別方式・例えば
  `git -C <repo> --work-tree=<scratch> checkout` 等）は本工区の時間内では行わず、
  ②の逐語読取で結論に足る証拠は得たと判じ、これ以上の手法追求は行わなかった。
  ★之を「AST機械証拠で0.6.確定」と書くのは過大主張ゆえ、②が別方法である事を明記して代替した★。
- ★web_reservation/booking_service.py:408 のUPDATE文が動的に構築する`updates`列一覧の全列挙は
  当職自身では行っていない★（a6票のdetector出力`touches ['clinic_id']`を引用のみ・当職の逐語読取は
  「delegation呼出の存在」に留まる）。occupancy根拠が不成立という結論には影響しない
  （delegation呼出が条件付きで存在する事自体は当職が直接確認済）が、列一覧の完全独立再現は未実施。
- ★a1 worktreeのdirty差分（appointment_detail.py等3file M表示）の由来・意味★＝未測・裁定せず。
  当職が観測した時点（2026-08-07T01:5x台）の事実のみ記録。current_order_15の対象はcommit済の
  4a0e9036であり、worktreeの現在の作業状態そのものではない為、本工区の結論に影響しない。
- ★residual 7siteにおけるraw SQLとdelegation呼出の実行順序の意味論★（足軽6号㈤節・足軽1号票
  「判らぬ・別枠」節で既に射程外と明記）は、当職も同様に射程外として引き継ぐ（本工区の対象を
  広げない）。

## 閉じ

- 述語⑤（target 4a0e9036）＝★不成立（residual=7≠0・非occupancy根拠不成立）★。
- 分離＝測るは当職・直すは足軽1号／fix=0・commit=0・push=0・merge=0・DDL=0（全順守）。
- 本票のみで新規file作成1本（本file）。既存fileは一字も変更せず。
- 軍師secondへ本票を監査提出する（別便）。
