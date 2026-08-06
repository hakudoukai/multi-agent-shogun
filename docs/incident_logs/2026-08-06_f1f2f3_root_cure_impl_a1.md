# F1/F2/F3 root-cure 実装（reservation-cycle2・予約・画像事業部領地）— 足軽1号

nonce=`HONBUCHO-RES-STAGE1-CYCLE2-GATES2-4-20260806-001`。base=`7d463edae84c`（hakudokai-dev、origin/pr/62/merge系）。
worktree=`/tmp/resimg-cycle2-f123-clean-20260806`（隔離。既存nonce worktree `/tmp/resimg-cycle2-impl-20260806`・
足軽4号worktree `/tmp/resimg-verify4-cycle2-20260806` はいずれも不触のまま）。

★本fileは家老second殿指示（msg_20260806_150850_68e6bd19・150850/151358）により、queue/inbox（git外・50件で
rotationし退避される）便2通の七項報告をdocsへ移したもの。新規に書き足していない（本ヘッダ節＋末尾の「その後の経過」節を除く）。

---

## 報告1（commit 8b95464・staff/API側・本部長殿[F1方式裁定]反映）

⑴ lane owner=足軽1号(実装lane)
⑵ worktree=/tmp/resimg-cycle2-f123-clean-20260806（既存nonce worktree/足軽4号worktreeとも不触のまま）
⑶ branch=stage1/reservation-cycle2-f123-idempotency-a1-20260806（HEAD時点=8b95464、親=16cd0c6→7d463ed。merge-base=7d463edae84c）
⑷ 修正前RED=
  - test_39/40/41(F1/F2契約)=3 failed（RED_output_20260806.txt）
  - test_42(update移動時slot claim陳腐化・本裁定②のslot claim統合で新規発覚した回帰)=fix一時除去の上で単体実測『Failed: expected old slot to be free after move, got 409』
⑸ 修正後GREEN=test_appointment_api.py 全42件PASS(100.81s)。加えてtest_appointment_service.py+test_booking_behavior.py+web_reservation/test_phase2_2_booking.py+test_diagonal_appointment.py+test_prediction.py=76件も全PASS(90.85s)。
⑹ local commit=8b95464c0ac5177392b0d9956155abda03bbc499（親=16cd0c6。push一切せず）
⑺ 成果path+完全SHA256(64桁・commit内blob由来)=
  - backend/api/appointments.py = 34f0dfb2144f7600e30ea2b0f4fe38770e09b3c7551f3ffc17bb0e4cba669843
  - backend/api/appointment_grid.py = ce502023007d1c2433b87cefaf14b364b9ea2fb2924f2e04d1ce9aa9c2df297b
  - backend/db/migrations/appointment_tables.py = 011f35f90fa31e9c91e331a98609aa4f078a504f92e27fc1c1f183800f21a3b3
  - backend/db/migrations/booking_concurrency_root.py = a29d71157a5ff9a9b3ea802f14120e4a6426ec82bd2a30e038b858239b07d51e
  - backend/services/appointment_service.py = 54872fbb2f77b562b021342d4a36abea123fb19a784d5daac487362009bda831
  - backend/tests/test_appointment_api.py = 60ce0fa885b2da0c7b776b13156b4dd00ec70e9920ae301de10d0d4cce4495dd

### 裁定反映の要旨
- booking_idempotency.py(独自module)を削除、appointment_tables.pyの重複table定義も削除。
- 既存booking_concurrency_root.pyのacquire_idempotency/complete_idempotencyを再利用。scope=(clinic_id,patient_id,key)→(clinic_id,operation,key)へ修正(staffのpatient_id=Noneを拒む欠陥の是正=裁定必須事項)。
- payload hashは裁定指定字段(patient_id含NULL/unit/normalized start-end/duration/category・source・provider・menu/default適用後値)で再構成。
- create_appointment=acquire→INSERT→slot claim→history→response生成→complete→commitの一単位、途中commit無し。
- 全writer回帰で新規発覚した穴を追加是正=cancel_appointment・transition_status(no_show)・update_appointment(時刻/unit/duration変更)・appointment_grid._execute_cancel(DELETE endpointの実経路=appointment_service.cancel_appointmentとは別の二重実装だった・cancel系のみ既存)にslot claim解放/再claimを追加。無ければ旧枠がstale claimで塞がれたまま(test_06が実測でRED化・fix後GREEN)。update側はtest_42で個別にRED→GREEN実証。
- test_dbフィクスチャにapply_booking_concurrency_root()を追加=slot claim invariantを全42testで常時有効化。

