# current_order_13 五述語契約 最終票（②③④⑤ + ⒜⒝⒞再確認・足軽1号）

下命=karo-second訂正便(msg_20260807_005536・00:55:36)受入契約五述語 + 追加便(01:56:26・02:02:04)
「②→④→⑤→③の順で続行・部分targetをfinalと呼ぶな」。

測時=2026-08-07T02:35頃。worktree=`/tmp/resimg-cycle2-f123-clean-20260806`。
branch=`stage1/reservation-cycle2-f123-idempotency-a1-20260806`。

## 母集団宣言

対象＝karo-second訂正便の五述語①〜⑤ + 必須陽性対照三箇所。
実測範囲＝appointment/booking/diagonal/concurrency/web_reservation全域(backend/tests/ +
tests/ 配下の関連file、gate3 detector走査対象458ファイル)。

## commit系譜（4件・各commitごとにgit stash往復でRED→GREEN実測済）

| commit | 内容 | 対応述語 |
|---|---|---|
| `4a0e903` | move_appointment_slotへcancelled/no_show guard一元化 + move経路offset barrier | ⒜⒝一部・②の土台 |
| `37107e8` | InactiveAppointmentSlotMoveError型化 + 3呼び手(update_appointment/api_update_detail/change_booking)を409へmap | ② |
| `1c9a12b` | cross入口(Web対Staff)15分offset真並行barrier test新設 | ④ |
| `ae1d2a9` | residual 7箇所の機械一貫性test新設 + appointment_detail.py end_time drift根治(test実行で発見) | ⑤ |

現HEAD=`ae1d2a9932ace06693a02b81e20a15284858826b`／dirty=0。

## ① 全occupancy-changing入口が共通domain commandを通る

gate3 detector(足軽4号作)を自worktreeで再走(commit`ae1d2a9`断面): 未委譲1(email_parser.py:108・
既locked・本工区裁量外)・residual7・detector自体の数値は当職の4commit通しても★不変★
（appointment_lifecycle.pyはdetector自身のDELEGATED_MODULES除外対象ゆえ、guard/型追加が
構造的分類を動かさない事の裏付け・前票`2026-08-07_three_door_offset_overlap_e3_guard_new_target_a1.md`
で既報）。

## ② cancelled/no_show等terminal sourceからのmove/update/rescheduleが全入口で同じ409ないし不変

必須陽性対照3箇所を実HTTP経由(TestClient)でtest化・全PASS確認
(`backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py`):

| 呼び手 | 結果 | test |
|---|---|---|
| appointment_service.update_appointment (PUT /api/appointments/{id}・★E-3本体★) | 409 | test_staff_put_appointment_blocks_move_of_cancelled_appointment |
| appointment_detail.api_update_detail (PATCH .../detail) | 409 | test_detail_patch_blocks_move_of_cancelled_appointment |
| booking_manage.change_booking (POST /booking/manage/{token}/change) | 409 | test_booking_manage_change_booking_blocks_move_of_cancelled_appointment |
| diagonal_service.update_linked_appointment (update_appointmentのbest-effort側伝播) | 不変(黙って何もせず主requestは成功) | 既存test_diagonal_update_linked_resyncs_slot_claims等で間接確認 |
| appointment_grid.move (既存guard・422) | 422(既存維持・無変更) | 既存test群 |
| web_reservation booking_service.update_booking (既存guard・None) | None返し(既存維持・無変更) | 既存test群 |

★diagonal_service経由が「409」でなく「不変」である事の判断根拠★:
`update_linked_appointment`が守る対象(`linked_id`側)は、正しい運用では
`cancel_linked_appointment`の単一cancel branchでリンク解除される為、cancelled化した
appointmentがなおlinked_appointment_idを持つ状態は★本来起こらぬはずの防御的経路★。
主appointmentの更新自体は成立すべきであり、副次的なlinked側伝播のみ黙ってskipする
現行の設計(既存broad except Exception + warningログ)が適切と判断し、変更しなかった。

★guard判定ロジックの重複0★: appointment_lifecycle.move_appointment_slot内の
1箇所のみが判定を持ち、4呼び手は`InactiveAppointmentSlotMoveError`という型を
捕捉して各々の契約(409 or 黙殺)へmapするのみ(判定条件の複製なし)。

## ③ status-onlyも含めた before→after occupancy class(A〜E)の母集団化

母集団=A:active→inactive(release) / B:N/A・inactive→active(claim) /
C:active→active,occupancy変化(atomic reassign) / D:active→active,不変(no-op) /
E:inactive→inactive(no-op)。実読で分類（実装は無改変・既存構造の確認）:

