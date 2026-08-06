# 足軽4号 → 家老second: patch追加9 test の四軸再分類（御裁12:31:38下命・実走せず分類のみ）

断面: 2026-08-06T12:42:47+0900 JST（当職 実測。以下は悉く己で打ち直した値、記憶に依らず）
本便は read-only。hakudokai-dev への書込・commit・実走（pytest等）は一切行っていない（下命の禁に従う）。
下命=家老second msg_20260806_123328_2e1b61e2（12:33:28）。

## 前提（冒頭・同じ行、旧便は消していない）

★旧107行＝`docs/incident_logs/2026-08-06_patch_added_tests_inventory_a4.md`（sha256冒頭ec9dd2f9）は
★消していない・書き換えていない★。本便は新規fileとして追記し、旧107行の§2一覧（9件の列挙そのもの）を
唯一の母集団として引く（新規に数え直していない＝同一9件である事は旧便のtable行と本便のtable行が同じ
test名・同じfile:lineである事で照合可能）。

★冒頭に本便に掛かる条一つ（新書式・下命④より）★= 「主張には★どう検め直すか★を添えよ」（索引
`docs/incident_logs/2026-08-06_rules_index_a2.md` §G）。∴ 各分類に検め直し方を添える。

★縛りの遵守申告★= 保持／supersede の可否は論じていない（御裁が既に定めた事として扱う）。実走・一字も
書く事はしていない。旧107行は消していない。

★ファイル名の断り★= 当初`_p0_three_test_execution_result_a6.md`を書きかけたが、Write前に既存内容を
読み確認した所★足軽6号の別件（P0 watchdog heredoc注入）が既に同名で在った★（衝突）。上書き寸前で
気付き、本fileの別名へ切替えた。足軽6号のfileには一切触れていない。

## §0 本便で新たに実測した事（旧便からの追加分。旧便が「列挙」に留めたのに対し、本便は各testの
中身と、baseの当該関数の中身を実際に読んで四軸を判じた）

- `/tmp/resimg-cycle2-impl-20260806` にて base(`7d463edae84c704edabbd9da5465078dc62e55b1`)の
  `backend/services/web_reservation/booking_service.py`全411行を`git show`で取得し実読（`_check_conflict`/
  `create_booking`関数本体）。
- working treeの同fileを実読（`create_booking`のBEGIN IMMEDIATE化・idempotency分岐・例外map）。
- `backend/db/migrations/booking_concurrency_root.py`全301行実読。
- `backend/tests/test_booking_concurrency_root_migration.py`全164行実読。
- `backend/services/appointment_service.py`・`backend/api/appointments.py`を`grep -n
  "booking_concurrency_root\|idempot\|claim_appointment_slots\|root_tables_present"`で実測
  （hit=`claim_appointment_slots`のimportのみ。idempotency系関数のimportは0件）。
- `docs/incident_logs/2026-08-06_reserveimage_cycle2_defect_handoff_a5.md`・同`_acceptance_matrix_a4.md`・
  同`_red_positive_control_design_a3.md`を実読。
- `queue/inbox/_archive/shogun-second_pruned.yaml`の`msg_20260806_083105_4fea0002`（seq149912ハンドオフ
  本文・受入①〜⑨の原文）を実読。
- `/tmp/resimg-cycle2-baseline-concurrency.txt`・`/tmp/resimg-cycle2-baseline-replay.txt`を実際に
  `cat`+`sha256sum`し、a3便が引用したsha256（141b59d9…／02f0b934…）と当職実測が★一致★する事を確認
  （他者の引用を鵜呑みにせず己の手で検めた＝この2fileは他工区で既に実走済のログであり、当職が新規に
  実走したものではない。当職はfileの実在・sha一致・内容を確認したに留まる）。

## §1 母集団（旧107行§2と同一9件。file:lineは working tree 実測値）

| # | test名 | file:line |
|---|---|---|
| 1 | test_true_two_connection_same_slot_only_one_active_row | test_phase2_2_booking.py:355 |
| 2 | test_exact_request_replay_returns_same_appointment_id | test_phase2_2_booking.py:408 |
| 3 | test_durable_idempotency_key_and_slot_claims_after_migration | test_phase2_2_booking.py:432 |
| 4 | test_gate2_baseline_scan_zero_and_15_minute_grid | test_booking_concurrency_root_migration.py:58 |
| 5 | test_gate2_duplicate_stops_before_any_schema_mutation | test_booking_concurrency_root_migration.py:68 |
| 6 | test_gate3_rehearsal_schema_backfill_and_exact_rollback | test_booking_concurrency_root_migration.py:82 |
| 7 | test_slot_claims_block_offset_overlap_and_partial_index_blocks_status_bypass | test_booking_concurrency_root_migration.py:110 |
| 8 | test_cancel_release_allows_slot_reuse | test_booking_concurrency_root_migration.py:124 |
| 9 | test_idempotency_reconnect_mismatch_and_stale_pending_does_not_block_slot | test_booking_concurrency_root_migration.py:137 |