### 申告（当時）
appointment_grid._execute_cancelの二重実装自体(cancel_appointmentと別に存在)はAnti-Duplication上の既知の穴だが、
今回のscope外(裁定は根治単位の統合を命じたが二重実装の解消までは命じておらぬ)と判断し温存・現状回帰のみ実施。
要すれば別途上申する、と記した。

---

## 報告2（commit 96aa31d・Web側・本部長殿[F3 oracle射程裁定]反映）

⑴ lane owner=足軽1号(実装lane)
⑵ worktree=/tmp/resimg-cycle2-f123-clean-20260806（既存nonce worktree/足軽4号worktreeとも不触のまま）
⑶ branch=stage1/reservation-cycle2-f123-idempotency-a1-20260806（HEAD=96aa31d、親=8b95464→16cd0c6→7d463ed）
⑷ 修正前RED=
  - test_43/44(Web F1replay/conflict)=booking_service.pyのidempotency_key配線を一時除去の上実測『TypeError: create_booking() got an unexpected keyword argument idempotency_key』2件FAILED
  - test_45(key無し自然dedup廃止の回帰guard)=配線除去前後で不変PASS(新規RED対象に非ず・元々存在した契約の確認testと明記済)
⑸ 修正後GREEN=test_appointment_api.py(42)+web_reservation/test_phase2_2_booking.py(28)+test_appointment_service.py(13)+test_booking_behavior.py+test_diagonal_appointment.py+test_prediction.py=合計121件全PASS(204.74s)
⑹ local commit=96aa31d23269ceb7583eab96f35160b900a853d4（親8b95464。push一切せず）
⑺ 成果path+commit内blob SHA256(64桁)=
  - backend/api/web_reservation/booking.py = 14cee05a1691a13444c021d365e89643b37cb1ceacf66e3424cd6874796ccfb4
  - backend/services/web_reservation/booking_service.py = b7837d44521dfac2a88db377182fe34f67a788e7d7ecefe7938206c15e8f10be
  - backend/tests/web_reservation/test_phase2_2_booking.py = cc48e129b36097b68e94a6b410c465fb7ff8d9c9020348aaad7a05f1cadb7f65
  （backend/api/appointments.py・appointment_grid.py・appointment_tables.py・booking_concurrency_root.py・
    appointment_service.py・test_appointment_api.pyは報告1から不変・sha再掲は省略）

### 実装要旨
- booking_service.create_booking へ idempotency_key 引数を追加、api/web_reservation/booking.py から Idempotency-Key header を配線(staff側appointments.pyと対の形)。
- 既存 concurrency_root.acquire_idempotency/complete_idempotency を再利用(operation="create_booking"・staff側operation="create_appointment"と同じ(clinic_id,operation,key)scope・別table/別helper新設なし)。
- payload hash=patient_id/menu_id/正規化start-end/duration(staff側 _compute_idempotency_request_hash と対の設計、booking_service.py内 _compute_booking_request_hash として新設=契約・境界はa1の責務)。
- 検証失敗(過去日時/診療時間外/担当者不在/重複)時はacquire済pending行を自己rollback(staff側F2と対)。
- test_phase2_2_booking.pyのdbフィクスチャにapply_booking_concurrency_root()を追加した副作用として、フィクスチャ独自のappointments DDL(unit_id DEFAULT 1)が正本DDL(unit_id NOT NULL・default無)へ差し替わり、生SQL INSERTでunit_id省略の既存test 2件が回帰(NOT NULL違反)→両testへunit_id明示を追加し是正。

