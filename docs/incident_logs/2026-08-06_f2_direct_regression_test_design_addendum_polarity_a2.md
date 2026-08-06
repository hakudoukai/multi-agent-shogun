# 追補——f5c2cc9(F2直接回帰test設計)§6疑似コードの極性 誤り訂正 (足軽2号)

正本=`docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_direct_regression_test_design_a2.md`
(commit `f5c2cc9`・軍師second PASS 10:39:46)。★正本は書き換えぬ★——同便は既に軍師second
PASS済であり、書き換えればPASSの指す先が消える(当隊の条=「送信済・収め済の誤りは同id上書きで
直すな。新id/別fileで訂せ」)。本追補は★別fileとして★誤りを訂す。

出所=家老second msg_20260806_145235_ad5f2643 (2026-08-06T14:52:35)。当職が
`docs/incident_logs/2026-08-06_f2_red_crosscheck_a2.md`§2-1で見出した、
正本の地の文とpseudocodeの極性不整合について、家老second殿より「f5c2cc9は書き換えず追補で
訂せ」との裁を受け、本便を起草する。

## ㈠ 誤りの所在——§6疑似コードの極性が誤り。§4-4の地の文が正

正本§4点4(地の文)は「本testは★現行codeの欠陥を前提としたRED期待test★である」と書いた
——すなわち★現行(欠陥)codeの下でこのtestはRED(失敗)する★という意図であった。

しかし正本§6の疑似コード
(`test_fk_check_failure_leaves_schema_committed_not_rolled_back`)が実際に書いたassertは
以下の3件のみである:
```python
assert "_appointments_pre_root" not in tables      # rename後table消失=commit済の証
assert "appointment_slot_claims" in tables          # 新tableも作成済のまま=commit済の証
assert dangling == 1                                # 仕込んだ1件のみ・除去されていない
```
これらは★いずれも、現行(欠陥)codeの下で真になる値を確認するassert★である
(=「commit済のまま残っている」事を確認=欠陥がまさに起こっている状態の記録)。
∴ この3 assertは★現行codeの下でPASSする★——単体では★GREEN(documentary)★にしかならず、
★RED(失敗)を生まぬ★。

∴ ★§4-4の地の文(「RED期待test」)が意図(正)であり、§6のpseudocode(assertの極性)が
その意図を実現できていなかった(誤り)★。

## ㈡ 因——当職の便内の不整合(己の落度・他者に帰さず)

本件は足軽4号の実装の誤りではない。足軽4号は当職の設計(§2の仕込み手順・§3の担保構造)を
そのまま採用した上で、当職のpseudocodeには無い★新規のassert★
(`assert not root_tables_present(conn)`=「fk_check失敗時はroot tablesが存在してはならぬ」
というdesired contract)を自ら追加し、これによって実際にRED(`test_41`がFAILED)を
成立させた(足軽4号 commit `a694ae9e`、実測=`test_41_f2_fk_check_failure_leaves_schema_committed_red
FAILED`)。当職のassert群はそのまま`test_42`(documentary/GREEN)として別testに温存された。

∴ 因は★当職が正本執筆時、§4-4で「RED期待」と書きながら、§6でそのRED化に要る
「desired contract(あるべき姿)へのassert」を書き落とし、代わりに「現状(欠陥)の記録用assert」
のみを書いてしまった、当職自身の便内の不整合★である。同人へ帰す誤りではない。

## ㈢ 結論(F2がREDである事)は変わるか変わらぬか

★変わらぬ★。

正本の主張——「dangling FK仕込み(§2)によりF2の欠陥を確実に(deterministic に)REDとして
示せる」という★結論そのもの★は、足軽4号の実測(`test_41` FAILED、pytest実走)によって
★裏書きされ、覆っていない★。当職の仕込み手順(§2)・担保の構造分析(§3)は、いずれも
足軽4号によって独立に採用され、正しく機能した。

★誤っていたのは「結論」ではなく「結論を実現するための具体的手段(assertの極性)」のみ★
——すなわち、正本§6のpseudocodeを★そのままコピーして実装しても、単体ではRED化できず
GREEN(documentary)にしかならなかった★という点である。RED化には、当職が書かなかった
「desired contract(あるべき姿)へのassert」がもう1本必要だった。この不足分を足軽4号が
自ら補ったことで、結論(F2はREDとして示せる)は現物で成立した。

## ㈣ 三値(未解決のまま残す・本追補では埋めぬ)

- **UNMEASURED**: `test_41`のdesired contract(`not root_tables_present`)が、本部長裁定等の
  既存正本に基づく物か、足軽4号独自の判断かは、当職の
  `2026-08-06_f2_red_crosscheck_a2.md`§3点1で★UNMEASUREDのまま残しており、本追補でも
  同様にUNMEASUREDのまま残す★(下命=「そのまま残されたし」に従う。当職からは解決せぬ)。

---
断面: 2026-08-06T14:53:33+0900 (`date -Iseconds`実測)。
正本参照=`docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_direct_regression_test_design_a2.md`
(commit `f5c2cc9`・不変・書換なし)。
提出先: 家老second。
