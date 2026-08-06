# 足軽4号 → 家老second/軍師second: 台帳(site×reachable case)訂正1（propagate_status裁定不要確定・email_parser行を母集団維持のまま欄値訂正）

下命=17:52:36便①②（台帳二件訂正）。★対象file(`2026-08-06_ledger_site_reachable_case_a4.md`)は
書き換えず、本便を訂正1として追補する（消すな・重ねよ、の条に従う）★。

## §0 三sha+worktree欄

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 直前HEAD(陰性test commit後)=`e88e758`
- 提出直前確認=下記実測

```
$ date -Iseconds
2026-08-06T18:01:08+09:00
$ git rev-parse HEAD
e88e7582fa2c8d83e4617cec962a5724df8ad695
```

## §1 訂正其の一: `diagonal_service.py:propagate_status` case A ＝★裁定待ちではなく確定済★

★原文(2026-08-06_ledger_site_reachable_case_a4.md §2表・propagate_status行「分母の増減理由」欄)★:
> 変化なし(★本部長殿裁定待ち★=value依存(target_status)ゆえ機械的委譲不可・099288fのcommit本文でも明示的に対象外)

★訂正後★:
> 変化なし(★裁定不要・述語(ACTIVE_SQL)が既に定める★=未委譲の到達可能case(class A)・
> 実装未着手のためGAP継続。⑶の分子に算入)

★根拠(当職独立実読・家老second殿の実測を根にせず)★:
```
$ grep -n "ACTIVE_SQL" backend/db/migrations/booking_concurrency_root.py
16:ACTIVE_SQL = "status NOT IN ('cancelled','no_show')"
```
`diagonal_service.py:propagate_status`(344-384行実読)は`target_status in ("arrived","no_show")`で
linked appointmentのstatusを直接UPDATEする。`no_show`は`ACTIVE_SQL`により非active側 ∴
active→no_show=release=★class A(述語から確定・裁定不要)★。`arrived`はactive側のまま
∴ active→active・occupancy字段不変=class D(委譲対象外、当職前便§2-1で確認済・変更なし)。

★∴ §3「完了述語の現況」の該当行も同様に訂正する★:
- 原文: 「1. `diagonal_service.py:propagate_status` の case A(no_show→inactive連動) —
  本部長殿裁定待ち(value依存ゆえ機械的委譲不可、099288f本文で対象外と明記)」
- 訂正後: 「1. `diagonal_service.py:propagate_status` の case A(no_show→inactive連動) —
  ★述語(ACTIVE_SQL)から確定済・裁定不要★。実装未着手ゆえGAP継続(099288f本文でも
  target_status依存ゆえ機械的委譲は対象外と明記されているが、これは「実装が機械的にできない」
  であり「裁定が必要」ではない——両者は別の主張である)」

★§4「分母の増減理由」の該当箇所も同様に訂正★:
- 原文: 「変化なし(GAP継続・到達可能)=2件: propagate_status(case A) / api_update_detail(case C)」
  の`propagate_status(case A)`部分に添えられた説明を上記の訂正後文言に統一する。
  ★件数(2件)自体は不変★——本訂正は理由の言い換えであり、母集団の増減ではない。

## §2 訂正其の二: `email_parser.py` 行 ＝★母集団9のまま維持・欄値を訂正★

★原文台帳は元より母集団9件のまま(email_parser行を削除してはいない)——ただし「分母の増減理由」欄
(§4)で「occupancy-race母集団から除外」と書いた語が、除外を示唆する誤解を招く表現だった★。
下命に従い、欄の値を下記へ訂正する(母集団9は不変)。

★原文(§2表・email_parser行「分母の増減理由」欄)★:
> 第三種(達成でも隠れてでもない)=到達不能と判明・occupancy-race母集団から除外が妥当。
> ただし別種の欠陥(unit_id欠落バグ・機能不全)として台帳外で別途追跡要(a1が099288f本文で
> 「別途報告」と明記・当職も同意)

★訂正後(下命の指定書式どおり)★:
> 到達不能（第三種）／因＝unit_id NOT NULL 違反で恒常IntegrityError／委譲＝不可／
> 出処＝a1 17:40・当職陰性test独立確認(commit`e88e758`・2026-08-06T18:00:09+09:00・
> `backend/tests/test_email_parser_unreachable_unit_id_a4.py`にて固定)

★§2表「reachable cases」欄・「test」欄は変更なし(既に第三種/陰性test方針を記載済)——
「test」欄の「§2-1で実施」の記述に★commit sha`e88e758`を追記★する:
> ★陰性test=当職独立実施(§2-1) → ★commit`e88e758`(test_email_parser_unreachable_unit_id_a4.py)
> でcommitへ固定済(2026-08-06T18:00:09+09:00・家老second令17:52:36便②に対応)★

★§4「分母の増減理由」の該当行も同様に訂正★:
- 原文: 「第三種(到達不能と判明・occupancy-race母集団から除外・ただし別種の欠陥として
  別途追跡)=1件: email_parser」
- 訂正後: 「第三種(到達不能と判明・★母集団9件から除外はしない、行は残す★)=1件: email_parser
  ／因=unit_id NOT NULL違反・恒常的IntegrityError／委譲=不可／陰性testをcommit`e88e758`で固定
  (実測のみで終わらせず、直った日に気付けるようにする)」

## §3 母集団の確認（訂正後も9のまま・変わらず）

訂正1・2いずれも「分母の増減理由」欄の★言い換え★であり、母集団(9 site)・
未委譲到達可能case数(2件: propagate_status/api_update_detail)・第三種数(1件: email_parser)
の★数字はどれも変わらない★。変わったのは「裁定待ち」という誤った分類と、「除外」という
誤解を招く表現の二点のみ。

## §4 順序確認（下命⑥）

㈠台帳二件訂正=本便で完了。㈡陰性testをcommit=完了済(commit`e88e758`、backend/tests/
test_email_parser_unreachable_unit_id_a4.py、1 passed in 3.74s)。㈢guard列挙節(前便の三行形)=
完了済(`2026-08-06_offset_overlap_derive_not_assert_a4_addendum2.md`)。㈣提出=本便をもって
軍師secondへ提出する(下記§5渡した刻)。

## §5 禁則遵守・渡した刻

test fileのみ変更(commit`e88e758`・productionコード不触)。docs/incident_logs配下の記録の訂正・
追補のみ。push/PR/main/本番=一切なし。

★軍師secondへ提出=下記実測★
```
$ date -Iseconds
2026-08-06T18:01:17+09:00
```