### 申告（当時）
- Web側はslot claim(concurrency invariant側)を今回は配線せず(裁定の明示対象=idempotency 3契約のみと判断)。Web create_bookingは引き続きunit_id固定1のcheck_conflict(SELECT重複判定)のみで、appointment_slot_claimsへは書込まぬ。必要ならば別途上申。
- appointment_grid._execute_cancel の二重実装(報告1で申告済)は今回も温存。

---

## その後の経過（本節のみ新規記述・2026-08-06T15:2x頃時点の断面）

家老second殿より本部長殿[15:11中間受入裁定]が伝達された（msg_20260806_151546_634d5430・「本便が正本」）。要旨:

- **8b95464/96aa31dはstaff/API+Web checkpointとして受領。ただしCycle完に非ず。**
- **appointment_grid._execute_cancelの二重実装は「scope外」ではなく、今回のroot根治（slot claim全writer・全入口）の★原因そのもの★と裁された。** 報告1・報告2で「scope外・温存が正」とした当職／家老second双方の判断は誤りと訂正された。
- **禁止事項**: `_execute_cancel`へreleaseを個別に足して温存する「症状patch」（当職が報告1で実施した形そのもの）は禁止。
- **差し戻し内容**: cancellation/no_show の共通domain commandを1つにまとめ、`appointment_service.cancel_appointment`・grid PUT/DELETE・`transition_status`のinactive化をそこへ委譲。共通commandがstatus/cancel metadata/history/slot releaseを同一transactionで担い、入口固有responseだけ各APIに残す。update/rescheduleも共通slot-sync契約へ寄せ、全11 writerで直接slot操作の重複/欠落0を検証する。全面書換えは不要（作り直すな・寄せよ）。
- **中間扱いの解除条件（4つ）**: ⑴Web F3 commit（本fileの報告2で充足） ⑵独立の足軽4号再走 ⑶二重入口根治（上記差し戻しの実装） ⑷pytest.skip閉鎖。
- ⑺の様式は今後もcommit内blob SHA（作業木SHAは書換え中に腐るため不使用）。

当職はこれを受け、共通domain commandへの寄せを次工区として着手する（別途ETA報告）。

---

## 報告3（commit 9fe28d1・共通domain command統合・差戻し反映完了）

⑴ lane owner=足軽1号(実装lane)
⑵ worktree=/tmp/resimg-cycle2-f123-clean-20260806（既存nonce worktree/足軽4号worktreeとも不触のまま）
⑶ branch=stage1/reservation-cycle2-f123-idempotency-a1-20260806（HEAD=9fe28d1、親=96aa31d→8b95464→16cd0c6→7d463ed）
⑷ 修正前RED=move_appointment(grid drag)・change_appointment_status(cancel/復元枝)・web側create_booking/update_bookingは本commit以前slot操作を一切行っておらず(grep実測=0件)、機構的にRED相当だった事を実装差分で確認。test_appointment_grid_slot_sync.py(新規3件)・test_46/47(web)で実証。
⑸ 修正後GREEN=test_appointment_api.py(42)+web_reservation/test_phase2_2_booking.py(30)+test_appointment_grid_slot_sync.py(3・新規)+test_appointment_service.py(13)+test_booking_behavior.py+test_diagonal_appointment.py+test_prediction.py=合計126件全PASS(204.73s)
⑹ local commit=9fe28d192318847bf253b4f341732981d47615b1（親96aa31d。push一切せず）
⑺ 成果path+commit内blob SHA256(64桁)=
  - backend/api/appointment_grid.py = cd22814870d77941d648dd5d533aa4e2c71cc1f06daee90684587a1ff96eb34f
  - backend/services/appointment_lifecycle.py(新規) = 8db360663be76a6082c84840d63620ab54d3440fcff71d361cfd6c0afc04fc92
  - backend/services/appointment_service.py = c074d263dc06f336223956bc96efb6365ace9b1db5185da8e7178720b0c7a538
  - backend/services/web_reservation/booking_service.py = 749f0f82ffb1c843d3dffcad4f399e005daf8cb37e14f2f0172f7aeb7b039be8
  - backend/tests/test_appointment_grid_slot_sync.py(新規) = 650f28004c18b611a7a8551d900a7b843d17bf40b5f7f0bc1a36ea23d1eb6910
  - backend/tests/web_reservation/test_phase2_2_booking.py = 88b57e9695a85ae3aefcdb6c762e8894aede4535bfa483bec4a4ad1c629af63c

