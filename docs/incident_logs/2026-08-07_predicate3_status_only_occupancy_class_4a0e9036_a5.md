# target `4a0e9036` の断面における述語③の成否（status-only遷移のoccupancy class母集団化・足軽5号）

## 下命

karo-second msg_20260807_023330_e1a8c6a2 (2026-08-07T02:33:30)。

契約名 = 「target `4a0e9036` の断面における述語③の成否」
述語③(本部長殿逐語) = 「status-only transitionもbefore→afterのoccupancy classで母集団化」
境界 = 測るのみ・実装fix 0／commit 0／push 0／merge 0／DDL 0／migration 0・a1木は読取のみ

★測時=2026-08-07T02:36:52+0900、盤を測ってから本便を書く★

## occupancy classの定義（★己で引き直す・鵜呑みにせず★）

足軽4号の定義（terminal={cancelled,no_show}）を土台として提示されたが、当職は以下を
★自ら実コードを読んで独立に再確認★した:

1. `backend/services/appointment_lifecycle.py` の `move_appointment_slot` guard
   （E-3根治・本commitで追加）: `if row["status"] in ("cancelled","no_show"): raise ValueError(
   f"cannot move slot for inactive appointment ...")` ——★コード自身が"inactive"と呼ぶ2値★。
2. `deactivate_appointment` の入力検証: `if target_status not in ("cancelled","no_show"):
   raise ValueError("unsupported target_status for deactivate_appointment")` ——
   deactivate（占有解放）が許す遷移先は★この2値のみ★。
3. `booking_concurrency_root.py` のACTIVE_SQL述語（前工区・述語①測定で既に確認済）=
   `status NOT IN ('cancelled','no_show')`。

三者が指す集合は完全一致。∴ **terminal(inactive) class = {cancelled, no_show}**、
**non-terminal(active) class = 残り7値 = {tentative, confirmed, arrived, in_progress,
billing, completed, late}**。

★completedについて★: 足軽4号の指摘通り、"completed"は語感上「終わった」だが、
`deactivate_appointment`のtarget_status whitelistにも`move_appointment_slot`のguardにも
一切現れず、コード上占有解放の根拠が存在しない。当職も独立に同じ結論に達した
（`VALID_TRANSITIONS`（後述）でも`completed`からの遷移は空リスト=遷移先0だが、
それは「occupancy的に非activeだから」ではなく「業務上の終端状態だから」という別の理由
——両者を混同しない）。

## status 9値（★己で確かめる★）

`backend/db/migrations/appointment_tables.py:89` のCHECK制約を直読:
```
CHECK(status IN ('tentative','confirmed','arrived','in_progress','billing','completed','cancelled','no_show','late'))
```
9値・令の記載と一致確認済。

## 母集団の定義（★先に書く★）

**「status-only transition」= `appointments.status`列の値が変わる書込みのうち、
同一書込みで`unit_id`／`start_time`／`duration_minutes`を変更しないもの**
（述語①のmove系母集団とは排他——両方を変える書込みは無い事を実コードで確認済、
述語①のA節参照）。

**除外する物（理由を明記）**:
1. **`visit_status`のみ変更しstatus列自体は不変**の書込み（例:
   `appointment_grid.py:550-554`の"else"枝＝arrived/in_tx/billing/done/no_show選択時に
   status列が読まれさえしない）——★status遷移そのものが発生していない為、定義上
   population外★。
2. **`appointments`以外の表**の`SET status`（`visit_records_local`／`soap_records`／
   `notification_queue`／`questionnaire_sessions`／`new_patient_tracking`等、
   grep実測で17箇所発見・いずれも別表）。
3. **到達不能branch**（`appointment_grid.py:525-531`のdead code、述語①で確認済——
   `_FRONT_TO_BACK_STATUS`の全7値に両立する(status,visit_status)組が無く不実行）——
   母集団には含めるが判定対象外として区別。

## ★発見: 同一表に対し2つの異なる検証体制が併存★

`appointments.status`を書き換える経路は、当職の実測により★ガードの有無が異なる2つの
regimeに分かれる★事が判った——本工区の測定対象として重要ゆえ先に明記する。

- **regime 1 (`appointment_service.py` `transition_status`／`cancel_appointment`)**:
  `validate_status_transition(current, target)` が `VALID_TRANSITIONS`
  （下記グラフ・line 28実測）で許された遷移のみ通す。★current状態を必ず検査する★。
