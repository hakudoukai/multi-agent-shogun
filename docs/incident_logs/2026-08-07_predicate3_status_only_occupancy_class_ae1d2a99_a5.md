# target `ae1d2a99` の断面における述語③の成否（最終commit後の全述語再走・足軽5号）

## 下命

karo-second msg_20260807_023716_36c59b49 (2026-08-07T02:37:16)。本部長殿逐語令
「最終commitの後にa2/a4/a5/a6全述語再走→軍師監査」。

新final target = `ae1d2a9932ace06693a02b81e20a15284858826b`（足軽1号02:34:34完了・
karo-second独立測02:35:43済）。当職は述語③(status-only transitionのoccupancy class
母集団化)の再走を担当。

前工区 = `docs/incident_logs/2026-08-07_predicate3_status_only_occupancy_class_4a0e9036_a5.md`
（★4a0e9036断面に対する測定★・既に契約名にcommitを明記済につき本便冒頭で再確認のみ行う）。

★測時=2026-08-07T02:41:49+0900★

## 独立worktree

`/tmp/resimg-verify5-predicate3-ae1d2a99-20260807`（`GIT_NO_LAZY_FETCH=1`下で
`git worktree add --detach`・target `ae1d2a99`へdetached HEAD・エラー0＝blob要求は
発生せず(既存fetch分で充足)。`git status --porcelain`測時点で無変更）。

対象file同一性=`git show ae1d2a99...:<path>`のcommit blobと当職worktreeの working
fileをsha256照合、6file(appointment_grid.py／diagonal_service.py／
appointment_service.py／appointment_lifecycle.py／next_appointment.py／
appointment_tables.py)すべてOK(完全一致)。

a1のworktree(`/tmp/resimg-cycle2-f123-clean-20260806`)は本工区でも読取のみ
（porcelain 0・HEAD=ae1d2a99、karo-second独立測と一致）。

## `4a0e9036`→`ae1d2a99` の3新規commitが述語③へ与える影響（★先に測る★）

```
$ git log --oneline 4a0e9036..ae1d2a99
ae1d2a9 E-3⑤ residual raw SQL 機械一貫性根拠 + appointment_detail end_time drift根治
1c9a12b E-3④ cross入口(Web対Staff)15分offset真並行実証
37107e8 E-3② typed result一律mapping — InactiveAppointmentSlotMoveErrorで409統一
```

該当3commitの差分を実測した結果:

- **37107e8・ae1d2a9（一部）**: `move_appointment_slot`のguard例外を`ValueError`から
  専用型`InactiveAppointmentSlotMoveError`（`ValueError`のsubclass）へ変更し、
  `appointment_service.py`側でcatchしHTTP 409へmap。★これは述語①(move guard)の
  範疇であり、述語③(status-only遷移)の母集団・分類には無関係★——`VALID_TRANSITIONS`・
  `_FRONT_TO_BACK_STATUS`・`deactivate_appointment`・`reactivate_appointment`・
  `propagate_status`のいずれも変更なし（実diff確認済、後述）。
- **1c9a12b**: cross入口(Web/Staff)の15分offset真並行testのみ追加。status遷移ロジック
  への変更なし。
- **ae1d2a9（本体）**: `appointment_detail.py`のend_time drift根治
  （`duration_minutes`のみPATCH時に`end_time`列が再計算されなかった不整合の修正）。
  ★これは`unit_id`/`start_time`/`duration_minutes`/`end_time`に関わる述語①(move)の
  範疇であり、`status`列は一切関与しない——述語③の母集団には無関係★。

**直接確認（差分0の実測）**:
```
$ git diff 4a0e9036 ae1d2a99 -- backend/api/appointment_grid.py \
    backend/services/diagonal_service.py backend/routers/next_appointment.py
(出力なし=無変更)
```
`appointment_grid.py`（regime2の本体）・`diagonal_service.py`（`propagate_status`の
本体）・`next_appointment.py`のいずれも★1バイトも変わっていない★。
`VALID_TRANSITIONS`辞書（`appointment_service.py`）も新worktreeで再実読し、前工区と
★完全一致★（値を再掲・照合済）。`deactivate_appointment`・`reactivate_appointment`の
関数本体も差分箇所外（diff hunkが`move_appointment_slot`内のみである事を確認済）。

## 結論（★答は変わらぬ★・理由付きで明記）

前工区(`4a0e9036`)で確定した以下は、`ae1d2a99`の断面でも★全て不変のまま成立する★
（当職が新規に読み直した上での再確認であり、前便の丸写しではない）:

- occupancy class定義（terminal={cancelled,no_show}／non-terminal=残7値）
- regime1(`VALID_TRANSITIONS`)の14遷移・regime2(`change_appointment_status`の
  `_FRONT_TO_BACK_STATUS`)の4枝・`diagonal_service.propagate_status`の分類
- ★未委譲2種（regime2の"booked"枝によるterminal→non-terminal直書き2件・
  `propagate_status`のnon-terminal→no_show直書き1件）は`ae1d2a99`でも★変わらず残存★
- `status='billing'`は`ae1d2a99`でも到達不能のまま（該当箇所に変更なし）

**「target `ae1d2a99` の断面における述語③」＝ ★不成立（4a0e9036と同一の理由で）★**。

## 陽性対照（本部長殿裁定待ちにつき★期待値へ寄せず実測のまま再確認★）

前工区で報告した不一致・未委譲は`ae1d2a99`でも同一（該当箇所に変更が無い為）:
- diagonal_service 317・375＝該当行が実体を指さぬ不一致は継続（file自体は同一sha256
  ではないが——`diagonal_service.py`は無変更ゆえ★行番号もまったく同一★のはず。
  念の為`ae1d2a99`断面で再実測: 317行目・375行目とも前回と同一内容(パラメータ定義行・
  閉じ括弧行)を確認、不一致は継続）。
- appointment_grid 534＝前工区で確認した未委譲raw書込みは`ae1d2a99`でも同一箇所・
  同一内容のまま存在（`appointment_grid.py`無変更ゆえ）。

## 境界遵守声明

測るのみ・実装fix 0（当職worktree`git status --porcelain`測時点で無変更）・commit 0・
push 0・merge 0・DDL 0・migration 0・a1木は読取のみ。★入口patch禁★
（本部長殿逐語）に従い、未委譲2種を発見してもguardを足す等の是正は一切行っていない。
