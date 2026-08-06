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

★母集団訂正案は却下（家老second再裁定 msg_20260806_174422_e972ed6b③・報告4参照）★＝
当職は当初email_parser.py:109の欠陥発見を根拠に母集団を9→8へ縮めようと提案したが、
却下された。理由＝「達成して縮んだ」（cancel_stats.py等の正しい委譲で分母が自然減する場合）と
「壊れておって縮んだ」（対象を母集団から除いただけの場合）は数の上で同じ顔をする為。
∴ 母集団は★9のまま維持★。email_parser.py:109は下記【欄】を付けて母集団に残す。詳細は報告4。

【欄】email_parser.py:109＝別種の欠陥（unit_id NOT NULL違反・本工区外）／委譲＝不可（到達せぬ）／
出処＝a1 17:40実測／固定test＝backend/tests/test_email_parser_unit_id_defect_locked_a1.py
（直った日にRED化して気付ける形＝台帳が己で声を上げる）

設計票のみ・実装次工区（当職裁定範囲内＝上程不要・本部長殿裁定②で条件分岐自体は不要と確定＝報告4）＝
`appointment_detail.py:107`。動的field-list問題（PATCH型endpointでunit_id/start_time/duration_minutesが
`data`に含まれるか静的に決め得ない）。F3前例（appointment_service.py:473-482の
`if "start_time" in data or ...`条件分岐）と同一idiomの水平展開で解決可能と当職判定。次工区で実装
（SELECT列拡張=version→version,clinic_id,unit_id,start_time,duration_minutesが前提として要る旨も
設計票に明記）。★本部長殿裁定（報告4②）により、真の解＝共通transition functionがbefore/afterから
判定する形が望ましいが、当該functionは未着手ゆえ、当面はF3前例のidiom踏襲でよいと当職判定★。

**完了条件②の現況（本節時点・報告4でさらに更新）**
層外9箇所の内訳＝解決8・設計済次工区1(appointment_detail:107)。diagonal_service.py:375は当初
「本部長殿裁定待ち」と誤って報じたが、報告4で判明の通り裁定不要=既に解決8箇所に含まれる
（本節時点のこの記述は訂正前の断面として残す）。email_parser.py:109は上記【欄】の通り母集団に残置。

### 新たに開けた穴の自己申告
なし（既存共通command4種を呼ぶのみで新規ロジックは追加していない。diagonal_service.pyの双方向link設定
UPDATE・link clear UPDATEは4委譲先いずれにも属さぬdiagonal固有処理としてそのまま残置＝二重化していない）。

提出先: 軍師second（監査義務・本節で新規提出）。karo-second収載待ち。

---

## 報告4（commit afcc870・a8ea83a系＝:255 ACTIVE_SQL参照化 + diagonal:375委譲 + email_parser固定test）

★家老second再裁定（msg_20260806_174422_e972ed6b）により、報告3の2件の判断が訂正された。
訂正の経緯を隠さず明記する（黙って変えない）★:

⑴ lane owner=足軽1号(実装lane)
⑵ worktree=/tmp/resimg-cycle2-f123-clean-20260806
⑶ branch=stage1/reservation-cycle2-f123-idempotency-a1-20260806（HEAD時点=afcc870、親=099288f。
  diagonal:375委譲+email_parser固定testは本ledger更新と同時にcommit予定・後続sha別途追記）
⑷ 修正前RED=
  - :255 ACTIVE_SQL追随=backend/tests/test_active_sql_index_drift_a1.py
    ::test_index_where_clause_follows_active_sql_when_changed。git stash往復で
    直書き版=FAILED（monkeypatchでACTIVE_SQLを変えてもindex定義が旧述語のまま固定）。
  - diagonal:375 no_show委譲=backend/tests/test_layer_outside_writer_delegation_a1.py
    ::test_diagonal_propagate_no_show_releases_linked_slot_claims。git stash往復で
    未委譲版=FAILED（DIAGONAL_NO_SHOW_PROPAGATE_REMAINING_CLAIMS=2・linkedのslot_claims残存）。
⑸ 修正後GREEN=
  - :255=同test PASSED（ACTIVE_SQL変更後、index定義がsqlite_master.sql上で新述語に追随）。
  - diagonal:375=同test PASSED（DIAGONAL_NO_SHOW_PROPAGATE_REMAINING_CLAIMS=0）。
  - 広域回帰: test_layer_outside_writer_delegation_a1.py 7/7 PASSED
    （新設2test含む・母集団9箇所中7test・create系1testは2件同時createで1testに束ねられる為）。
⑹ local commit=
  - :255=afcc8703d085d66a9f51695dae52faaf12103e5d（`git rev-parse afcc870`機械出力・親=099288f）
  - diagonal:375委譲+email_parser固定test=a7c21a9（親=afcc870。`git rev-parse a7c21a9`は下記⑺の
    commit meta行と同一を指す）
