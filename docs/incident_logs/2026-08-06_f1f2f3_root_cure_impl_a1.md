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

提出先: 軍師second（監査義務）。karo-second収載。
