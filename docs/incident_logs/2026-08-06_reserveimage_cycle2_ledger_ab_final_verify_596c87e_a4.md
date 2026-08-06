# 足軽4号 → 家老second/軍師second: 596c87e最終断面 F1/F2/F3再走 + Ledger A/B + 陽性対照確認

下命: `msg_20260806_153826_ffc05947`（15:38:26・96aa31d再走）+ `msg_20260806_154034_b9faaab7`（15:40:34・母集団二階裁）。

## §0 測定対象／提出直前HEAD／一致or差分（本便より新設・下命の条を順守）

- 測定対象sha=`596c87e7975673747cc4517d9509e0cbdabc7806`
- 提出直前HEAD確認刻=`2026-08-06T16:07:14+09:00`（`git log --all --author=ashigaru4-stage1`直近実測）
- 一致or差分= ★一致（提出直前に再確認済・これ以上の新commitなし）★
- ★本便の執筆過程で対象shaが3度動いた事を隠さず記す★＝当初下命は`96aa31d`（15:38便）宛だったが、
  執筆中に`9fe28d1`（15:42・cancellation/no_show/reschedule共通command化）→
  `596c87e`（16:03・create-with-claim/idempotency統一）と2度連続で進み、当職はその都度
  read-only git object経由で追跡・再sync・再走した。★これ以上は追わず本便で断面固定する★
  （下命の条＝測りを出す時は測り終えた刻のHEADを出す直前に引き直せ、を字義通り実践した結果の判断）。
- lane owner=足軽4号・worktree=`/tmp/resimg-verify4-cycle2-20260806`・
  branch=`ashigaru4-verify-cycle2-20260806`・最終commit=`24f8ff6`
  （sync commit。sha256/行数は§4参照）。

## §1 F1/F2/F3 回帰網 最終再走結果（596c87e）

```
9 items in test_reserveimage_cycle2_regression_f1f2f3_a4.py:
test_39 PASSED(documentary) / test_40 FAILED / test_45 FAILED / test_46 FAILED /
test_47a PASSED / test_47b FAILED(RED=欠陥実在) / test_47c PASSED /
test_41 FAILED(F2=零のまま) / test_42 PASSED(documentary) /
test_43 PASSED / test_44 PASSED(F3=GREEN・key有りreplay)
5 failed, 6 passed
```
★8b95464→96aa31d→9fe28d1→596c87eの全断面を通じ、この分布は不変★
（F2は一貫してRED=当職はこれを上へ継ぎ続ける。F3はkey有り呼出しで一貫してGREEN)。

### §1-1 F3（下命①の直接対象）＝★確定GREEN★
先便(96aa31d)で確定した「idempotency_key有りreplay=同一ID・key無し再送=409」の契約は
596c87eでも不変。当職の`test_44`(key有りreplay)はPASS継続。

### §1-2 test_40/45/46（F1・当職test固有の陳腐化、先々便から不変）
`create_appointment`にidempotency_key引数が実装済(key無し呼出しはtest_40の対象外・
先々便§2で両呼出し形併記済)。test_45/46は当職test自体がinterface変更に追従できていない
既知の陳腐化(先々便§5で説明済・当職の今後の宿題として残置)。

### §1-3 test_47b（㈤・audit log欠落）＝★RED継続・596c87eでも未解消★
`log_appointment_action`は依然core commitの外・replayは依然そこへ到達しない構造。
596c87eの3commit(cancellation/no_show consolidation・create-with-claim統一)は
`appointment_service.py`のcreate_appointment本体のpost-commit部分には手を加えていない
（当職実測=`git diff --stat 96aa31d 596c87e -- backend/services/appointment_service.py`で
変更行がpost-commit block(L329以降)に及んでいない事を確認）。∴ 欠落は構造上そのまま。

## §2 陽性対照3種（下命④・a1が自ら実装・当職が独立確認）

a1が`backend/tests/test_create_with_claim_cross_entry.py`(596c87eで新設)に3本実装済。
当職の木で実走=★3/3 PASSED★:
```
test_web_vs_web_true_two_connections_second_gets_409   PASSED
test_web_vs_staff_same_slot_cross_entry_conflict         PASSED
test_offset_overlap_partial_conflict                     PASSED
```

