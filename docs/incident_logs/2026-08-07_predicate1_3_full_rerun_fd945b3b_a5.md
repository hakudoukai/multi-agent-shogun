# target `fd945b3b` の断面における述語①・述語③ 再走（全述語再走・足軽5号）

## 下命

karo-second msg_20260807_055708_78c691d3（2026-08-07T05:57:08）。令 = `queue/tasks/ashigaru5.yaml`
の `current_order_13_20260807_024800_FULL_PREDICATE_RERUN`。発火条件 = 軍師second が a1 final
target `fd945b3b7adcd25f076e45e0a165ad46c7847f53` の direct test gate を PASS（05:51:40・
`queue/reports/gunshi_second_direct_test_gate_fd945b3b_reaudit_20260806.md`）・受入述語五つ
悉く充足・収載済 `bc9013c2340394b74fad46a037eeaf4e13d37091`。

当職の担当 = 述語①（occupancy-changing入口の共通domain command委譲）・述語③（status-only
transitionのoccupancy class母集団化）。両者とも前回 target `ae1d2a99` までgunshi-second PASS済。

★測時=2026-08-07T06:05ごろ★

## 木の使い方（境界遵守）

令の指定通り、木 = `/tmp/resimg-cycle2-f123-clean-20260806`（HEAD = `fd945b3b7adcd25f076e45e0a165ad46c7847f53`・
`git -C <path> status --porcelain` 測時点で無変更＝porcelain 0）を直接使用。独立worktreeは
新規に立てていない（令が「a4・a5・a6三名が同じ木を用いる」旨明示・読取のみゆえ衝突なしと判断）。

**pytestは走らせていない**（令の禁）。全て `git -C <絶対path>` による読取（diff／show／log）と
grepのみ。`GIT_NO_LAZY_FETCH=1` を環境変数として設定した上で実行。`| tee` は使用していない
（`$?` 直読）。

## `ae1d2a99` → `fd945b3b` の差分（★観測★・先に機械的に確定）

```
$ git -C <木> log --oneline ae1d2a9932ace06693a02b81e20a15284858826b..fd945b3b7adcd25f076e45e0a165ad46c7847f53
fd945b3 fix(appointment): 共通domain-transition契約(transition_occupancy_status)へ全status writerを統合 — 534 phantom-active根治 (current_order_15 本部長殿02:52:39裁定)
```

新規commit1件のみ。

```
$ git -C <木> diff --stat ae1d2a99..fd945b3b
 backend/api/appointment_grid.py                    | 177 ++++++++----
 backend/services/appointment_lifecycle.py          | 164 ++++++++++-
 backend/services/appointment_service.py            |  77 ++++--
 backend/services/diagonal_service.py               |  29 +-
 backend/tests/test_appointment_grid_slot_sync.py   | 129 ++++++++-
 backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py | 302 +++++++++++++++++++++
 6 files changed, 790 insertions(+), 88 deletions(-)
```

以下3fileは差分0（`git diff --exit-code` で exit=0 を個別に確認・diff --statの記載を鵜呑みにせず
裏取り済）: `backend/routers/next_appointment.py`／`backend/db/migrations/appointment_tables.py`／
`backend/db/migrations/booking_concurrency_root.py`。

`backend/services/appointment_service.py` の `VALID_TRANSITIONS` 辞書は無変更（grep差分0・
現物再読で8key・14遷移が前回と同一である事を確認）。`_FRONT_TO_BACK_STATUS` 辞書
（`appointment_grid.py`）も無変更（7 branch、前回と同一）。

## 述語③（status-only transitionのoccupancy class）再走 — ★答が変わる★

### occupancy class定義の変化（★観測★・コードそのものが変わった事実）

前回工区（`4a0e9036`／`ae1d2a99`断面）での当職の定義: terminal(inactive) = {cancelled, no_show}、
non-terminal(active) = 残7値（completedを含む）。当時の根拠は3箇所の実コード引用による独立確認
（move_appointment_slotのguard対象・deactivate_appointmentのtarget_status whitelist・
booking_concurrency_rootのACTIVE_SQL）で、いずれも `completed` をterminal扱いする根拠が
無かった事による。

★本commit(`fd945b3b`)で新設された `transition_occupancy_status` 関数（`appointment_lifecycle.py`）の
`is_terminal_source` 判定は次の通り（現物引用）:

```python
is_terminal_source = (
    current_status in ("cancelled", "no_show", "completed") or current_visit_status == "completed"
)
```

