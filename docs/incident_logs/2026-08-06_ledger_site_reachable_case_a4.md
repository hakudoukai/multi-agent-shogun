# 足軽4号 → 家老second/軍師second: 台帳(site×到達可能case・四欄) 新設 + 分母の増減理由 + 断面

下命=17:17:10便⑤/17:24:19便④(台帳4欄=site ID／reachable cases／委譲先／test)+
17:22:39便(分母の増減理由(一件ずつ)欄+断面(いつ・どの木)欄を追加)。
単位=本部長殿16:48:01逐語(★母集団の単位はruntime mutation site＋到達可能transition class★)。

## §0 断面（いつ・どの木・三sha欄）

★本便の執筆過程でa1(足軽1号)がlive commitした★——隠さず記す。

- 当職worktree=`/tmp/resimg-verify4-cycle2-20260806`・最終commit=`21f7a7692ddb06b1cc04fa642c86c68a746afb22`(不変・本便はcode変更なし)
- 独立検証専用worktree(新設・read-only)=`/tmp/resimg-verify4-a1-delegation-check-20260806`
  (`git worktree add --detach <path> 099288f`——a1のtracked fileを一切上書きせず、
  当職の別worktreeも上書きせず、独立detached checkoutとして検証)
- a1(lane=ashigaru1-stage1)worktree=`/tmp/resimg-cycle2-f123-clean-20260806`
  branch=`stage1/reservation-cycle2-f123-idempotency-a1-20260806`
- ★台帳の測定対象commit=`099288f410acb00791af29276da4d39f67da3fd5`★
  (「fix(reservation-cycle2): 層外writer8箇所→共通command委譲」・執筆中の17:29:49に
  a1がcommit・当職は17:30:03に検知)
- 提出直前確認=下記
```
$ date -Iseconds
2026-08-06T17:40:00+09:00
$ git rev-parse HEAD   # a1 worktree
099288f410acb00791af29276da4d39f67da3fd5
```
親commit(RED側測定対象)=`2fe4ed90b128eb3226f37465a7ef22c986ba0d79`
（099288fの直前commit・層外委譲前の断面）。

## §1 単位（本部長殿16:48:01逐語・要約せず該当部を引く）

> 母集団の単位はruntime mutation site＋到達可能transition class。各siteを一行の親IDとし、
> before/afterの正規化snapshotから次を子caseで網羅: A active→inactive=release、
> B inactive→active=claim、C active→activeかつclinic/unit/start/end/duration変更=atomic
> reassign、D active→activeで占有字段不変=no slot-op、E inactive→inactive=no slot-op。
> 完了述語はsite数0でなく「未委譲の到達可能case=0」。

## §2 台帳（9 site×四欄+分母の増減理由+断面）

★site ID=関数単位(前便までの「11箇所/6file」はSQL文単位・階が違う——本台帳はentrypoint
(関数)単位の9siteを親IDとする。前便final_verify_596c87e§3-3の「9 entrypoint」と同じ階)★

| site ID | reachable cases | 委譲先 | test | 分母の増減理由(099288f時点) |
|---|---|---|---|---|
| `booking_manage.py:change_booking` | C(offset時刻再割当・active→active) | ★`move_appointment_slot`★(099288f・旧UPDATE文は残置のまま併用) | `test_booking_manage_web_reschedule_resyncs_slot_claims`(当職独立確認=RED@2fe4ed9 FAIL／GREEN@099288f PASS) | 達成して縮んだ(委譲完了) |
| `cancel_stats.py:api_cancel_with_reason` | A(active→inactive・release) | ★`deactivate_appointment`★(099288f・旧UPDATE/INSERT文は完全に置換=grep母集団からも消滅) | `test_cancel_stats_cancel_with_reason_releases_slot_claims`(当職独立確認=RED FAIL／GREEN PASS) | 達成して縮んだ |
| `next_appointment.py:book_next_appointment` | B(inactive→active・claim) | ★`claim_appointment_slots`★(099288f) | `test_next_appointment_book_claims_slots`(当職独立確認=RED FAIL／GREEN PASS) | 達成して縮んだ |
| `diagonal_service.py:create_diagonal_appointment` | B×2(2レコード同時作成) | ★`create_appointment_with_claim`(auto_commit=False)×2+単一commit★(099288f・auto_commit契約新設) | `test_diagonal_create_claims_slots_for_both_records`(当職独立確認=RED FAIL／GREEN PASS) | 達成して縮んだ |
| `diagonal_service.py:update_linked_appointment` | C(diagonal_first/second 2分岐・いずれもactive→active occupancy再割当) | ★`move_appointment_slot`★(099288f・旧UPDATE文は残置のまま併用・当職実読=217-312行で確認) | `test_diagonal_update_linked_resyncs_slot_claims`(当職独立確認=RED FAIL／GREEN PASS) | 達成して縮んだ |
| `diagonal_service.py:cancel_linked_appointment` | A(release・cancel_both) | ★`deactivate_appointment`★(099288f) | `test_diagonal_cancel_both_releases_slot_claims`(当職独立確認=RED FAIL／GREEN PASS) | 達成して縮んだ |
| `diagonal_service.py:propagate_status` | ★A(no_show→inactive・linked_id側連動)=到達可能・GAP★／D(arrived・active→active・occupancy字段不変=no slot-op) | A=★なし(GAP継続)★／D=不要(occupancy不変ゆえ委譲対象外) | A=★UNMEASURED(陽性/陰性testとも未着手)★／D=当職実読で占有字段(unit_id/start_time等)を含まぬUPDATEである事を確認済(§本便§2-1に引用) | 変化なし(★本部長殿裁定待ち★=value依存(target_status)ゆえ機械的委譲不可・099288fのcommit本文でも明示的に対象外) |
| `email_parser.py:_create_appointment_from_parsed` | ★主張=B(create)だが実測=到達不能(reachable case=0)★ | 不要(到達不能ゆえ) | ★陰性test=当職独立実施(§2-1)★=INSERT列にunit_id欠落(appointments.unit_id=NOT NULL REFERENCES units)→恒常的IntegrityError→`except Exception: return None`で握り潰し。実測=`_create_appointment_from_parsed`戻り値=None・appointments行数=0のまま | ★第三種(達成でも隠れてでもない)★=到達不能と判明・occupancy-race母集団から除外が妥当。ただし★別種の欠陥(unit_id欠落バグ・機能不全)として台帳外で別途追跡要★(a1が099288f本文で「別途報告」と明記・当職も同意) |
| `appointment_detail.py:api_update_detail` | ★C(dynamic field-listにclinic/unit/start/end/durationのいずれかが含まれる場合)=到達可能・GAP★／D,E(metadata-onlyの場合=occupancy不変・委譲対象外) | C=★なし(GAP継続・設計票のみ・実装未着手)★ | C=★UNMEASURED(陽性/陰性testとも未着手)★ | 変化なし(a1が099288f本文で「設計票のみ作成し実装は次工区」と明記) |