- **regime 2 (`appointment_grid.py` `change_appointment_status`)**: `validate_status_transition`
  も`VALID_TRANSITIONS`も★呼んでいない★。`_FRONT_TO_BACK_STATUS`マッピングのみで分岐し、
  ★現在のstatus値を条件に含まぬ枝が存在する★（後述「booked」枝）。

同一列に対し検査の有無が経路で異なる、という構造上の事実を先に述べた上で、以下
両regimeのbefore→after組を列挙する。

## A. regime 1（`VALID_TRANSITIONS`・appointment_service.py）— 14遷移

```
VALID_TRANSITIONS = {
    "tentative":   ["confirmed", "cancelled"],
    "confirmed":   ["arrived", "late", "cancelled", "no_show"],
    "arrived":     ["in_progress", "completed", "cancelled"],
    "in_progress": ["completed", "cancelled"],
    "completed":   [],
    "cancelled":   [],
    "no_show":     [],
    "late":        ["in_progress", "completed", "cancelled"],
}
```
（`backend/services/appointment_service.py:28` 実読）

| before | after | occupancy class | 経路 | 判定 |
|---|---|---|---|---|
| tentative | confirmed | non-terminal→non-terminal | raw (line 706-711) | 委譲なし(class内ゆえ述語①上は無害・述語③としては未委譲のまま記録) |
| tentative | cancelled | non-terminal→terminal | `deactivate_appointment` | 委譲済 |
| confirmed | arrived | non-terminal→non-terminal | raw | 未委譲(記録のみ) |
| confirmed | late | non-terminal→non-terminal | raw | 未委譲(記録のみ) |
| confirmed | cancelled | non-terminal→terminal | `deactivate_appointment` | 委譲済 |
| confirmed | no_show | non-terminal→terminal | `deactivate_appointment` | 委譲済 |
| arrived | in_progress | non-terminal→non-terminal | raw | 未委譲(記録のみ) |
| arrived | completed | non-terminal→non-terminal | raw | 未委譲(記録のみ) |
| arrived | cancelled | non-terminal→terminal | `deactivate_appointment` | 委譲済 |
| in_progress | completed | non-terminal→non-terminal | raw | 未委譲(記録のみ) |
| in_progress | cancelled | non-terminal→terminal | `deactivate_appointment` | 委譲済 |
| late | in_progress | non-terminal→non-terminal | raw | 未委譲(記録のみ) |
| late | completed | non-terminal→non-terminal | raw | 未委譲(記録のみ) |
| late | cancelled | non-terminal→terminal | `deactivate_appointment` | 委譲済 |

集計: non-terminal→non-terminal = 8件（すべてraw・未委譲だが占有境界を跨がぬ）／
non-terminal→terminal = 6件（すべて`deactivate_appointment`委譲済）／
terminal→terminal・terminal→non-terminal = ★このgraphには0件★（cancelled/no_show/completed
はいずれも遷移先が空リストゆえ、この経路からは復元も再遷移も一切起きない）。

## B. regime 2（`appointment_grid.py` `change_appointment_status`・ガード無し）

`_FRONT_TO_BACK_STATUS`（line 470-478実測、述語①便で既出）の枝ごとに、★currentを
条件に含むか否か★を明記して列挙する。

| 枝 | before条件 | after | 経路 | occupancy class | 判定 |
|---|---|---|---|---|---|
| "cancel" | ★current問わず★ | cancelled | `deactivate_appointment` (line 519) | any→terminal | 委譲済(current=terminalの場合も再実行され得るが冪等的・class変化なしのケースも含む) |
| "booked" | ★current問わず（guard無し）★ | confirmed | raw UPDATE (line 534-539) | **current=cancelled→terminal→non-terminal**／**current=no_show→terminal→non-terminal**／current=非terminal→non-terminal→non-terminal(class不変) | ★terminal→non-terminalの2遷移が未委譲★（`reactivate_appointment`を経由せず、既存claimの再claimなしにstatus文字列のみ書換え） |
| visit_status系(arrived/in_tx/billing/done) かつ current=cancelled | current==cancelled固定 | confirmed(restore_status) | `reactivate_appointment` (line 543) | terminal→non-terminal | 委譲済 |
| visit_status系 かつ current≠cancelled(no_show含む) | current≠cancelled | ★status列は不変★(visit_statusのみ) | raw (line 550-554) | 母集団外(status遷移なし・上記除外②該当) | N/A |