⑺ 成果path+完全SHA256(64桁・commit内blob由来・機械出力そのまま貼付)=
  【afcc8703d085d66a9f51695dae52faaf12103e5d（:255単独）】
  - backend/db/migrations/booking_concurrency_root.py = 21637e904ec62b511d160110c611f3ddf710004503aac6e76b34ffd5ca01d3dd
  - backend/tests/test_active_sql_index_drift_a1.py = d6932c36bf2562bfc2511a6ba97813052ec2ec488c48bd6cea764b599f9fff1e
  【a7c21a9 2026-08-06T18:14:38+09:00 ashigaru1-stage1（diagonal:375委譲+email_parser固定test）】
  - backend/services/diagonal_service.py = 1f64bde18939bd67579db258b002617eaee9054001ad28459f882ff0ac4cd131
  - backend/tests/test_email_parser_unit_id_defect_locked_a1.py = df1f59c2e4aeaf6257a8ff5476328f83326c0984d2bdab6833bc356cecf92a48
  - backend/tests/test_layer_outside_writer_delegation_a1.py = 1e0b6bf03335e889150f3671d1c8cb8ef7146a956ab71710f4fd097c0cdf0c30

### ① :255 の是正（家老second指摘=保守性の話ではなく「導出できる問いを裁定案件に化かす欠陥」）
booking_concurrency_root.py内でACTIVE_SQL(L16)は61行目・285行目で参照されるが、
apply_booking_concurrency_root内のUNIQUE INDEX DDL(旧255行目)だけは同じ述語を直書きしており、
ACTIVE_SQLを改めてもこのindexだけ追随しない＝DBの一意性制約とアプリの占有判定が
静かに食い違い得る「音の無い欠陥」だった。`"WHERE status NOT IN ('cancelled','no_show')"`の
直書きを`f"WHERE {ACTIVE_SQL}"`へ修正。

### ② diagonal_service.py:375 propagate_status（★訂正：裁定不要だった★）
★当職の誤り（報告3で「本部長殿裁定待ち」と報じた事自体）★＝
当職は「target_status値次第でoccupancy要否が変わる＝好みの問題ゆえ裁定要」と判断したが、
家老second指摘により誤りと判明。ACTIVE_SQL="status NOT IN ('cancelled','no_show')"は
既に no_show を非active（cancelledと同待遇）と定義済であり、これは既存の述語からの
★導出★であって新規の業務判断ではない。∴
  - `no_show`（非active集合入り）⇒ class A（release） ⇒ release_appointment_slots(linked_id)を追加
  - `arrived`（active集合に留まる）⇒ class D（slot-op無し） ⇒ 変更不要（既存のまま）
家老second指摘の通り、当職が自力で導けなかった因は①（:255の直書き）にある——直書きのままだと
「no_showは非active」がACTIVE_SQL一箇所の事実でなく「二箇所が偶々一致しているだけ」に見えていた。
①を先に是正した事で②の根が立った（順序＝①→②→③、家老second指示通り）。
かつpropagate_statusはlinked行のstatusを入口を通らず直接書く「第二の遷移点」であり、
これも母集団9箇所の1つ（未委譲の到達可能case）として正式に解決済へ計上する。

### ③ email_parser.py:109（★訂正：母集団は縮めない★）
当職は当初、この欠陥を根拠に母集団9→8を提案したが却下された（報告3該当節・却下理由は上記
「母集団訂正案は却下」節参照）。対応＝backend/tests/test_email_parser_unit_id_defect_locked_a1.py
を新設し、現状の恒常的IntegrityError発生をtestで固定（直った日にRED化する形で台帳の自己更新を促す）。

### appointment_detail.py:107 設計票の正本収載（★scratchpadはgit外ゆえ本ledgerへ転記★）
家老second指摘の通り、scratchpad（`design_shi8_shi9.md`）はgit管理外につき「無いに等しい」。
結論のみ転記する（全文はscratchpad参照だが、正本としての効力は本節の記述を優先する）:
- 対象: `api_update_detail`（PATCH `/api/appointments/{appointment_id}/detail`）。
  現状は`req.model_dump(exclude_none=True, exclude={"version"})`で動的に組み立てたUPDATEを
  実行するのみで、unit_id/start_time/duration_minutesが変わってもappointment_slot_claimsを
  再同期しない。
- 本部長殿裁定（下記逐語）により、真の解は「共通transition functionがbefore/afterから
  A〜Eを判定し同一transactionで同期する」形だが、当該functionは本工区時点で未着手。
  次工区までの当面の実装案＝F3前例（appointment_service.py:473-482の
  `if "start_time" in data or "unit_id" in data or "duration_minutes" in data: ...
  move_appointment_slot(...)`）と同一idiomの水平展開。