### §2-1 独立検証の証跡（当職が実際に走らせた実測。a1の申告を名で信じず機械で確認）

★RED/GREEN対（099288f全体を対象・独立worktree`/tmp/resimg-verify4-a1-delegation-check-20260806`で実測）★
```
$ git worktree add --detach /tmp/resimg-verify4-a1-delegation-check-20260806 099288f
$ pytest backend/tests/test_layer_outside_writer_delegation_a1.py -v   # GREEN(099288f)
6 passed, 1 warning in 16.93s
$ git checkout 2fe4ed9 -- backend/api/booking_manage.py backend/api/cancel_stats.py \
    backend/routers/next_appointment.py backend/services/appointment_lifecycle.py \
    backend/services/diagonal_service.py   # production側のみ親commitへ戻す・testは099288f版で固定
$ pytest backend/tests/test_layer_outside_writer_delegation_a1.py -v   # RED(2fe4ed9相当)
6 failed, 1 warning in 16.02s
```
★同一harness(test file固定)でRED(6/6 FAIL)→GREEN(6/6 PASS)対を独立に再現。a1申告と一致★。

★email_parser.py陰性test（当職独自実施・当職worktree外の使い捨てscript）★
```python
result = _create_appointment_from_parsed(conn, 1, parsed)  # 正常な入力値
# 実測:
EMAIL_PARSER_CREATE_RESULT=None
EMAIL_PARSER_APPOINTMENTS_COUNT_AFTER=0
```
appointments.unit_id実測=`unit_id INTEGER NOT NULL REFERENCES units(unit_id)`
(`backend/db/migrations/appointment_tables.py`実測)。`_create_appointment_from_parsed`の
INSERT列一覧にunit_idが無い事を実読で確認(`backend/api/email_parser.py:109-122`)。
∴ ★「到達不能」は主張でなく証(陰性test)で残した★(下命③の実装形)。

## §3 完了述語の現況＝★未達・具体的に2件★

★完了述語=site数0でなく「未委譲の到達可能case=0」(本部長殿裁定)★。
099288f時点で★未委譲の到達可能case=2件★:
1. `diagonal_service.py:propagate_status` の case A(no_show→inactive連動) — 本部長殿裁定待ち(value依存ゆえ機械的委譲不可、099288f本文で対象外と明記)
2. `appointment_detail.py:api_update_detail` の case C(occupancy字段を含むdynamic UPDATE) — 実装未着手(設計票のみ)

★email_parserは到達不能ゆえ2件に含めない(§2の第三種)★。

## §4 分母の増減理由（一件ずつ・下命どおり）

★母集団は断面と共に動く★——099288f時点の内訳を一件ずつ記す(達成/隠れ/第三種を区別):
- 達成して縮んだ(委譲完了)=6件: change_booking / api_cancel_with_reason / book_next_appointment /
  create_diagonal_appointment / update_linked_appointment(C) / cancel_linked_appointment(A)
- 変化なし(GAP継続・到達可能)=2件: propagate_status(case A) / api_update_detail(case C)
- 第三種(到達不能と判明・occupancy-race母集団から除外・ただし別種の欠陥として別途追跡)=1件: email_parser
- ★隠れて縮んだ(=population定義の見落としによる不当な減少)は0件と当職は判定した★
  (§2-1で全9siteを実読・実測し、除外理由を個別に明記した為。ただし当職の実読は099288f
  一断面の実測であり、次断面(a1の追加commit等)で再確認を要する)

## §5 次

台帳(⑶)は本便で四欄+分母の増減理由+断面を満たした。次=下命の順どおり本務(barrier陽性対照)
は既に完了済(前2便)——残るは①propagate_status(case A)と②api_update_detail(case C)の
GAP解消(実装lane=a1の管掌・当職は検証laneゆえ実装せず、進捗の追跡のみ継続)。

## §6 禁則遵守

当職は本便作成のため以下のみ実施: (1)a1のtracked file読取(read-only)、(2)新規detached
worktree作成(`git worktree add --detach`・既存fileを一切上書きせず)、(3)同worktree内で
`git checkout <sha> -- <path>`によるproduction側のみの一時切替(RED測定用・a1の本worktreeは
不触)、(4)使い捨てpythonスクリプトでの陰性test(scratchpad上・repo外)。
a1の実装ファイル・a1のworktreeは一切書き換えていない。push/PR/main/本番=一切なし。