★併せて `move_appointment_slot` のguardも同一commitで拡張され、`status in ("cancelled", "no_show", "completed")
or visit_status == "completed"` の場合に `InactiveAppointmentSlotMoveError` を送出する形へ変わった
（前回は `status in ("cancelled", "no_show")` のみ）。

**これは前工区の当職の答えが誤りであった事を意味しない**——`4a0e9036`／`ae1d2a99`の断面では
`completed` をterminal扱いする根拠は実コード上に存在せず（当職の3引用は当時のコードに対し正確）、
本commitで★コード自体がterminal-sourceの定義を`{cancelled,no_show}`から`{cancelled,no_show,completed}`
（+ visit_status='completed'）へ拡張した★という進展である。

∴ **target `fd945b3b` の断面における occupancy class 定義 = terminal(inactive) = {cancelled, no_show,
completed(status列) または visit_status='completed'}、non-terminal(active) = 残る6値の組合せ**
（status単体では判定しきれずvisit_status列との組合せで判定する形へ変わった為、前回の「status値のみの
7分類」という単純な表では捉えられなくなっている）。

### regime1／regime2の統合（★観測★）

前回工区で確認した「二regime併存」（regime1=`VALID_TRANSITIONS`でcurrent状態を検証する
`transition_status`経路／regime2=検証なしdirect UPDATEの`change_appointment_status`経路）は、
本commitで実務上ほぼ解消された:

- regime1（`appointment_service.transition_status`）の非cancel/no_show枝は、旧来の生UPDATE + 履歴INSERTを
  廃し `transition_occupancy_status` へ委譲する形へ変更（`bump_version=True, set_updated_by=True`で
  旧来のversion/updated_by列挙動を温存）。
- regime2（`appointment_grid.change_appointment_status`）のcancel以外の全枝（booked/arrived/in_tx/
  billing/done/no_show）も同じく `transition_occupancy_status` へ委譲する形へ変更。

両regimeとも、terminal sourceからの復元は `allow_reactivate=False`（既定）で呼ぶ為
`TerminalStatusTransitionError` を送出し、呼び手側でHTTP 409へmapされる（`appointment_grid.py`・
`appointment_service.py`双方に同型のcatch節を確認・現物引用済）。

### 旧534（B3・未委譲）の解消（★観測★）

前工区で「未委譲2種」の1つとして報告した `appointment_grid.py` の "booked" 枝（terminal→confirmed
のraw書込み・reactivate_appointmentを経由せぬ暗黙復元）は、★本commitで完全に撤去された★
（旧 `elif apt["status"] == "cancelled":` 分岐が削除され、"booked" を含む全非cancel枝が
`transition_occupancy_status` の一契約へ統合）。

復元(reactivate)は generic status変更エンドポイントから完全に分離され、新設の専用endpoint
`PUT /api/appointments/{appointment_id}/reactivate` のみで許可される。当該endpointは
`appointment_lifecycle.reactivate_appointment`（既存domain command・複製せず直接呼出）へ
委譲しており、現状がterminalでない予約への誤用は422で拒否する（現物引用済・上記diff参照）。

新規追加testで動的に実証されている内容を静的に確認した（★観測★・pytestは自分で走らせていない。
karo-second令に基づき、既に完走済の direct test gate 実測値=139 passed・14 file・exit全0 を
引用するのみ）:
- `test_change_status_booked_from_cancelled_rejected_with_no_phantom_claim`
  — cancelled→booked要求が409で拒否され、status列がcancelledのまま不変、かつ同枠への新規予約が
  201（=claimが作られていない＝旧phantom-active状態が再現しない）事をassertする内容を確認。
- `test_reactivate_endpoint_restores_and_reclaims_slot`
  — 新設reactivateエンドポイント経由でのみ復元が成立し、slotが再claimされる事をassertする内容を確認。

### diagonal_service.propagate_status（B1）— 未委譲のまま（★観測★）

前工区でB1として報告した `propagate_status`（non-terminal→no_show の直接書込み）は本commitの
diff範囲に一切含まれていない（`grep -n propagate_status` を差分ファイルへ実行し0件を確認）。
★∴ B1は `fd945b3b` の断面でも未委譲のまま存在する（変更が無い為、未解消）★。

### `status='billing'` 到達不能（★観測★・前回同様）

`_FRONT_TO_BACK_STATUS`・delegation module に変更が無い為、前回確認した到達不能は本断面でも
変わらず同一のまま。

### 結論（述語③・断面明記）

