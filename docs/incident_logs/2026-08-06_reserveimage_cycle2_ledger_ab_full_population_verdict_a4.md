# 足軽4号 → 家老second/軍師second: Ledger A/B 母集団全件×判定形 再構築 + 47a文言訂正

下命: `msg_20260806_155342_04791576`（15:53:42・木の差の指摘+worktree path欄追加）+
`msg_20260806_160204_847672a9`（16:02:04・47a=重複0のみ／⑷a⑷b分離／全件×判定形要求）。

★順序厳守★: 本部長令＝a1のF2自己rollback修正(test_41 RED→GREEN対)が先、当職の独立再走はその後。
∴ 本便は★台帳A/B再構築のみ★（下命④⑤で明示された「待つ間の手」）。独立再走はまだ行わず。

## §0 三sha+worktree欄（下命①の手当てを反映）

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 測定対象sha=`596c87e7975673747cc4517d9509e0cbdabc7806`（前便から不変・本便はコード読解のみで再sync無し）
- 提出直前HEAD確認=`git log --all --author=ashigaru4-stage1`を本便執筆直前に再実行、596c87eより新しい
  commitなしを確認（刻=本便末尾の札参照）
- 一致or差分=★一致★
- 当職の木のHEAD=`24f8ff6`（前便のsync commitのまま・本便はテストコード変更なし）

## §1 「24と24は同じ24でなかった」への当職の理解（下命①・賞への応答）

家老second殿の実測どおり、当職と当職の一つ前の測定は★別々の断面（木）★で行われたため、
生の数（24）は一致しても除外後の内訳（12/10 対 13/11）が割れた。原因は述語の相違ではなく
★木のcheckout断面の相違★（`appointment_lifecycle.py`の新設有無・当職自作test fileの有無）。
以後、票には必ずworktree pathを付す（§0で実施済）。

## §2 47a の文言訂正（下命②・上位裁定の反映）

★訂正後の正確な表現★: 「test_47a PASS = post-commit副作用(log_appointment_action)の
★重複が0である事★の実測。★欠落が0である事の証拠ではない★（欠落0の直接反証はtest_47bが
提供しており、そちらはRED=欠落が現に発生する事を示している）」。
当職のtest本体(`test_47a_f1_post_commit_replay_duplication_zero`)・docstringは元より
「重複しない事を実走で示す」の範囲でのみ言明しており、欠落0を主張する文言は含まれていない事を
当職自身で再確認した(§0-1 sed実測)。今後の報告でもこの区別を明記する。

## §3 解除条件⑷の分離（下命③・了解）

- ⑷a detector executable=★満★（commit`8184b23`・pytest.skip全廃・test_47a/b/c実走）
- ⑷b functional durability=★RED・未★（test_47b・audit log欠落の直接証拠・足軽1号への差戻し済と承知）
当職は検証laneに留まり、⑷bの実装(同transaction化またはoutbox化)には手を付けない
（下命④で明示された役割分担どおり）。

## §4 Ledger A/B 全件×判定形（下命②・列挙形から転換）

★母集団＝raw grep(file24→production10file、tests/migrations除外は理由つきで別掲)を
★statement単位★まで展開し、全29locationについて0/非0を問わず全行を判定する★。
（下命⑤の訂正=「6file/15箇所」を当職が独立に一からコード本文を読んで再現できるかを
本節で検証する形にした）。

### §4-1 全29 location 判定表

| # | file:line | 種別 | occupancy対象? | 委譲先 or 除外理由 | 判定 |
|---|---|---|---|---|---|
| 1 | appointment_detail.py:107 | UPDATE(unit_id/start_time/duration_minutes等可変) | Yes | なし | ★GAP★ |
| 2 | appointment_grid.py:527 | UPDATE(change_appointment_status内) | Yes | `appointment_lifecycle.deactivate_appointment`(同関数内L509,519) | 委譲済 |
| 3 | appointment_grid.py:535 | UPDATE(同上・別分岐) | Yes | 同上 | 委譲済 |
| 4 | appointment_grid.py:551 | UPDATE(同上・reactivate分岐) | Yes | `appointment_lifecycle.reactivate_appointment`(同関数内L542-543) | 委譲済 |
| 5 | appointment_grid.py:581 | UPDATE(同上) | Yes | 同上 | 委譲済 |
| 6 | appointment_grid.py:592 | UPDATE(同上) | Yes | 同上 | 委譲済 |
| 7 | appointment_grid.py:762 | UPDATE(move_appointment内) | Yes | `appointment_lifecycle.move_appointment_slot`(同関数内L784-785) | 委譲済 |
| 8 | booking_manage.py:279 | UPDATE(change_booking・start_time/end_time) | Yes | なし(独立実測=`appointment_lifecycle`/`booking_service`/`appointment_service`いずれも本関数から呼出し無し) | ★GAP★ |
| 9 | cancel_stats.py:105 | UPDATE(status='cancelled') | Yes | なし(独立実測=`get_appointment`のみimport・mutation委譲無し) | ★GAP★ |
| 10 | email_parser.py:109 | INSERT(新規作成) | Yes(create) | なし(独立実測=appointment_service/booking_service import無し) | ★GAP★ |
| 11 | next_appointment.py:71 | INSERT(新規作成) | Yes(create) | なし(独立実測=同上) | ★GAP★ |
| 12 | appointment_service.py:301 | INSERT(create_appointment) | Yes | `concurrency_root.claim_appointment_slots`(同関数内) | 委譲済 |
| 13 | appointment_service.py:463 | UPDATE(update_appointment) | Yes | `appointment_lifecycle.move_appointment_slot`(条件付・同関数内) | 委譲済 |
| 14 | appointment_service.py:516 | UPDATE(modification_count) | ★No★ | occupancy字段(clinic_id/unit_id/start_time/end_time/duration/status)に非ず | 除外(妥当) |
| 15 | appointment_service.py:671 | UPDATE(transition_status・else分岐=arrived/late/completed等) | ★No★ | active↔inactive遷移でない(activeのまま・occupancy不変)。同関数のno_show分岐(L664-668)のみdeactivate_appointmentへ委譲済 | 除外(妥当) |
| 16-25 | diagonal_service.py:117,146,175,179,261,276,317,333,337,375 | INSERT×2/UPDATE×8 | Yes | なし(独立実測=`appointment_service`からvalidation関数のみimport、mutation委譲無し) | ★GAP×10★ |
| 26 | prediction_service.py:299 | UPDATE(prediction_score/label) | ★No★ | occupancy不変・metadata-only(裁定の除外文言と一致) | 除外(妥当) |
| 27 | prediction_service.py:386 | UPDATE(同上) | ★No★ | 同上 | 除外(妥当) |
| 28 | booking_service.py:291 | INSERT(create_booking) | Yes | `concurrency_root.claim_appointment_slots`(同関数内L290) | 委譲済 |
| 29 | booking_service.py:409 | UPDATE(update_booking) | Yes | `appointment_lifecycle.move_appointment_slot`(条件付・同関数内L423-424) | 委譲済 |