## §2 軸の定義（当職の解釈・下命に忠実に）

- ㈠独立出所＝本patchとは別に、この test が検証する要件を事前に定めた文書が存在するか。
- ㈡baseline陽性対照＝base(7d463ed)へこの test を当てると、defect特定的なREDになるか（import/型不一致
  等の“関係ない理由”での落ちは非該当とする）。
- ㈢target回帰＝patch後のtarget実装（root migration機構）の新規挙動を守る回帰testとして機能するか。
- ㈣どの門を閉じ得るか＝受入①〜⑨（seq149912ハンドオフ原文）またはitem13（旧code RED維持要件、原文＝
  `.../reserveimage-cycle2-concurrency-idempotency-evidence-and-root-design-20260806.md` L225、a3便経由
  で当職が特定）のどれを、どこまで閉じるか。

## §3 四軸判定（test毎・三値=該当／非該当／判じ難き）

### #1 test_true_two_connection_same_slot_only_one_active_row (test_phase2_2_booking.py:355)

| 軸 | 三値 | 何を見てそう判じたか |
|---|---|---|
| ㈠独立出所 | 該当 | a3便§2-1が特定した原文＝`.../evidence-and-root-design-20260806.md` L225「item13」の「陽性対照2.1」がこのtest名を固有名で指す（当職はa3便のsha256/行番号citationを実読したのみで、原本fileそのものはhonbucho配下ゆえ当職からは未到達＝伝聞一段）。 |
| ㈡baseline陽性対照 | 該当 | `/tmp/resimg-cycle2-baseline-concurrency.txt`（sha256=`141b59d9f7a15aef…`・当職実測sha一致）を全文読了。`AssertionError: assert 2 == 1`実測。base `_check_conflict`(base:169-180)がcheck-then-insertでlockを持たぬ構造と整合。 |
| ㈢target回帰 | 該当（留保付） | working tree実測=`create_booking`が`BEGIN IMMEDIATE`(booking_service.py:214)でwriter lockを先取りする設計に変わっており、barrierで強制した競合窓を閉じる方向の変更と読める。★但し当職はpatch後の実走はしておらぬ＝「設計上該当」であり実測GREENの確認ではない★。 |
| ㈣どの門 | 該当（部分） | item13「陽性対照2.1」を構成する事は該当。★但しitem13が真に求める「migration適用後も既知欠陥snapshotへ再度当てて機械的にREDを再検定する仕組み」は、a3便§2-4実測（当該仕組みはpatch・test fileに見当たらぬ）と当職も同じ範囲を読んで同意＝この部分は非該当。 |

検め直し方: `git show 7d463eda…:backend/services/web_reservation/booking_service.py`の169-180行を再読し
lock非存在を確認、`/tmp/resimg-cycle2-baseline-concurrency.txt`を再度sha256sumし`141b59d9f7a15aefe793367e82cfcdc436fc3f51479ec3a49a7f3cef24dd30da`と一致するか照合せよ。

### #2 test_exact_request_replay_returns_same_appointment_id (test_phase2_2_booking.py:408)

| 軸 | 三値 | 何を見てそう判じたか |
|---|---|---|
| ㈠独立出所 | 該当 | 同上item13「陽性対照2.2」がこのtest名を固有名で指す（a3便§2-2経由）。 |
| ㈡baseline陽性対照 | 該当 | `/tmp/resimg-cycle2-baseline-replay.txt`（sha256=`02f0b934bc27ee3f…`・当職実測sha一致）を全文読了。`BookingConflictError: 指定の時間帯には既に予約が入っています`実測。base `create_booking`にreplay吸収機構が皆無な事（base:198-233に該当ロジック無し）と整合。 |
| ㈢target回帰 | 判じ難き | 本testが検査する経路＝patch後`booking_service.py`L260-278の「idempotency_key未使用時のexisting早期return（key無しsilent replay）」。★この経路自体が本御裁で★supersede確定（L408-429）★の対象★。「今後も守るべき挙動を守る回帰」と読めば非該当（置換対象を固定するtestは回帰の名に値しない）、「現patch codeがGREEN化する事実を守る回帰」と読めば該当——読みが割れるため判じ難きとする。 |
| ㈣どの門 | 該当（部分） | item13陽性対照2.2を構成。#1と同じ理由でitem13の「再検定の仕組み」要件は非該当。 |