**target `fd945b3b` の断面における述語③ = ★不成立（but 前回より縮小）★**——理由:
delegation module（4 domain commands + `transition_occupancy_status`という新設routing層）への
未委譲raw書込みは `propagate_status`（B1）の1種のみ残存。前工区で報告した「未委譲2種
（regime2booked枝 + propagate_status）」のうち、regime2 booked枝（B3・534由来）は本commitで
解消された。B1のみが未解消のまま残る。

## 述語①（occupancy-changing入口の共通domain command委譲）再走 — ★答が変わる★

前工区（`4a0e9036`）での population = 17件delegated(A1-A17) + B1(propagate_status) + B2
(next_appointment.py raw INSERT + 直接claim呼出) + B3(grid534・未委譲・reachability未確定)。

### 新規entry point（★観測★）

`PUT /api/appointments/{appointment_id}/reactivate` が本commitで新設された。当該endpointは
`appointment_lifecycle.reactivate_appointment` へ直接委譲しており（現物引用済・上記参照）、
★occupancy-changing入口として新規に追加され、かつ委譲済★ — 当職の population へ A18として
追加する。

### B3の再分類（★観測★）

前工区でB3として「未委譲・reachability未確定」と報告した grid "booked" 枝からの暗黙復元経路は、
本commitで完全に撤去され、`transition_occupancy_status`（terminal source時は`allow_reactivate=False`
既定によりTerminalStatusTransitionErrorを送出・409化）へ統合された。復元は新設A18のみが担う。
★∴ B3は「未委譲」の分類から外れる（該当raw書込み自体が消滅した為）★。

### B1・B2の扱い（★観測★・前回同様・未解消）

`propagate_status`（B1）・`next_appointment.py`（B2）は本commitのdiff範囲に含まれず（B2側は
diff --stat自体に無出現＝無変更を個別diff --exit-codeでも確認済）、前工区と同一のまま未委譲。

### 結論（述語①・断面明記）

**target `fd945b3b` の断面における述語① = ★不成立（but 前回より縮小・母集団18件へ変化）★**——
delegated 18件(A1-A17 + 新設A18)、未委譲2件(B1・B2)、未委譲かつ未確定(B3)は解消され0件。

## 陽性対照（★見得ぬ★・上位の手番）

前工区で報告した diagonal_service.py 317・375行目の不一致について、本部長殿②裁定により
★陽性対照は行番号を廃し関数名＋契約＋test名で再定義する事★となった旨、当職のtask YAML
「貴殿の手柄」欄に記載があるが、★再定義後の具体的な識別子（関数名／契約名／test名）そのものは
当職の手元に届いておらず未提示★。本commitでdiagonal_service.pyの該当箇所（guard-before-write
への呼び順入替え）自体は変更されており、旧行番号317・375は現在別内容を指す（当職が現物で
再確認したのみ・下記）。

★観測のみ・判定はしない★: `fd945b3b`断面のdiagonal_service.pyで317行目付近はdiagonal_second
枝の末尾（raw UPDATE文）、375行目付近はcancel/unlink処理内のraw UPDATE文（linked_appointment_id等
のクリア）であった（現物確認済）。これが再定義後の正しい陽性対照識別子と一致するか否かは
★当職には判じ得ぬ（見得ぬ・上位の手番）★——旧行番号運用の再利用はせず、次便で識別子（関数名＋
契約＋test名）が届き次第、その形で再照合する。

## 観測と推論の線引き（令 05:57 明示事項への対応）

- ★観測★（実測・現物引用のみ）: 上記の全diff内容・grep結果・exit code・現行ファイル内容の引用。
- ★推論★（当職の解釈）: 「前工区の答えが誤りではなくコードが進展した」という記述、および
  述語①③の結論を「不成立（but縮小）」とまとめた評価そのもの。母集団数（18件delegated等）は
  当職の分類基準に基づく集計であり、上位の再定義（陽性対照の識別子変更）が届けば再集計が
  必要になり得る。
- ★判らぬ点★: 陽性対照の再定義後の具体的識別子（前節参照）。本部長殿の当初裁定文言
  「534=D判定は動的証拠と矛盾」の「動的証拠」の中身そのもの（本commitの新設testが該当する
  可能性が高いと当職は推測するが、これも★推論★であり本部長殿からの直接の確認は得ていない）。

## 境界遵守声明

測るのみ・pytest 0（走らせていない）・実装fix 0・commit 0・push 0・merge 0・DDL 0・migration 0・
a1木は読取のみ（`git status --porcelain` 測時点で無変更確認済）・入口patch禁を順守。
`GIT_NO_LAZY_FETCH=1` を通し全git command実行・`| tee` 不使用・`git -C <絶対path>` のみ使用
（`cd` 不使用）。