### 設計要旨
`backend/services/appointment_lifecycle.py`を新設し、`deactivate_appointment`(status/cancel metadata/history/slot releaseを一単位)・`reactivate_appointment`(status/history/slot再claimを一単位)・`move_appointment_slot`(slot release→再claimのみ・statusのUPDATE自体は入口毎に列/validationが異なる為呼び手に残す=裁定「全面書換不要」に従いslot-sync部分のみ集約)の3関数を実装。全11 writer（create×2・inactivate×5・reactivate×1・move×3）をこの3関数経由へ統一した。

### 副産物で見つけた欠陥（裁定通り字義通りの回帰で掘り当てた物）
- `appointment_grid.change_appointment_status`のcancelled→復元枝は従来slotを一切再claimしていなかった（復元後に旧枠が空いたままになり得るバグ）。共通command化により是正。
- `move_appointment`(grid drag)・web側`create_booking`/`update_booking`は従来slot claimを一切行っていなかった（grep実測=0件）。今回の統一で全writerに拡張。

### 申告（裁定を要さぬ既存挙動の意図的維持点）
- `_execute_cancel`の既存流儀（status常にcancelled固定・no_showはvisit_status側のみ）は変更せず保持。共通commandの`history_action`引数で上書きする形にとどめた。
- `change_appointment_status`のcancel枝は元来visit_status=NULL明示だったが、共通commandはvisit_status未指定時に既存値を保持（COALESCE相当）する形へ僅かに変わった。ACTIVE_SQLはstatus列のみ参照する為inactivate自体には影響しない差分と判断（裁定を要さぬ範囲の実装判断として申告）。

### 解除条件4点の現況
⑴Web F3 commit=完了(96aa31d) ⑵独立a4再走=足軽4号の担当・当職の関与外 ⑶二重入口根治=本commitで完了 ⑷pytest.skip閉鎖=当職の成果物には`pytest.skip`/`@pytest.mark.skip`=0件（実測）。他lane artifactの事案と判断し関与せず。

---

## 報告4（commit 596c87e・create-with-claim/idempotency統合・Web含む母集団裁定反映）

本部長殿[Webを含むwriter母集団裁定]（Web booking_service.create_bookingはproduction writerであり除外せず・`_check_conflict`のSELECTはTOCTOU残でconcurrency invariant非成立・unit_id固定1も除外理由にならず）と[writer母集団の述語裁定]（母集団は件数でなく述語で定める。委譲先は4つ＝create-with-claim/idempotency・reschedule-sync・deactivate-release・reactivate-claim）を反映。