検め直し方: `/tmp/resimg-cycle2-impl-20260806/backend/services/web_reservation/booking_service.py`の
249-278行を再読し、`existing`早期return分岐が`root_enabled and idempotency_key`偽の時にのみ通る事を
条件式で追え。

### #3 test_durable_idempotency_key_and_slot_claims_after_migration (test_phase2_2_booking.py:432)

| 軸 | 三値 | 何を見てそう判じたか |
|---|---|---|
| ㈠独立出所 | 判じ難き | F1（staff経路idempotency未配線）自体は独立文書`_reserveimage_cycle2_defect_handoff_a5.md`L29で在ると確認済。★但しF1が指すのはstaff経路（`appointment_service.py`／`appointments.py`）★。当職実測=`appointment_service.py`は`claim_appointment_slots`のみimportし`acquire_idempotency`/`complete_idempotency`は0件（grep実測）。本testが呼ぶのはWeb経路（`booking_service.create_booking`への直接キーワード引数渡し）であり、F1が指す欠陥そのものは検査していない。「F1 root要件」を独立出所として引くのは、共有基盤（`booking_concurrency_root.py`）を介した間接的関連に留まる。 |
| ㈡baseline陽性対照 | 非該当 | base `create_booking`（base:188-207実読）は`idempotency_key`引数自体を持たぬ。本testをbaseへ当てればキーワード不一致で落ちる形になり、defect特定的なREDではなくAPI形状不一致による落ち方——baseline陽性対照としては成立しない（当職はbase関数定義を実読したのみで実走はしていない）。 |
| ㈢target回帰 | 該当 | `acquire_idempotency`/`complete_idempotency`/`claim_appointment_slots`の組合せ動作（migration file 155-206行実装）を新規に検証しており、target実装（root migration機構）の挙動を守る回帰として機能する。 |
| ㈣どの門 | 判じ難き（部分） | root migration主体機構の疎通検証としては成立するが、F1が求める「staff API層のIdempotency-Key配線」の門は本testでは検査対象外（staff側は本testの呼出し対象に含まれぬ）。受入⑤（TTL等5項目）は本testでは未検査（#9が別途担う）。 |

検め直し方: `/tmp/resimg-cycle2-impl-20260806/backend/services/appointment_service.py`を
`grep -n "acquire_idempotency\|complete_idempotency"`で再走し、hit=0である事を確認せよ。

### #4〜#9 共通事実（当職再実測・旧107行§2-2と一致）

`backend/tests/test_booking_concurrency_root_migration.py`自体がbase(`7d463eda…`)に不在
（`git show`rc=128、当職本便で再実行し一致確認）。∴ #4〜#9は悉く「baseへ当てればfile自体がcollectできず
ImportError相当」であり、defect特定的なREDには成り得ない（㈡は悉く非該当）。以下は㈠㈢㈣のみ個別に記す。