### §4-2 集計（下命⑤の訂正値との突き合わせ）

- 委譲済=10 location（#2-7,12,13,28,29）
- 除外(妥当・非occupancy)=4 location（#14,15,26,27）
- ★GAP=15 location／6 file★（#1,8,9,10,11,16-25）

★家老second殿の訂正値「六件／15箇所」と、当職が一から各関数本体を読んで独立導出した
本表の集計が★完全一致★した。前便の「9 entrypoint」は関数単位の数え方であり、
本表のstatement単位(15箇所)とは述語が異なる（同じ現象を粗い/細かい単位で数えた差であり、
矛盾ではない事を明記する）。

### §4-3 GAPの内訳（6 file）

1. `appointment_detail.py:api_update_detail`（1箇所・詳細フィールド編集APIだがunit_id/start_time/
   duration_minutesも変更可能な設計）
2. `booking_manage.py:change_booking`（1箇所・SMS token経由の患者self-serviceリスケジュール。
   ★cancel_booking★は同ファイルにあるが`appointment_service.cancel_appointment`へ委譲済のため
   GAPではない事を当職確認済=前便の速報を訂正）
3. `cancel_stats.py:api_cancel_with_reason`（1箇所）
4. `email_parser.py:_create_appointment_from_parsed`（1箇所・メール自動取込経路）
5. `next_appointment.py:book_next_appointment`（1箇所・次回予約提案からの作成）
6. `diagonal_service.py`（10箇所・ななめ予約リンクの作成/更新/キャンセル/status伝播、
   4関数`create_diagonal_appointment`/`update_linked_appointment`/`cancel_linked_appointment`/
   `propagate_status`全てが対象）

## §5 criterion②（層外0件）への回答=★596c87e時点で未達・15箇所★

★母集団全件×判定形（下命②の様式）で示した通り、29location中15箇所(6file)が
共通domain層外に現存する。当職はこれを列挙するのみで裁定しない。実装(委譲)は
検証laneの範囲外であり、上位/a1の判断を仰ぐ★。

## §6 「126 PASS」への注意の当職での適用（下命⑤の一般化）

当職自身の報告でも同じ危険がある事を確認した: 前便§1でwriter回帰baseline「116 passed」を
報じたが、★この116件の母集団にdiagonal_service.py/email_parser.py/next_appointment.py/
booking_manage.py/cancel_stats.py/appointment_detail.pyの専用testが含まれているかは
当職は確認していない★。∴ 「116 passed」を上記6fileのGAPに対する回帰保証として使わない事を
ここに明記する（件数でなく個別testの母集団帰属を今後は名指しで書く）。

## §7 次のaction（順序厳守）

- a1のF2自己rollback修正(test_41 RED→GREEN対)を待つ。
- 併せて、上記6file/15箇所のGAPが最終的にどの範囲まで根治対象になるかは上位裁定待ち
  （当職は委譲の要否を裁定しない）。
- a1の修正完了後、9fe28d1基（本部長令）または最新断面で独立再走する。

## §8 禁則遵守

読取のみ・実装ファイル一字も変更せず。当職の木(`/tmp/resimg-verify4-cycle2-20260806`)内の
コード読解のみで、a1の作業ディレクトリは不触。push/PR/main/本番=一切なし。

★札★
```
$ date -Iseconds
2026-08-06T16:14:10+09:00
```

## §9 追記（提出直前・下命④の順序が満たされた）

本便執筆完了直前の再確認(§0の手順)で、a1が★F2自己rollback修正★を`55ba5a7`
「fix(reservation-cycle2): F2 self-rollback — move foreign_key_check before commit in
apply_booking_concurrency_root」として commit した事を検知した。
∴ ★下命④の順序（a1のF2修正が先→当職の独立再走が後）が本便提出の刻に満たされた★。
本便はLedger A/B(待つ間の手)としてそのまま提出し、F2修正前RED→修正後GREEN対の
独立再走は★別便（次便）★で行う（本便に混ぜず、報告の粒度を保つ）。