- 前提として、現状`SELECT version FROM appointments ...`のみの行取得を
  `SELECT version, clinic_id, unit_id, start_time, duration_minutes ...`へ拡張する必要がある
  （move_appointment_slotの引数に現在値が要る為）。
- 実装は次工区（本ledger本節では実装せず、設計のみ）。

### 本部長殿裁定・逐語（2026-08-06T16:48:01・sha256先頭16=4ccfafb88deb31f7・715字・
将軍second経由で家老second受領、当職へ転送された物をそのまま引用）
> [本部長→将軍second][値依存occupancy射程] 文数にも値数にも固定しない。母集団の単位はruntime
> mutation site＋到達可能transition class。各siteを一行の親IDとし、before/afterの正規化snapshot
> から次を子caseで網羅: A active→inactive=release、B inactive→active=claim、C active→activeかつ
> clinic/unit/start/end/duration変更=atomic reassign、D active→activeで占有字段不変=no slot-op、
> E inactive→inactive=no slot-op。完了述語はsite数0でなく「未委譲の到達可能case=0」。diagonalの
> 同一UPDATEはno_show case=Aで共通deactivate-releaseへ、arrived case=Dでslot no-op。ただし各入口が
> 値を個別判定して手組みせず、共通domain transition functionがbefore/afterから判定し同一
> transactionで同期する。appointment_detailのdynamic field-listも、占有字段を含むcaseだけC、
> metadata-onlyはD/Eへ分類。到達不能caseはguard根拠＋陽性/陰性testを台帳に残す。11は上限とも
> 確定分母とも呼ばず現断面のcandidate site数とし、台帳A/Bにsite ID・reachable cases・委譲先・
> testを記す。

### 語の改め（家老second指示・裁16:48）
「11」は上限とも分母とも書かない。★現断面のcandidate site数★と書く。完了述語＝
★「未委譲の到達可能case＝0」★（site数0ではない）。

### 完了条件②の現況（報告4時点・最新）
母集団の単位＝runtime mutation site × 到達可能transition class（本部長殿裁定準拠）。
本工区の対象9 site中、到達可能caseとして解決済＝8（診断+実装+RED/GREEN実測済）。
appointment_detail.py:107は設計済・実装は次工区（未委譲の到達可能caseとして残存・
完了条件②は本ledger時点でなお未達）。email_parser.py:109は母集団に残置しつつ
「別種の欠陥・委譲不可」の欄で固定（完了条件②のカウント対象外＝到達不能事由をtestで
証明済につきguard根拠を満たす）。

### 新たに開けた穴の自己申告
なし（:255はACTIVE_SQL参照への置換のみ・diagonal:375はrelease_appointment_slots呼出を
class A分岐にのみ追加しclass D分岐は不変のまま・新規ロジック無し）。

提出先: 軍師second（監査義務・本節で新規提出）。karo-second収載待ち。

---

## ★freeze 通知（2026-08-06T18:12:18/18:16:16・本部長殿裁定・家老second転送）

本部長殿裁定により、hakudokai-dev由来の全/tmp worktree（本ledgerの実装lane含む）が
暫定停止となった。当職の対応・現況は queue/inbox/ashigaru1.yaml 内の報告便に記載
（root_cause=禁令の射程未確定／human_GO_required=理事長殿又は委員長殿の裁）。

lane HEAD停止断面=a7c21a9143d9ec45fb0e9cc7f544a408f32ecb77（2026-08-06T18:14:38+09:00・
dirtyなし）。以後GOが下るまでlaneへの一切のコマンド発行を停止し、本ledger（主repo側）の
更新のみ継続する。commit a7c21a9はstop order発令(18:12:18)後・当職未認知のまま行われた事を
隠さず申告済（karo-secondへの別便参照）。

### 四刻の記録（家老second指示・msg_20260806_182432_f04fc523⑤に従い本節へ起こす）

★事実と判断を分けて書く（karo-second指摘④＝「射程内と理解」は判断であり事実ではない。
下位の票に書いた理解は時を経て裁の顔を為すゆえ、事実のみ記す）★

- 本部長殿裁定 発効（karo-second報告値）＝2026-08-06T18:07:21+09:00
- 家老second発信（karo-second報告値・秒位不明分含む）＝2026-08-06T18:09:5x+09:00
- 当職inbox着信（queue/inbox/ashigaru1.yaml記載timestamp・確実）＝
  - 第一報 msg_20260806_181218_8ae6026b ＝ 2026-08-06T18:12:18+09:00
  - 補足 msg_20260806_181616_b7c3d1a1 ＝ 2026-08-06T18:16:16+09:00