| # | test名 (:line) | ㈠独立出所 | ㈡ | ㈢target回帰 | ㈣どの門（三値＋根拠） |
|---|---|---|---|---|---|
| 4 | test_gate2_baseline_scan_zero_and_15_minute_grid (:58) | 該当＝受入②（門2 non-PII scan）はseq149912ハンドオフ本文（`msg_20260806_083105_4fea0002`実読）に明記 | 非該当（共通事実） | 該当＝`scan_active_overlaps`/`scan_slot_granularity`の期待値をmigration実装(48-111行)と1対1で検証 | 判じ難き（部分）＝scanの形式自体は閉じるが、fixtureは`_add`によるsynthetic固定データ（"SYN-1"〜"SYN-4"、当職`_schema`/`_add`実装を実読して確認）であり、受入②が求める「clean隔離DB上の（既存）実データscan」の代替にはならない |
| 5 | test_gate2_duplicate_stops_before_any_schema_mutation (:68) | 該当＝受入②後段「重複1件ならapply停止」 | 非該当（共通事実） | 該当＝`apply_booking_concurrency_root`が`DuplicateAppointmentsFound`送出時にDDL変更前(222-224行)で停止し`root_tables_present`が偽のままである事を検証、実装と一致 | 該当（部分）＝停止ロジックの正しさは合成データでも論理として検証可能であり此処は閉じると判ずる。★但しscanの网羅性そのもの（#4の欠）は本testでも埋まらぬ★ |
| 6 | test_gate3_rehearsal_schema_backfill_and_exact_rollback (:82) | 該当＝受入③（SHA一致後のみapply）・受入⑧（pre/post overlap=0、FK/integrity OK） | 非該当（共通事実） | 該当＝`uq_appointments_active_exact_start`存在・`claims_backfilled==10`・FK/integrity OK・SHA一致確認いずれも実装(247-301行)と対応 | 判じ難き（部分）＝機構としての正しさは閉じるが、正式予行手順書（`reserveimage-cycle2-ddl-rehearsal-rollback-20260806.md`・当職未読=honbucho配下ゆえ到達不能）に沿った人手運用の遂行そのものの代替にはならない（本testは`tmp_path`上のfile copyのみ） |
| 7 | test_slot_claims_block_offset_overlap_and_partial_index_blocks_status_bypass (:110) | 該当＝受入⑥（slot claim契約）のcreate相当 | 非該当（共通事実。加えて当職追加確認＝`claim_appointment_slots`自体もbaseの`booking_service.py`にimport無し） | 該当＝UNIQUE index・PRIMARY KEYの両方が重複/offset重複を`IntegrityError`で弾く事を検証、実装(247-277行)と一致 | 該当（部分）＝受入⑥のcreate相当のみ閉じる。当職実測（前便`_acceptance_matrix_a4.md`と一致）＝★update/cancel相当のslot claim契約は本patch6path中0件★であり、本testもこの欠を埋めていない |
| 8 | test_cancel_release_allows_slot_reuse (:124) | 該当＝受入⑥のcancel相当 | 非該当（共通事実） | 該当＝cancel後のslot解放→再claim可能である事を検証、`release_appointment_slots`実装(150-152行)と一致 | 判じ難き（部分）＝本testは`release_appointment_slots`という低レベル関数を直接呼ぶ形であり、実際のcancel API（`booking_service.cancel_booking`）がこの関数を正しく呼んでいるか自体は本testのscope外（当職未確認＝`cancel_booking`本体499行以降は本便で読了していない） |
| 9 | test_idempotency_reconnect_mismatch_and_stale_pending_does_not_block_slot (:137) | 該当＝受入⑤（TTL未失効block/失効reclaim/異payload409/completed reconnect/orphan claim0）と当職実測でほぼ1対1対応（print文`TTL_PENDING_BLOCK_BEFORE=1 TTL_RECLAIM_AFTER=1 ORPHAN_CLAIMS=0 REPLAY_EXTRA_ROWS=0`＋`IdempotencyConflict`assertが異payload相当） | 非該当（共通事実） | 該当＝5項目いずれも`acquire_idempotency`実装(155-189行)のロジックと1対1対応を確認 | 判じ難き（部分）＝受入⑤原文は経路を区別していないが、staff側（`appointment_service.py`）はidempotency_key自体を受け取れず（F1・当職grep実測）、本testが検査するのはWeb経路のみ。受入⑤を「staff/Web双方に対して閉じた」と読むのは誤りで、Web側primitiveのみと限定すべき |

検め直し方（#4〜#9共通）: `git -C /tmp/resimg-cycle2-impl-20260806 show
7d463edae84c704edabbd9da5465078dc62e55b1:backend/tests/test_booking_concurrency_root_migration.py`
を再実行しrc=128である事を確認せよ。個別根拠は各行が指すfile:lineを再読せよ。

## §4 本便が新たに開ける穴

- ㈠独立出所の判定のうち、「seq149912ハンドオフ本文」「item13原文」はいずれも当職が直接原本に到達できた
  もの（前者=`queue/inbox/_archive/shogun-second_pruned.yaml`実読、後者=a3便経由の一段伝聞・原本は
  `/home/hakudokai/hermes-departments/honbucho/reports/`配下で当職の読取範囲外）。item13関連の2件（#1・#2）
  は★当職が原本を直接読んでおらぬ一段伝聞★である事を明記する——a3便のsha256/行番号citationを信じたに
  留まる。
- ㈢target回帰の「該当」判定は悉く★静的読解（コードの構造が意図と一致する事の確認）★であり、実際に
  patch適用後のtestを実走してGREENである事を当職自身は確認していない（旧107行§0と同じ制約が本便にも
  残る）。
- #8の「cancel APIが`release_appointment_slots`を正しく呼ぶか」は本便のscope外として明記したのみで、
  当職はこの点を検証していない＝新たな未測点として残る。

## §5 己が本工区で直した誤り

無し（read-onlyゆえ直す手を持たぬ）。当初書きかけたfile名が足軽6号の既存fileと衝突していた事に
Write前のRead一発で気付き、上書きせず別名へ切替えた（§0直前の断り書き参照）。

## §6 完了条件申告

行数・sha256・測時は本便末尾に記す。三値・新たに開ける穴・検め直し方はいずれの分類にも一行以上添えた。
軍師second へ本便を監査提出する（義務）。

---
生成: ashigaru4 / 2026-08-06T12:42:47+0900 JST / read-only監査。hakudokai-dev・/tmp/resimg-cycle2-impl-20260806・
repo内他fileは一切未変更。旧便`2026-08-06_patch_added_tests_inventory_a4.md`・足軽6号`_p0_three_test_execution_result_a6.md`
はいずれも無変更。