★B節の核心発見（述語①のB3を述語③の枠で再確認）★: 「booked」を選んだ場合のみ、
current状態を一切見ずに`status='confirmed'`へ直書きする。これは
**cancelled→confirmedおよびno_show→confirmedという2つのterminal→non-terminal遷移**が
`reactivate_appointment`（唯一の正規のslot再claim入口）を★経由しない★形で存在する
事を意味する。一方、同じterminal→non-terminalへ至る別の入口（visit_status系操作を
cancelled状態の予約に対し行った場合）は正しく`reactivate_appointment`を経由する。
★同じoccupancy class遷移(terminal→non-terminal)が、経路によって委譲有無が割れる★
——これが本工区で新たに定量化できた構造である。

なお current=no_show への reactivate 経路は本regime内に★存在しない★
（`elif apt["status"] == "cancelled":` はno_showを含めておらぬ為）。no_showから
non-terminalへ戻る手段は「booked」枝の未委譲raw書換えのみ、という非対称も実測で判明。

## C. `diagonal_service.py` `propagate_status`（述語①のB1・本工区の枠で再分類）

前工区(述語①)でB1として確認済の未委譲caseを、occupancy classの枠で改めて分類する。

ガード: `linked_row["status"] not in ("cancelled","no_show","completed")`
（line 403実測）——before候補は non-terminal 7値中 completed を除いた6値
（tentative/confirmed/arrived/in_progress/billing/late）。

| before | after | occupancy class | 判定 |
|---|---|---|---|
| {tentative,confirmed,arrived,in_progress,billing,late} のいずれか | arrived | non-terminal→non-terminal | raw・未委譲(class内・記録のみ) |
| 同上6値のいずれか | no_show | non-terminal→terminal | raw・★未委譲★（前工区B1として既報告済の同一事象） |

## D. 未使用のstatus値（境界事例・欠陥ではなく観測）

CHECK制約は`billing`をstatus列の許容値として定義しているが、当職が実測した
`appointments.status`への全SET箇所（regime1・regime2・diagonal propagate_status・
create経路）のいずれにも`status='billing'`へ遷移させる書込みが存在しない
（`_FRONT_TO_BACK_STATUS`の"billing"エントリは`visit_status`側のみを操作し、
`status`列側は触れない）。∴ **`status='billing'`は現行コードのいずれの書込み経路
からも到達し得ない**（"dead value"・dead branchと同型のパターン・欠陥数へ混ぜない）。

## 結果（述語・断面明記）

**「target `4a0e9036` の断面における述語③」＝ ★不成立（全件が委譲されているわけではない）★**。

- non-terminal→non-terminal（占有境界を跨がぬ）遷移 = regime1で8件・diagonal Cで最大6件、
  いずれも未委譲だが★占有そのものへの影響は無い★（述語①の「非occupancy」除外基準と整合）。
- non-terminal→terminal 遷移 = regime1で6件全て委譲済／regime2「cancel」枝も委譲済／
  diagonal Cのno_show1件は★未委譲★（B1として前工区で既報告）。
- terminal→non-terminal 遷移 = regime2に2種存在し、片方（visit_status系操作からの
  間接復元）は委譲済、★もう片方（"booked"直接選択）は未委譲★。同じclass遷移が
  経路により割れる事を本工区で新たに定量化した。
- status='billing' は到達不能（母集団から除外・観測のみ）。

欠陥数へは混ぜていない——上記はいずれも「述語③の成否」の記録であり、実装是正の要否は
本工区の射程外（測るのみ）。

## 本測りが覆っていない層

- `VALID_TRANSITIONS`が実際に全呼び手で強制されているか（regime1の`transition_status`を
  経由しない別の書込み経路が将来増えても本graphは検知しない）は静的読解の限界内。
- regime2「booked」枝のfrontend側到達可能性（cancelled予約に対し実際に「booked」選択肢が
  UIへ表示されるか）は述語①B3と同様backend測定の射程外・未検証のまま。
- diagonal_service.py propagate_statusのarrived伝播（class内遷移）が機能的に安全か否かは
  未測定（構造上「委譲なし」である事のみ確認）。

## 境界遵守声明

測るのみ・実装fix 0（当職worktree `git status --porcelain` 測時点で無変更）・commit 0・
push 0・merge 0・DDL 0・migration 0・a1木は読取のみ（write 0）。