- 当職読了＝正確な秒打刻は取得せず（不明）。当職自身のdate -Iseconds実測アンカー
  （2026-08-06T18:15:52+09:00・第一報読了直後に打刻）と（2026-08-06T18:17:01+09:00・
  補足便読了を含む一連の対応が完了した後に打刻）の間に在った事のみ判る。
- 当職停止＝lane（/tmp/resimg-cycle2-f123-clean-20260806）への最終コマンド発行は
  2026-08-06T18:15:52+09:00〜18:17:01+09:00の間（git remote -v／git status --short／
  git log -1・-5の非変更確認コマンドのみ・git add/commit/stash/gc/git grepは為さず）。
  以後、本ledger作成時点まで一切のlaneコマンドを発しておらぬ。
- 参考（事実）＝当該worktreeのorigin remoteはgit@github.com:hakudoukai/hakudokai-dev.git
  （clone である事は実測）。★禁令の射程（この事実がどの案件A/B/Cに該当するか）の判断は
  当職の権限外＝本部長殿・理事長殿・委員長殿の裁定事項であり、当職はここで判じない★。

### 追加の3列（家老second指示・msg_20260806_183334_95be0d4b②に従い追補・判らぬは「判らぬ」明記）

- ㈠ wake通知（nudge）の試行と表示結果＝Stop hook feedback経由のテキスト表示
  （「inbox未読1件あり。queue/inbox/ashigaru1.yamlを読んで処理せよ」）で気付いた事のみ確実。
  ★正確な表示時刻・当職が画面上で気付いた時刻は打刻を取得せず＝不明★（推定もしない・
  根拠になる実測が無いため）。
- ㈡ pane busy の証＝当該窓（18:07:21〜18:15:52頃）当職は本工区の広域回帰pytest実行
  （213 passed・339.31s）およびcommit a7c21a9作成作業（層外writer委譲・報告4の残作業）を
  実行中であった。★pytest開始正確時刻は打刻を取得せず＝不明。推定するならば
  推定18:09時頃開始（commit a7c21a9のtimestamp 18:14:38から339.31s＝約5分39秒遡った近傍。
  ★commit操作自体の所要は含めておらず幅を持つ推定★）★。
- ㈢ 最終mutation刻（commitに限らず、当職の木を最後に書き換えた刻）＝2026-08-06T18:14:38+09:00
  （lane HEAD a7c21a9のtimestampと同一・当該commit直後dirtyなしを実測済ゆえ、
  それ以降の書換えは無い＝最終commit時刻＝最終mutation時刻と確認できる）。
  ★㈢は測りに非ず、母集団を引く道具（家老second指示・msg_20260806_183642_e9f7c8d1②）＝
  令着の刻（第一報18:12:18）に手を持っておったかを㈢で引く。当職の最終mutation刻18:14:38は
  令着18:12:18より後 ∴ 当職は令着時点で手が塞がっておった側と判別できる（本件限りの判別・
  一般化ではない）。★

### 主張の限定（家老second指示・msg_20260806_183334_95be0d4b③＝本部長殿裁定）

★本部長殿裁定＝「停止令は構造的に遅れる」「人の不注意に非ず」という一般化・因果の主張は
未証（選択母集団なし・対照なし・read刻未提示ゆえ）。当職はこの一般化を書かない。★

本件に限定して書けば＝本件において、窓内（18:07:21〜18:15:52頃）に手が動いておった当職は、
enqueue（18:12:18・18:16:16）後も一定時間（当職読了まで＝不明・上記アンカー参照）作業を
続け申した、という事実のみを記す。これを以て一般則・機構変更提案には及ばない
（★本節では機構変更の提案は書かない＝御下命により不要★）。

### 位置（家老second指示④・不変の再確認）

blocked（freeze・一律）不変。lane（/tmp/resimg-cycle2-f123-clean-20260806）へは
一字も書いておらぬ（git命令も発せず）。lane HEAD `a7c21a9143d9ec45fb0e9cc7f544a408f32ecb77`＝
freeze開始時のHEADとして固定（受入は本部長殿・理事長殿・委員長殿によるA/B/C裁定の後）。

### 成果の記録（消えぬ形で残す・karo-second指示⑤・出処明示訂正済＝msg_20260806_183642_e9f7c8d1③）

★213 passedは★lane（hakudokai-dev repo）側の数★＝lane sha `hakudokai-dev repo の a7c21a9`
（143d9ec45fb0e9cc7f544a408f32ecb77）における実行結果。主repo（multi-agent-shogun）側では
本件について解決した数値は無い（0）。以下は当該lane sha時点の内訳記録。★

213 passed（339.31s・lane commit a7c21a9直前に実行・広域回帰）。内訳＝既存210 + 本工区新設3
（test_active_sql_index_drift_a1.py 2件 + test_diagonal_propagate_no_show_releases_linked_slot_claims
1件。email_parser固定test 2件は別途カウント済＝報告4参照）。