| site | class | 委譲先 | 備考 |
|---|---|---|---|
| appointment_service.create_appointment | B | create_appointment_with_claim | claim同一tx |
| web_reservation booking_service.create_booking | B | create_appointment_with_claim | claim同一tx |
| diagonal_service.create_diagonal_appointment ×2 | B×2 | create_appointment_with_claim | auto_commit=False共有tx |
| next_appointment.book_next_appointment | B | claim_appointment_slots直呼(残5.①参照) | claim同一tx（一元commandは未使用だが同一tx内claim実測済=test_next_appointment_book_claims_slots） |
| email_parser._create_appointment_from_parsed | B(意図)だが★到達不能★ | — | unit_id NOT NULL違反で必ずIntegrityError・本工区外(locked test) |
| appointment_service.update_appointment (時刻/unit/duration変更) | C | move_appointment_slot | ②のguardでcancelled/no_show源からのC遷移を拒否済 |
| appointment_detail.api_update_detail | C | move_appointment_slot | 同上 + ⑤でend_time drift根治 |
| appointment_grid.move | C | move_appointment_slot | 既存422 guard + 中央guard二重防御 |
| booking_manage.change_booking | C | move_appointment_slot | ②で409化 |
| diagonal_service.update_linked_appointment | C | move_appointment_slot | ②で「不変」化(黙殺) |
| web_reservation booking_service.update_booking | C | move_appointment_slot | 既存None guard + 中央guard二重防御 |
| appointment_service.cancel_appointment / appointment_grid._execute_cancel / diagonal cancel(both) | A | deactivate_appointment | status+history+release同一tx |
| cancel_stats.api_cancel_with_reason | A | deactivate_appointment | 同上(既存test:test_cancel_stats_cancel_with_reason_releases_slot_claims) |
| diagonal_service.propagate_status(no_show枝) | A | release_appointment_slots直呼 | ACTIVE_SQLがno_showを非active定義済(裁定済・本工区外) |
| diagonal_service.propagate_status(no_show以外) | D | なし(意図的no-op) | occupancy field不変ゆえ委譲不要 |
| appointment_grid.py:534(status-only、非cancel) | D | なし(意図的no-op) | occupancy field不変・既存detector圏外(妥当) |
| diagonal_service.cancel_linked_appointment(単一cancel/unlink枝) | E相当 | なし | リンクmetadataのみ変更・occupancy不変・status変更なし |
| (cancelled化した予約へのmemo/treatment_content等 非occupancy列のみのPATCH) | E | なし(意図的no-op) | occupancy_changed=False分岐でmove_appointment_slot自体を呼ばぬ設計＝正しい黙示no-op(既存の`if occupancy_changed:`条件分岐が自然にE-classを弾く) |

★occupancy増加(B)はclaim必須★＝上表B行は悉くcreate_appointment_with_claimないし
claim_appointment_slotsを同一transaction内で呼ぶ(既存実装・変更なし・real testで実測済み)。
★occupancy減少(A)はstate+auditを同一transaction★＝deactivate_appointmentがstatus UPDATE・
history INSERT・release_appointment_slotsを一つの関数内・単一transactionで行う(既存実装・
2026-08-06 15:11中間受入裁定の対象・変更なし)。

## ④ 15分offsetのcross入口競合はactive1

`test_true_concurrency_cross_entry_offset_a1.py`（Web対Staff・真並行・独立connection+
barrier・15分offset）: old RED(active=2)→target GREEN(active=1・claims=2)実測。
5回連続実行で再現性確認(flaky無し)。

## ⑤ residual raw SQL＝0ないし非occupancyの機械根拠

`test_residual_raw_sql_slot_consistency_e3_a1.py`: 7residual箇所全てで実呼び手を叩いた後、
appointments表現在値からslot_starts()で機械計算した期待slot集合と
appointment_slot_claimsの実際が★完全一致★する事を検証・全6test PASS
(diagonal 1testが2箇所分をカバー)。

初回実行でappointment_detail.py:api_update_detailの実在drift(end_time列未更新)を検出・
根治済(上表参照)。残り6箇所は真にdriftなし=raw SQLとdelegated claimが同一occupancy状態を
指しており二重書込みの実害が無い事を機械的に確認(prose根拠から機械根拠へ格上げ)。

## 必須陽性対照三箇所（測る所であって直す所ではない、と正しく理解して対応）

karo-second訂正便で「appointment_service E-3／diagonal_service 317・375／
appointment_grid 534」は★測る所★と明示された。当職は個別guardを★足さず★、
共通層(move_appointment_slot)一元化のみで通す方針を貫いた。実測結果:

- appointment_service E-3(update_appointment) = ②のtest_staff_put_appointment...で通過確認。
- diagonal_service 317/375 = A-E分類上、317(both-cancel)はA(deactivate_appointment委譲済・
  既存test_diagonal_cancel_both_releases_slot_claimsで確認)、375(no_show propagate)はA
  (release直呼・裁定済)。いずれも★個別guard不要=既に正しい構造★。
- appointment_grid 534(status-only) = D-class(occupancy不変)。既存detector圏外は妥当
  (occupancy field自体を変えぬゆえslot-op自体が不要)。

## 回帰

411 passed / 0 failed（appointment/booking/diagonal/concurrency/web_reservation/grid全域、
commit`ae1d2a9`断面での最終実測）。

## 判らぬ・別枠（正直に残す）

- diagonal_service.update_linked_appointmentを「不変」で通した判断(②)は当職の設計判断
であり、本部長殿ないしkaro-secondの明示裁定を得たものではない。★裁定を要するなら
指摘されたし★。
- next_appointment.book_next_appointmentは`create_appointment_with_claim`でなく
`claim_appointment_slots`直呼びのまま(前サイクルでa4により「達成して縮んだ」と評価済・
本工区でも変更せず)。完全統一(create_appointment_with_claimへの一本化)は求められて
おらぬと理解し、手を付けていない。
- email_parser.py:108は引き続き本工区外・locked testのまま不変。

## 閉じ

- branch: `stage1/reservation-cycle2-f123-idempotency-a1-20260806`
- HEAD: `ae1d2a9932ace06693a02b81e20a15284858826b`
- dirty: 0
- push: 0／merge: 0（禁則順守）。DDL差分: 0（⒞=全期間通じて不要のまま）。
- ★本票をもって五述語契約②③④⑤ + ⒜⒝⒞の対応を完了と申告する（部分targetではなく
  本commit系譜4件を一体として最終targetとする）。軍師secondへ再監査提出済(別便)。★
