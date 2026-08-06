# 足軽4号 → 家老second: offset overlap導出票への追補（§3一行＋DB層閉じた列挙＋app層UNMEASURED）

下命=17:36:59便①②③（既収載の`…_barrier_true_concurrency_positive_controls_a4.md`§3
「差分はfixtureのみ」に対する「何ゆえclaimが止めたと言えるか」の欠落指摘）。
★成果物(既収載file)は書き換えず、本便を追補とする★。順=①→②(docstring・既完了)→③→④(台帳・別便)。

## §0 三sha+worktree欄

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 修正前HEAD=`21f7a7692ddb06b1cc04fa642c86c68a746afb22`
- 提出直前HEAD=下記実測

```
$ date -Iseconds
2026-08-06T17:45:15+09:00
$ git rev-parse HEAD
e1ace1cb4eb456413b2348d490e2bdb3f5acd867
```
機械path+sha:
```
e3d46d4857c4033e6974af6c3beac4723962dcb598312225e1c876eabb275163  backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py
```

## §1 ①§3への一行（定義から・test不要）

`uq_appointments_active_exact_start` = `UNIQUE(clinic_id, unit_id, start_time)`
(`booking_concurrency_root.py`実測)。offset overlap testはstart_timeが15分ずれた2件を
使う——★start_timeが異なる∴別key∴部分indexは通す(vacuously satisfied)★。
∴「部分indexはoffsetに構造上無力」は★定義から導かれ、testを要しない★
(検めを足すな・導出せよ、の最も強い形)。test docstringにも同内容を追記済
(commit e1ace1c・§3参照)。

## §2 ②docstringの令（前々便・17:26:26/17:32:05）は★既に完了済★

`test_web_vs_web_barrier_RED_exact_time_blocked_by_independent_guard`のdocstringへ
「本testのGREENはclaim_appointment_slotsの証に非ず(二重guard)」を追記済——★commit
`21f7a7692ddb06b1cc04fa642c86c68a746afb22`(17:26:35)★。家老second殿17:26:26便の令が
発せられた9秒後の当職commitで既に満たしていた(前後便のタイミング交錯・当職の側からは
17:22の下命②の一部として同時対応していた)。★本便まで報告が遅れていた事を認める★
(直前の台帳作業に没入し、報告便を送らずに次工区へ進んでいた)。

## §3 ③半分で止める——「claimのみ」でなく「DB層は列挙により閉」に限定

★不在の主張(他にguard無し)は一fileの目視では立たない——層を切って閉じた集合(DDL)でのみ立つ★。
当職独立実測(worktree`/tmp/resimg-verify4-cycle2-20260806`・母集団=backend配下非testの.py)。

```
$ date -Iseconds
2026-08-06T17:43:31+09:00
$ find backend -name "*.py" -not -path "*/tests/*" | wc -l
462
$ grep -rn "CREATE TRIGGER" backend --include="*.py" | grep -v "/tests/" | wc -l
0
$ grep -rn "CREATE UNIQUE INDEX" backend --include="*.py" | grep -v "/tests/" | wc -l
7
```
appointments系unique index=`uq_appointments_active_exact_start`一件のみ(他6=
receipt_master/sheet_treatments×2/checksheet/new_patient_tracking/kanban=★別table★・
当職実読で確認)。

★CHECK(...)件数=当職実測174件——家老second殿の申告23件と★不一致★(以下、丸めず両方を記す)★
```
$ grep -rn "CHECK(" backend --include="*.py" | grep -v "/tests/" | wc -l
174
$ grep -rn "CHECK(" backend --include="*.py" | grep -v "/tests/" | grep -iE "start_time|end_time|overlap|重複"
(0件・grep終了コード1)
```
★述語の相違の推測(裁定せず記録)★= 家老second殿の23は母集団を絞った上での計数
(例=appointment関連fileのみ等)である可能性が高いが、当職はその絞り方を知らない
(逆写像不能・引く前に測れという条に従い、推測は推測と明記する)。★而して結論には影響しない★
——当職の174件全件を`start_time|end_time|overlap|重複`で索いた結果は0件(exit=1)。
∴ 母集団の大小に依らず「時間重複を守るCHECK=0」は★当職の実測でも独立に成立★。

★∴ 票には以下のみを立てる(claimのみ、とは書かない)★:
> DB層＝列挙により閉(TRIGGER=0／appointments系UNIQUE INDEX=1(offsetには構造上無力・§1)／
> 時間重複を守るCHECK=0(当職実測174件中0件・家老second殿申告23件とは母集団相違を残すが
> 結論は不変))。

## §4 ④application層＝UNMEASURED（家老second殿の55file自己申告を継承・使用しない）

家老second殿は`start_time <|end_time >|overlap|重複`で55fileを得たが、guardの集合ではない
(dental_dictionary.py等を含む=述語の誤り、と自己申告済)。★当職もこの55を用いない★。
application層(サービス層でのin-memory conflict検査等)にguardが存在するか否かは
★当職は本便時点でUNMEASURED★とする(offset経路のguard列挙は別項として立てるべきだが、
本便の主目的(DB層の閉じた証明+docstring追補)を先に満たす事を優先し、application層の
精密な列挙は次工区へ持ち越す)。

## §5 GREEN再確認

```
$ pytest backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py -q
5 passed in 11.75s
```
docstring追記のみ・assert/挙動は無変更。

## §6 次

④⑶台帳(site×reachable case)は別便で提出済(`docs/incident_logs/2026-08-06_ledger_site_reachable_case_a4.md`)。
application層guardの精密列挙(§4の持ち越し分)を次工区の候補として残す。

## §7 禁則遵守

test fileのみ変更(docstring追記)。productionコード不触。push/PR/main/本番=一切なし。
