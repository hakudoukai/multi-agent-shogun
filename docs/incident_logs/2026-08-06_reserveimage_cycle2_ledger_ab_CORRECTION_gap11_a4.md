# 足軽4号 → 家老second/軍師second: 台帳A/B 訂正便（GAP=15→11・母集団29→31）

★本便は訂正便に御座る。supersedes=
`docs/incident_logs/2026-08-06_reserveimage_cycle2_ledger_ab_full_population_verdict_a4.md`
（commit`79b13be`収載・sha256=`475f689bc770a1407124e6bfb9f2d5c0d927742dfaba34ab7f89bf0edb04a5d5`・
軍師second PASS済）。★同idの上書きは行わず新規便で訂正する（当隊の条）★。

下命=`msg_20260806_162018_c29f7bec`（16:20:18・「完全一致は一致にあらず」の指摘）。

## §0 誤りの認め（隠さず・咎めを求めず）

当職が前便で「家老second殿の訂正値と完全一致」と書いた15箇所は、★家老second殿が16:06便で
既に撤回していた誤りの数字★であり、当職はそれを知らず一から独立に読解して同じ15へ到達した。
∴ ★一致は「同じ誤り(occupancy字段で濾さず全write文を数えた)を同じ理由で犯した結果」であり、
独立性の証にならない★。ご指摘のとおり。

併せて、当職の母集団自体にも誤りがあった: raw grepを本日最初(8b95464/96aa31d断面)に一度だけ
実行し、以後596c87e/55ba5a7へ断面が進んでも★raw母集団を再取得していなかった★。
`backend/services/appointment_lifecycle.py`(commit`9fe28d1`で新設・共通command本体)には
`deactivate_appointment`(L83)/`reactivate_appointment`(L125)の2箇所でoccupancy(status)を
直接書く文があるが、当職の母集団はこの2箇所を一度も含んでいなかった(29 vs 31の差の正体)。

## §1 訂正実測（55ba5a7・当職独立再実行）

```
$ git show 55ba5a7:backend/services/diagonal_service.py | \
    /usr/bin/grep -nE "UPDATE appointments SET (linked_appointment_id|linked_appointment_id=NULL)"
175  UPDATE appointments SET linked_appointment_id = ?
179  UPDATE appointments SET linked_appointment_id = ?
333  UPDATE appointments SET linked_appointment_id=NULL, link_type=NULL, link_order=NULL
337  UPDATE appointments SET linked_appointment_id=NULL, link_type=NULL, link_order=NULL
```
上記4文が触れる列(`linked_appointment_id`/`link_type`/`link_order`)は本裁定のoccupancy字段
(`clinic_id`/`unit_id`/`start_time`/`end_time`/`duration`/`status`)の★いずれにも該当しない★。
∴ ★除外(非occupancy・裁定の除外文言に該当)へ移す★。

母集団再取得(10 production file + 新設`appointment_lifecycle.py`、大小文字問わず再実行):
```
$ grep -rniE "(insert into appointments|update appointments|delete from appointments)" \
    backend --include="*.py" | grep -v "/tests/" | grep -v -E "migrations/" | wc -l
31
```
内訳=appointment_detail(1)+appointment_grid(6)+booking_manage(1)+cancel_stats(1)+
email_parser(1)+next_appointment(1)+appointment_service(4)+diagonal_service(10)+
prediction_service(2)+booking_service(2)+★appointment_lifecycle(2・前便で欠落★)=31。

## §2 訂正後の全件×判定（29→31、階=SQL文単位を明記）

| 区分 | 件数 | 内訳 |
|---|---|---|
| 共通層(canonical command本体・delegate先そのもの) | 2 | `appointment_lifecycle.py`:L83(deactivate),L125(reactivate) |
| 委譲済(canonical commandを呼ぶ側) | 10 | 前便§4-1の#2-7,12,13,28,29(不変) |
| 除外(非occupancy・裁定の除外文言に明記一致) | 8 | 前便の4(modification_count/active間遷移/prediction×2)
  +★新規4(diagonal_service.py:175,179,333,337=linked_appointment_id系)★ |
| ★GAP(共通層外・occupancy対象)★ | ★11★ | appointment_detail.py(1)/booking_manage.py:change_booking(1)/
  cancel_stats.py(1)/email_parser.py(1)/next_appointment.py(1)/
  diagonal_service.py(6=117,146,261,276,317,375のみ・occupancy対象に限定) |

合計=2+10+8+11=31 ✓

## §3 GAP=★11箇所／6file★（訂正後・下命通り）

file数は不変(6file)。diagonal_service.pyの内訳のみ10→6に訂正(linked_appointment_id系4文を除外)。
他5fileのGAP内容(各1箇所)は不変。

## §4 階の明記（下命=A/Bに階を明記せよ、への対応）

- ★A表(前便§3-1で提示済)＝entrypoint(関数)の全件★。11 entrypointが4canonical commandへ委譲。
- ★B表(本便で訂正)＝SQL write文(statement)の全件★。31文中11文がGAP。
- 両者は階が異なり合算しない(前便から継続順守)。

## §5 booking_manage.cancel_booking の扱い（維持・賞のあった訂正点）

前便での訂正(cancel_bookingは`appointment_service.cancel_appointment`経由で委譲済・
change_bookingのみGAP)は本便でも維持する(独立に読み直し再確認・変更なし)。

## §6 worktree／sha

worktree path=`/tmp/resimg-verify4-cycle2-20260806`・測定対象sha=`55ba5a7cb510acadebacae3b294c90654ffcb3e0`
（診断・訂正作業のみ・当職の木のHEADは`badce84`から不変・コード変更なし）。

## §7 今後の適用

本便の値(GAP=11箇所/6file、母集団=31文)を正本とし、前便(79b13be)の15箇所/29文は
本便が優先する。軍師secondへ本便を訂正便として提出し、supersedes関係を明記の上PASSを乞う。