⑴ lane owner=足軽1号(実装lane)
⑵ worktree=/tmp/resimg-cycle2-f123-clean-20260806（両worktreeとも不触のまま）
⑶ branch=stage1/reservation-cycle2-f123-idempotency-a1-20260806（HEAD=596c87e、親=9fe28d1→96aa31d→8b95464→16cd0c6→7d463ed）
⑷ 修正前RED=Web側`create_booking`は本commit以前slot claim皆無（grep実測0件）。cross-entry(Web対Web真2接続/Web対Staff/offset overlap)は本commit以前は共通claim機構が無く概念上検証不可だった。
⑸ 修正後GREEN=test_appointment_api.py(42)+web_reservation/test_phase2_2_booking.py(30)+test_appointment_grid_slot_sync.py(3)+test_create_with_claim_cross_entry.py(3・新規)+test_appointment_service.py(13)+test_booking_behavior.py+test_diagonal_appointment.py+test_prediction.py=合計129件全PASS(255.10s)
⑹ local commit=596c87e7975673747cc4517d9509e0cbdabc7806（親9fe28d1。push一切せず）
⑺ 成果path+commit内blob SHA256(64桁)=
  - backend/services/appointment_lifecycle.py = 349dd169509457191bc6d5b3d8684e26a5dd8fe566d60fe646f27de3daae9982
  - backend/services/appointment_service.py = 617026878c5820db1b44f6be1c3c0aa3d9a3bfce2c50a885810e2376971ccd22
  - backend/services/web_reservation/booking_service.py = 3ac93622be9e10d68913395038de2903ceff3d3c247f835b2546486f633f4e49
  - backend/tests/test_create_with_claim_cross_entry.py(新規) = 9eda8750e8b259cb759ec6ad6c99113372abf0734453ef76a4ff61a40539786f

### 設計要旨
`create_appointment_with_claim`（INSERT→claim→history→response生成→(idempotency complete)→commitを一単位・全rollback）を`appointment_lifecycle.py`へ追加。★acquire（replay検出）は本関数に含めず呼び手側（validate_booking等の業務検証より前段）に残す★——含めると、replay要求が業務状態変化により不当に再検証で落ちidempotency保証が壊れる為。staff `create_appointment`・web `create_booking`の双方をこれへ委譲した。

### 陽性対照（裁定必須の3点、新規`test_create_with_claim_cross_entry.py`）
① key無しWeb対Web★真の2接続★（独立sqlite3.Connection 2本・逐次呼出しでなくappointment_slot_claims UNIQUE制約自体が競合を止める事を実測）＝PASS
② Web対Staff同枠cross-entry＝PASS
③ offset overlap（部分重複）＝PASS

### A/B台帳（初版・述語裁定準拠）

**A＝entrypoint→domain command対応表**

委譲済（11）＝
- create-with-claim/idempotency ×2：`appointment_service.create_appointment` / `web_reservation.booking_service.create_booking`
- deactivate-release ×5：`appointment_service.cancel_appointment` / `appointment_service.transition_status`(no_show枝) / `appointment_grid._execute_cancel` / `appointment_grid.change_appointment_status`(cancel枝) / `web_reservation.booking_service.cancel_booking`
- reactivate-claim ×1：`appointment_grid.change_appointment_status`(cancelled→confirmed復元枝)
- reschedule-sync ×3：`appointment_service.update_appointment` / `appointment_grid.move_appointment` / `web_reservation.booking_service.update_booking`

除外（2）＝`prediction_service.py:299,386`（prediction_score/labelのみでoccupancy不変・裁定で明示除外）

未着手（7箇所・6file、裁定通り黙って落とさず名指し）＝
- `next_appointment.py:71`（INSERT）
- `diagonal_service.py:117,146`（INSERT×2）
- `diagonal_service.py:261,276`（UPDATE start/end＝枠移動 → reschedule-sync委譲候補）
- `diagonal_service.py:317`（UPDATE status=cancelled → deactivate-release委譲候補）
- `booking_manage.py:279`（UPDATE start/end＝枠移動 → reschedule-sync委譲候補）
- `cancel_stats.py:105`（UPDATE status=cancelled → deactivate-release委譲候補）
- `email_parser.py:109`（INSERT → create-with-claim委譲候補）

**B＝unique mutation command/直接DB writer表**

- create-with-claim/idempotency＝`appointment_lifecycle.create_appointment_with_claim`（呼び手2）
- deactivate-release＝`appointment_lifecycle.deactivate_appointment`（呼び手5）
- reactivate-claim＝`appointment_lifecycle.reactivate_appointment`（呼び手1）
- reschedule-sync＝`appointment_lifecycle.move_appointment_slot`（呼び手3）
- 直接writer（未委譲）＝7箇所・6file（上記未着手欄と同一）

