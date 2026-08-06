# 足軽4号 → 家老second/軍師second: F2 修正前RED→修正後GREEN 対 独立確認（55ba5a7）

下命に明示された順序（本部長令＝a1のF2自己rollback修正が先→当職の独立再走が後）が
提出直前に満たされた事を検知し（前便§9参照）、直ちに再走した結果を報じる。

## §0 worktree path／測定対象sha／提出直前HEAD sha／一致or差分

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 測定対象sha=`55ba5a7cb510acadebacae3b294c90654ffcb3e0`
  （"fix(reservation-cycle2): F2 self-rollback — move foreign_key_check before commit
  in apply_booking_concurrency_root"）
- 提出直前HEAD確認=`2026-08-06T16:20:53+09:00`（`git log --all --author=ashigaru4-stage1`実測、
  55ba5a7より新しいcommitなし）
- 一致or差分=★一致★
- 当職の木のHEAD=`badce84`（sync commit `9ce2d29` + test更新commit `badce84`）

## §1 F2 RED→GREEN 対（下命の直接要求）

### §1-1 test_41（修正前RED→修正後GREEN・同一test・test名/assert文言を変更せず）

```
$ /tmp/resimg-stage1-runtime-venv/bin/python -m pytest \
    backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py::test_41_f2_fk_check_failure_leaves_schema_committed_red -v

【8b95464〜596c87e(修正前)】FAILED
  assert not root_tables_present(conn)
   +  where True = root_tables_present(...)   ← fk_check失敗後もroot tablesが存続=RED

【55ba5a7(修正後・本便)】PASSED
  同一assert文が今度は真になる(root_tables_present=False)=GREEN
```
★test本体もassert文言も一切変更していない（当職実測=`git diff HEAD~1 -- backend/tests/...`で
test_41関数の本体に変更なし、docstringのみ追記）。同一testが断面の違いだけでRED→GREENに
転じた事を当職が独立に確認した★。

### §1-2 test_42（旧="欠陥実在の記録"→新="修正の記録"・書き換え理由を明記）

旧test_42は「root_tables_present(conn)がTrueである事」を欠陥の証としてassertしていたため、
55ba5a7適用後は同じ実装に対しFAILEDへ転じた（欠陥が無くなった為、旧assertが逆に偽になる）。
∴ 当職はtest_42を「fk_check違反時は全ロールバックされ、root tablesが一切残らない事」を
確認するGREEN testへ書き換えた(`test_42_f2_fk_check_before_commit_full_rollback_green`)。
commit=`badce84`。

```
test_41 PASSED / test_42 PASSED（両者ともroot_tables_present関連assertが一致した結果）
```

## §2 F1/F3を含む全体再走（退行なきことの確認）

```
9 items: test_39 PASSED / test_40 FAILED(既知・下記) / test_45 FAILED(既知) / test_46 FAILED(既知) /
test_47a PASSED / test_47b FAILED(既知RED=㈤未解決・別途a1差戻し済) / test_47c PASSED /
test_41 PASSED(新規GREEN) / test_42 PASSED(新規GREEN) / test_43 PASSED / test_44 PASSED
4 failed, 7 passed
```
F1(test_40/45/46=当職test固有の陳腐化、先便から既知)・F3(test_43/44=GREEN継続)・
㈤(test_47b=RED継続、足軽1号への差戻し済と承知)は55ba5a7でも不変。
★F2のみが本便でRED→GREENに転じた新規事項である★。

## §3 writer回帰baseline（55ba5a7・退行なし）

```
$ pytest test_appointment_api.py test_appointment_service.py test_phase2_2_booking.py
    test_appointment_grid_slot_sync.py test_create_with_claim_cross_entry.py
    test_booking_concurrency_root_f2_self_rollback.py tests/test_booking_validator.py -q
121 passed, 2 warnings in 225.02s
```
a1自身のF2 self-rollback専用test(`test_booking_concurrency_root_f2_self_rollback.py`・2件)も
当職の木で実走しPASSED確認済（当職独立実測・a1の主張の丸写しでない）。

## §4 陽性対照3種（前便から継続・55ba5a7でも有効）

```
test_web_vs_web_true_two_connections_second_gets_409   PASSED
test_web_vs_staff_same_slot_cross_entry_conflict         PASSED
test_offset_overlap_partial_conflict                     PASSED
```
方法論の留保（真のthread-level並行ではなく2独立connectionの逐次呼出し＋app層check無害化）は
前便§2-1のまま不変。

## §5 現状の残課題（裁定せず・上位判断に委ねる）

1. ㈤(test_47b)=audit log欠落・RED継続。差戻し先=足軽1号（当職は検証laneのまま・実装せず）。
2. Ledger B層外gap=6file/15箇所（前便§4で確定済・55ba5a7でも変化なし=当職実測、
   `appointment_detail.py`/`booking_manage.py:change_booking`/`cancel_stats.py`/
   `email_parser.py`/`next_appointment.py`/`diagonal_service.py`は55ba5a7のdiffに含まれず不変）。

## §6 七項

⑴lane owner=足軽4号 ⑵worktree=`/tmp/resimg-verify4-cycle2-20260806`
⑶branch=`ashigaru4-verify-cycle2-20260806` ⑷修正前RED=test_41(8b95464〜596c87e)
⑸修正後GREEN=test_41+test_42(55ba5a7・本便で確認)
⑹commit=`badce84`(test更新)+`9ce2d29`(sync)
⑺blob sha256=
```
f7f6f2fc60001c44b2a206464e7de31ff39d8fb17879589f8c131a73e8deb545  backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py（484行）
```

## §7 禁則遵守

実装ファイル一字も変更せず（当職の木への`git show 55ba5a7:<path>`materializeのみ・
a1の作業ディレクトリ不触）。push/PR/main/本番=一切なし。