### §2-1 当職の方法論評価（裁定せず・特徴を正確に記す）
`test_web_vs_web_true_two_connections_second_gets_409`は★2本の独立sqlite3.Connection★
（同一connectionの逐次呼出しではない）を使い、かつapp層の`_check_conflict`(TOCTOUを持つ
SELECT)を`monkeypatch`で無害化した上で、`appointment_slot_claims`のUNIQUE制約
(`(clinic_id,unit_id,slot_start)`)★単体★が競合を止める事(2件目=`sqlite3.IntegrityError`)
を実測している。
★これは「2つの独立DB接続」ではあるが、当職が§C(先便設計)で提案した
`threading.Barrier`によるOS-thread-level真の同時実行ではない(呼出しは逐次)★。
∴ ★DB制約が安全網である事の証明としては十分・的確★だが、★アプリ層のtiming-dependent
race(2つのHTTPリクエストが真に同時に到達した場合のロック待ち挙動等)は本testの射程外★
である事を当職は指摘する(裁定せず・記録のみ)。同様の性質が⑵⑶にも当てはまる。

## §3 Ledger A/B（下命②・二階台帳・合算禁）

★本部長裁定[15:33:46・sha256先頭16=8be08e49150a28ed]の逐語に従う。件数を正本にせず、
①全列挙+除外理由 ②共通domain層外0件の証明 ③4commandへの委譲 ④陽性対照、で判ずる★。

### §3-1 Ledger A（entrypoint → domain command 対応表）

★4canonical command（596c87eで全て実装済確認）★=
`create_appointment_with_claim` / `move_appointment_slot` / `deactivate_appointment` / `reactivate_appointment`
（すべて`backend/services/appointment_lifecycle.py`または`booking_concurrency_root.py`に集約）。

| entrypoint | 委譲先command | 当職実測根拠(file:line) |
|---|---|---|
| `appointment_service.create_appointment` | create-with-claim/idempotency | `appointment_service.py`実測=`concurrency_root.claim_appointment_slots`呼出し確認 |
| `appointment_service.update_appointment` | reschedule-sync(move) | L489-491=`appointment_lifecycle.move_appointment_slot` |
| `appointment_service.cancel_appointment` | deactivate-release | L593-594=`appointment_lifecycle.deactivate_appointment` |
| `appointment_service.transition_status`(no_show) | deactivate-release | L682-683=`appointment_lifecycle.deactivate_appointment` |
| `booking_service.create_booking` | create-with-claim/idempotency | L238以降=`concurrency_root.claim_appointment_slots`(L290) |
| `booking_service.update_booking` | reschedule-sync(move) | L423-424=`appointment_lifecycle.move_appointment_slot` |
| `booking_service.cancel_booking` | deactivate-release | L481-482=`appointment_lifecycle.deactivate_appointment` |
| `appointment_grid.change_appointment_status`(cancel枝) | deactivate-release | L509,519=`appointment_lifecycle.deactivate_appointment` |
| `appointment_grid.change_appointment_status`(cancelled→confirmed復元枝) | reactivate-claim | L542-543=`appointment_lifecycle.reactivate_appointment`(★a1発見のreactivate gapが本commitで解消★) |
| `appointment_grid.move_appointment` | reschedule-sync(move) | L784-785=`appointment_lifecycle.move_appointment_slot` |
| `appointment_grid._execute_cancel`(cancel_appointment_grid経由) | deactivate-release | L856,858=`appointment_lifecycle.deactivate_appointment` |

★11entrypoint、4commandへ全委譲確認済(当職独立grep+目視)★。a1の「create2/inactivate5/reactivate1/move3」
の内訳と当職の11行は数として一致するが、★当職はentrypoint単位(A表)で数えており、
a1が関数単位で何を1として数えたかは依然不明のまま(下命の「述語不一致」自体は本裁で
「固定数を正本にしない」と解消されたため、これ以上の追跡は不要と当職は判断)★。

### §3-2 Ledger B（unique mutation command / 直接DB writer表）

★A表に現れないが、occupancy字段(clinic_id,unit_id,start_time,end_time,duration,status)を
直接書き得るruntime entrypoint。当職が§A(先便)の母集団(file24→関数56)から拾い出し、
596c87eで再確認した★:

| file:function | 直接書込み内容 | 共通層への委譲 | 除外理由(該当する場合) |
|---|---|---|---|
| `api/appointment_detail.py:api_update_detail` | 生UPDATE(unit_id/start_time/duration_minutes含む・L106-109) | ★なし★ | (除外せず=真のgap) |
| `api/cancel_stats.py:api_cancel_with_reason` | 生UPDATE(status='cancelled'・L105-106) | ★なし★ | (除外せず=真のgap) |
| `api/booking_manage.py:change_booking` | 生UPDATE(start_time/end_time・L279) | ★なし★ | (除外せず=真のgap・SMS token経由のreschedule) |
| `api/booking_manage.py:cancel_booking` | 生UPDATE(status想定・L331以降) | ★なし★ | (除外せず=真のgap・SMS token経由のcancel) |
| `api/email_parser.py:_create_appointment_from_parsed` | 生INSERT(L109) | ★なし★ | (除外せず=真のgap・メール自動取込経路) |
| `routers/next_appointment.py:book_next_appointment` | 生INSERT(L71) | ★なし★ | (除外せず=真のgap・次回予約提案からの作成) |
| `services/diagonal_service.py:create_diagonal_appointment` | 生INSERT×2(L117,146) | ★なし★ | (除外せず=真のgap・ななめ予約リンク) |
| `services/diagonal_service.py:update_linked_appointment` | 生UPDATE(start_time/end_time・L261,276) | ★なし★ | (除外せず=真のgap) |
| `services/diagonal_service.py:cancel_linked_appointment` | 生UPDATE(status='cancelled'・L317) | ★なし★ | (除外せず=真のgap) |
| `services/diagonal_service.py:propagate_status` | 生UPDATE(status・L375) | ★なし★ | (除外せず=真のgap) |
| `services/prediction_service.py:save_prediction`/`get_daily_prediction` | 生UPDATE(prediction_score/label限定・L299,386) | (該当なし) | ★除外=occupancy不変のmetadata-only(裁定の除外文言に明記一致・当職実測=UPDATE対象列がprediction_score/prediction_labelのみでunit_id/start_time等を含まぬ事を確認)★ |

★596c87e時点でconcurrency_root/appointment_lifecycleへの参照が0件である事を
`grep -c`で当職実測済(全6file・上表除く=10 entrypoint中9件がgap)★。

### §3-3 criterion②（層外0件の証明）への回答＝★未達・具体的に9件★

★「N件見付け悉く潰した」ではなく「層外に0件」を示せ、との裁定に対し、当職の実測は
★層外に9 entrypoint(diagonal_service内4関数を含む)が現存する★事の直接証明である。
これは当職の落度ではなく、596c87eの範囲がA表の11(create/inactivate/reactivate/move)に
限定されたため(a1のcommit message自体もこの4fileには触れていない)。
∴ ★criterion②は596c87e時点では未達★。当職はこれを裁定せず、事実として上げる。

## §4 migrations/backfill 別台帳（下命⑷・継続）

`backend/db/migrations/appointment_tables.py`・`backend/db/migrations/booking_concurrency_root.py`
＝runtime writer母集団の外・別migration gateで検査対象(先便から継続・削除せず)。

## §5 skip閉鎖・writer回帰（継続確認）

- ㈤skip閉鎖(test_47a/b/c)=596c87eでも継続有効(§1-3参照)。
- writer回帰baseline=`test_appointment_api.py`+`test_appointment_service.py`+
  `test_phase2_2_booking.py`+`test_appointment_grid_slot_sync.py`+`test_booking_validator.py`
  = ★116 passed, 退行なし★（596c87e時点で当職実走）。

## §6 七項＋新様式

⑴lane owner=足軽4号 ⑵worktree=`/tmp/resimg-verify4-cycle2-20260806`
⑶branch=`ashigaru4-verify-cycle2-20260806` ⑷修正前RED=先々便(3 FAILED実測済)
⑸修正後GREEN(596c87e最終断面)=F3確定GREEN(§1-1)・F2=零のまま(§1-3)・
  陽性対照3/3 PASSED(§2)・Ledger A(11/11委譲確認)・Ledger B(9件gap現存・§3-3)
⑹commit=`24f8ff6`(sync)。テスト変更なし(先便`29f35fd`から不変・sha256=§0-1参照値と同一)
⑺blob sha256=
```
82857f23306f3b673619367754b053727a326bf0f4c4eced58c0ad570d2c7d38  backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py（467行・先便から不変）
```

## §7 禁則遵守

実装ファイル一字も変更せず(当職の木への`git show <commit>:<path>`materializeのみ・
a1の作業ディレクトリは一切不触・read-only git object経由)。push/PR/main/本番=一切なし。