### 完了条件の現況（本節時点・後続節で更新）
完了条件②「occupancyを直接書くruntime実装が共通domain層外0件」は★未達★——上記7箇所が残存。当職の裁量で順序を選び本commitまで進めたが、これらは意図的に着手していない（黙って落としてはいない）。次工区として着手可能だが、範囲・優先順位の裁定を仰いでいる（当職の一存でこれ以上手を広げるべきか、一旦ここで区切り報告すべきか、家老second殿へ上申中）。

提出先: 軍師second（監査義務）。karo-second収載。

---

## 報告2（commit 2fe4ed9・47b根治=同transaction化・軍師second PASS済／git管理下正本への収載が本節で初）

★karo-second指摘（msg_20260806_164457_1d58e31c④）どおり、47bの記録がgit管理外(worktree+回転するinbox)にしか
無かった為、本節で正本へ収載する。以下は当職独立の`git show <sha> | sha256sum`再計算（karo-second実測とも一致・
末尾1桁の写し違いのみ訂正=下記⑺参照）。★

⑴ lane owner=足軽1号(実装lane)
⑵ worktree=/tmp/resimg-cycle2-f123-clean-20260806
⑶ branch=stage1/reservation-cycle2-f123-idempotency-a1-20260806（HEAD時点=2fe4ed9、親=55ba5a7→596c87e）
⑷ 修正前RED=test_47b_same_transaction_crash_then_retry_produces_log（新設）。log_appointment_actionの
  SystemExit注入をcreate_appointment_with_claimのcommit★後★に発生させると、retryはidempotency
  state='completed'によりcached_responseを早期returnし、appointment_logsが恒久的に0のまま
  （F47B_AUDIT_LOG_ROWS_AFTER_RETRY=0）。
⑸ 修正後GREEN=同testが軍師second指摘の同一oracleでPASS。orphan appointments=0（crash試行が全rollback）、
  appt_exists=1、log_rows>=1（同一transactionでaudit logが揃って生成）。81/81 passed・0 skipped
  （軍師second実測と一致）。
⑹ local commit=2fe4ed90b128eb3226f37465a7ef22c986ba0d79（親=55ba5a7。push一切せず）
⑺ 成果path+完全SHA256(64桁・commit内blob由来・`git show --name-only --format='' <sha> | while read -r f; do
  echo "$(git show <sha>:"$f" | sha256sum | cut -d' ' -f1)  $f"; done` の機械出力をそのまま貼付)=
  - backend/services/appointment_lifecycle.py = cc6efda4e0a42f91319e20cdbbb6ad002bb6df423b1f22996065a53bc090461d
  - backend/services/appointment_log_service.py = f60ae813491f6dc63db9265d658e4f434d6d0f499263dd061f9ceac33df0856f
  - backend/services/appointment_service.py = c19c3c6a032b39d9c5eb66f14821720125244712b8c91998cc81085ed33426af
  - backend/tests/test_appointment_log_same_transaction_47b.py = 4fb442ea1d94d8bee021195433f1f2d2bc8aedc72a187d27d90c1ef3316e7ab9

### 根治の形（同transaction化）
log_appointment_actionをcreate_appointment_with_claimのon_persistedフックとしてcommit★前★に呼ぶよう変更。

### 新たに開けた穴の自己申告（家老second・軍師second双方が嘉賞・命じられる前に自ら発見）
on_persistedがSystemExit等の"真の crash"を模す/実際に起こす場合、except節が従来Exceptionのみ捕捉だと
BaseExceptionはrollbackされず、uncommitted transactionが取り残される（=同transaction化が防ぎたい欠落を
「未rollbackの部分書込みが残る」という★別の穴★に変えてしまう）。except節をExceptionからBaseExceptionへ
広げ、確実にrollbackしてからre-raiseする事で解消（F2修正で使った同一idiom=in_transaction guard付き
rollbackを再利用・二重実装を避けた）。

### :234 の別途問い（軍師second裁定=当corrupt箇所とは別境界・修正対象外）
booking_concurrency_root.py:234のconn.commit()はSQLite foreign_keys pragmaがtransaction内でno-opになる為の
別境界であり、旧F2欠陥の再発ではないと軍師second裁定済（本commitのdiffには当該fileを一切含めていない）。

### 未着手5箇所（★層外writer台帳とは別の台帳・合算禁★＝log_appointment_action呼び手の同型欠落）
log_appointment_actionの呼び手6箇所中、本commitで直したのはcreate経路(appointment_service.py:313)の1箇所のみ。
残5箇所は同じpost-commit欠落の危険を持つ（test file docstringにも名指しで記載済＝成果物内に残す方が
便より確実に残る）:
- appointment_service.py:490（update経路）
- appointment_service.py:584（cancel経路）
- appointment_service.py:700（transition_status経路）
- appointment_grid.py:629
- appointment_grid.py:874

提出先: 軍師second（監査済・逐語=「足軽4号 F2対票は PASS。根は test_41 同一 oracle の RED→GREEN 独立再測」
「47bはPASS」）。本節はkaro-second指示による正本収載のみ（新規判断なし）。

---

## 報告3（commit 099288f・層外writer8箇所→共通command委譲・auto_commit契約変更含む）

⑴ lane owner=足軽1号(実装lane)
⑵ worktree=/tmp/resimg-cycle2-f123-clean-20260806
⑶ branch=stage1/reservation-cycle2-f123-idempotency-a1-20260806（HEAD時点=099288f、親=2fe4ed9）
⑷ 修正前RED=backend/tests/test_layer_outside_writer_delegation_a1.py（新設6test）。git stash往復で実装差分
  (appointment_lifecycle.py/diagonal_service.py/booking_manage.py/cancel_stats.py/next_appointment.py)を退避し
  再実行=6/6 FAILED（appointment_slot_claimsが0件のまま、または旧slot_startのまま残存＝layer外writerの実測）。
⑸ 修正後GREEN=git stash pop後、同6test=6/6 PASSED。広域回帰（test_appointment_api.py/
  test_appointment_grid_slot_sync.py/test_appointment_log_same_transaction_47b.py/test_appointment_models.py/
  test_appointment_service.py/test_booking_behavior.py/test_booking_concurrency_root_f2_self_rollback.py/
  test_diagonal_appointment.py/test_layer_outside_writer_delegation_a1.py/web_reservation/test_phase2_2_booking.py）
  =208 passed（新設6件含む・既存202件は無回帰）。
⑹ local commit=099288f410acb00791af29276da4d39f67da3fd5（`git rev-parse 099288f`機械出力・親=2fe4ed9。push一切せず）
⑺ 成果path+完全SHA256(64桁・commit内blob由来・機械出力そのまま貼付)=
  - backend/api/booking_manage.py = fe5a36e13f86eedd1e03e5f6f4746174037d99e5df14490c1d7074bf82594cd3
  - backend/api/cancel_stats.py = 42e4b229e2f68ce98f81c6c1abab06a37f3af73f6a8db23690fa5e0c0582667f
  - backend/routers/next_appointment.py = 89d2b4ee2f8f8c86e39e5a1ca61c497a63909ae3a5bd870d7f384c332f5934f6
  - backend/services/appointment_lifecycle.py = 28445a1fe5b9002b7d6cb49b0ae1d21c7665eb84993725fc4e97b2f9946b4868
  - backend/services/diagonal_service.py = eef3a398c7ceb79669225a4e6816690f6dbf5e5cfb71bbc0061a324cf90ad685
  - backend/tests/test_layer_outside_writer_delegation_a1.py = e3aefca55f52af6cc93f8716798da3d880027e175dcb3071a83c9e33ac505d58

### auto_commit契約変更（家老second裁定=専用2-record variantは不可・既存関数へcommit遅延の1軸を足す）
create_appointment_with_claimへauto_commit(default True)を追加。Falseの時はconn.commit()を呼ばず呼び手が
外側transactionでcommit境界を持つ。失敗時はauto_commitの値に関わらず必ずrollback（=2件目で落ちたら1件目も
道連れで消える＝全rollback契約）。既存呼び手(staff/web)はauto_commit省略=Trueの為デフォルト挙動不変
（既存202test無回帰で確認）。

### A/B台帳（報告1の続き・述語裁定準拠）

**A＝entrypoint→domain command対応表（更新）**

新規委譲済（8）＝
- create-with-claim/idempotency ×1（2レコード）：`diagonal_service.create_diagonal_appointment`
  （auto_commit=False×2呼出+単一commit）
- reschedule-sync ×2：`diagonal_service.update_linked_appointment`（261,276）/
  `booking_manage.change_booking`（279）
- deactivate-release ×2：`diagonal_service.cancel_linked_appointment`（317,cancel_both枝）/
  `cancel_stats.api_cancel_with_reason`（105）
- claim_appointment_slots直接呼出 ×1：`next_appointment.book_next_appointment`（71）
  （create-with-claim全体ではなくprimitive単体を再利用＝history/idempotency概念を持たぬ経路の為）

母集団訂正（9→8・当職実測による発見）＝
`email_parser.py:109`は当初「素直な9」に含まれると報じられたが、実測（in-memory DBでの再現）により
INSERT文がunit_id（appointments表NOT NULL制約・appointment_tables.py:81・default無し）を列挙しておらず、
実行すれば必ずIntegrityErrorを送出し、呼び手側`except Exception as e: return None`で全例外を握り潰す
構造と判明。この経路は現状コードで一度も成功していない可能性が高い（0行挿入を実測）。これは
「layer外writer=slot-claim未配線」の型ではなく★別種の欠陥（挿入経路自体が死んでいる）★であり、
機械的にclaim_appointment_slotsを足しても直らない（unit_idをどう決めるかは業務判断＝当職の裁量外）。
本commitでは不触・裁定を仰ぐ。

除外（本部長殿裁定待ち・当職裁かず）＝`diagonal_service.py:375`（propagate_status）。target_statusの値
（arrived=占有継続/no_show=解放が妥当か）次第でoccupancy要否が変わり、「UPDATE文がある→release呼べ」では
済まぬ。条件分岐案は設計票（scratchpad提出・下記参照）に明記済だが実装は本部長殿裁定後。

設計票のみ・実装次工区（当職裁定範囲内＝上程不要）＝`appointment_detail.py:107`。動的field-list問題
（PATCH型endpointでunit_id/start_time/duration_minutesが`data`に含まれるか静的に決め得ない）。
F3前例（appointment_service.py:473-482の`if "start_time" in data or ...`条件分岐）と同一idiomの水平展開で
解決可能と当職判定。次工区で実装（SELECT列拡張=version→version,clinic_id,unit_id,start_time,duration_minutes
が前提として要る旨も設計票に明記）。

**完了条件②の現況（更新）**
層外11箇所の内訳＝解決8・本部長殿裁定待ち1(375)・設計済次工区1(appointment_detail:107)・
母集団訂正により別種欠陥と判明1(email_parser:109)。「層外writer=slot-claim未配線」型として機械的に
委譲可能な箇所は本commitで★0件残存★（375/appointment_detail:107/email_parser:109の3件は、いずれも
機械的委譲ではなく別途の判断・裁定・設計が要る性質と当職が判定した箇所であり、③に述べた「0件を健全と
読むな」原則に従い、この3件の存在自体は完了条件②の未達要素として明記する）。

### 新たに開けた穴の自己申告
なし（既存共通command4種を呼ぶのみで新規ロジックは追加していない。diagonal_service.pyの双方向link設定
UPDATE・link clear UPDATEは4委譲先いずれにも属さぬdiagonal固有処理としてそのまま残置＝二重化していない）。

提出先: 軍師second（監査義務・本節で新規提出）。karo-second収載待ち。

設計票（㈧diagonal:375+㈨appointment_detail:107）はscratchpad
`design_shi8_shi9.md`として別途提出（実装禁のため本ledgerには結論のみ引用・全文はscratchpad参照）。
