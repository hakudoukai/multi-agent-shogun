# 全述語 再走（target fd945b3b・a1 final target・読取/静的検めのみ）足軽6号

下命=karo-second msg_20260807_055708_7fe6f447（current_order_12_20260807_024800_FULL_PREDICATE_RERUN 解凍版）。
★本工区は読取・静的検めに限る★の指示に従い、★pytestは走らせていない★（a4・a5・a6が同一木を共有する為の衝突回避。
direct testは既に軍師second監査済＝139 passed・14 file別・exit全0・queue/reports/gunshi_second_direct_test_gate_fd945b3b_reaudit_20260806.md）。

## 対象の木（読取専用・実測確認）

- `/tmp/resimg-cycle2-f123-clean-20260806`（a1木・GIT_NO_LAZY_FETCH=1下でHEAD=`fd945b3b7adcd25f076e45e0a165ad46c7847f53`・
  status --short=0行・porcelain 0を当職自身が実測、branch=`stage1/reservation-cycle2-f123-idempotency-a1-20260806`）。
  作業前後でHEAD・porcelain不動を確認。tmp_pack=0。
- 比較先＝当職前票の対象木 `ae1d2a9932ace06693a02b81e20a15284858826b`（過去断面、diffの相手方としてのみ使用）。

## ㈠ diff --stat（ae1d2a99 → fd945b3b、直読・実行なし）

```
backend/api/appointment_grid.py                    | 177 ++++++++----
backend/services/appointment_lifecycle.py          | 164 ++++++++++-
backend/services/appointment_service.py            |  77 ++++--
backend/services/diagonal_service.py               |  29 +-
backend/tests/test_appointment_grid_slot_sync.py   | 129 ++++++++-
backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py | 302 +++++++++++++++++++++
6 files changed, 790 insertions(+), 88 deletions(-)
```

当職の過去票（534独立再検証／B1B2到達可能性／五述語再走）が依拠した6fileのうち、
appointment_grid.py・appointment_lifecycle.py・appointment_service.py・diagonal_service.pyの4件が変更対象。
next_appointment.py・appointment_detail.pyはdiff --statに出ず——個別再diffでも確認（後述）、両fileとも空diff（無変化）。

## ㈡ detector再走（足軽4号原本、sha256=e13185b7e7e4a091a4399805dd562ce897dafeb031d03412b5debaa4dbf1bcff、
一字も変えず複製・再照合。own tree=/tmp/resimg-fd945b3b-5pred-a6-20260807、a1木からcp -r物理複製、
`diff -rq`で複製直後の完全一致を確認済。detector script自体は/tmp/resimg-verify4-cycle2-matrix2-20260807
（旧target 4a0e9036木、a4が未追跡ephemeral fileとして残していた場所）からsha256照合の上でcopy）。

```
[gate3-detector] scanned 458 files under backend
UNDELEGATED occupancy-relevant mutation sites: 1
  - backend/api/email_parser.py:108 [_create_appointment_from_parsed] INSERT
RESIDUAL raw SQL: 7
  - backend/api/appointment_detail.py:140 [api_update_detail] UPDATE
  - backend/api/appointment_grid.py:841 [move_appointment] UPDATE
  - backend/api/booking_manage.py:280 [change_booking] UPDATE
  - backend/routers/next_appointment.py:69 [book_next_appointment] INSERT
  - backend/services/diagonal_service.py:291 [update_linked_appointment] UPDATE
  - backend/services/diagonal_service.py:313 [update_linked_appointment] UPDATE
  - backend/services/web_reservation/booking_service.py:408 [update_booking] UPDATE
RESULT: RED (exit=1)
```

## ㈢ 判定（ae1d2a99断面との比較）

- ㈡未委譲=0か: **偽（1件、変わらず）**。email_parser.py:108、file・行・関数・列すべて過去2断面と一致（当該fileはdiff --statに
  現れず＝無変化を実測確認済）。
- ㈢residual=0か非occupancy根拠か: **偽（7件、件数は変わらず）**。うち6件は当該fileが無変化ゆえ内容も不変
  （booking_manage.py／web_reservation/booking_service.py／appointment_detail.py／next_appointment.py／
  diagonal_service.py×2＝これは2ファイル変更ありのfileだが、raw UPDATE自体は残存かつ順序入替えのみ、後述㈤参照）。
  appointment_grid.pyのresidual site（move_appointment関数、旧768→新841）は、旧target該当行と新target該当行の
  内容を当職自身がsed直読で突合し★byte-identical・行番号のみ+73シフト★（appointment_grid.py全体の
  +177/-…差分による行ずれ、change_appointment_status/reactivate周辺の増築が原因）である事を確認した。

## ㈣ 修正0（境界の遵守として記載、述語に非ず）

実装fix=0（本票作成の過程でコードは一字も改変せず）。detector script自体も一字も変えず複製。

## ㈤ diff内容の直読（変更4fileの中身、当職の過去発見との突合）

### appointment_grid.py — 534サイトが構造から消失

`change_appointment_status`のif/elif連鎖（旧534行＝`elif new_status:`枝、raw UPDATE直書き）は撤去され、
全枝が共通契約`appointment_lifecycle.transition_occupancy_status`呼出しへ一元化された。
コミットメッセージ・diff内コメント双方に「軍師second/足軽4号/5号/6号=独立4名実測」の文言があり、
当職の過去票（534独立再検証・target=4a0e9036）が引用元の一つに含まれている事が読み取れる。
cancelled/no_show/completedからの復元は新設の専用endpoint`PUT .../reactivate`のみへ分離され、
generic変更経路では`TerminalStatusTransitionError`→HTTP409となる（diff上で確認、動作は未実行）。
★534サイト自体はdetector出力に元々現れていなかった（detectorの静的分類上delegatedとして扱われていた事情、
当職前々票で既述）ため、detector上の変化としては現れず、diff直読でのみ確認できる★。

### appointment_lifecycle.py — 新設関数`transition_occupancy_status`＋`TerminalStatusTransitionError`

新設のdocstringに536行相当の設計理由が記載されている。`move_appointment_slot`のguard判定は
`status in (cancelled, no_show)`から`status in (cancelled, no_show, completed) or visit_status=='completed'`へ拡張
（visit_status='completed'かつstatus列不変のケースを追加補足、diff内コメントに「completed経路の見落とし対策」と明記）。

### appointment_service.py — 当職発見のsilent-swallowに直接対応

当職前票（5predicates_rerun_ae1d2a99_a6.md）で報告した「`update_linked_appointment`呼出しをbroad
`except Exception`で包み、guard拒否がHTTP200のまま握り潰される」点について、diff内コメントに
「★足軽6号 実測=own testにてHTTP200のままguard拒否がsilentに握り潰される事を確認★」との名指し引用がある。
変更内容: catch節を`except appointment_lifecycle.InactiveAppointmentSlotMoveError`（typed）へ限定し、
`logger.warning`に加えてresponse bodyへ`linked_update_warning`キー（linked_appointment_id/reason/linked_status）を
機械確認可能な形で追加。主request自体は引き続きHTTP200を維持する設計（家老second補足として「本部長殿⑤の裁定通り」と
diff内コメントに記載、当職はこの裁定文言自体を実見していない＝karo-secondの補足コメントとしてのみ確認）。
`transition_status`関数も同型で`TerminalStatusTransitionError`捕捉→409化を追加。

### diagonal_service.py — guard-before-write順への入替え

当職前票で「data-integrity上の実害は実測上生じていなかったが、明示的なrollback呼出しをsource上確認できておらず
経験的[empirical]な保証に留まる」と記した点について、diff内コメントに「★足軽6号実測=実害上は残らなかったが、
経験的[empirical]であり構造的[structural]な保証ではなかった★」との名指し引用がある。変更内容: raw UPDATE文を
`move_appointment_slot`呼出しの★後★から★前★へ入替え（diagonal_first/diagonal_second両枝）。これにより
guard拒否時はlinked側への書込み自体が発生しない事が呼び順自体から保証される設計に変わった（diff直読、動作未実行）。

### 3陽性対照（本部長殿指定・literal行番号）— 新targetでの再確認

| 対照 | 新target(fd945b3b)での内容 |
|---|---|
| appointment_grid.py:534 | 該当行の意味自体が消失（旧elif連鎖が撤去され、行番号534は新コード上で別の内容を指す。534という
  特定行を指した独立の意味は無くなったと見受くる、断定はせず） |
| diagonal_service.py:317 | 空行（第2枝raw UPDATEブロック直後、`conn.commit()`直前の空行）。当職過去2断面
  （4a0e9036/ae1d2a99）と同じく、指定line番号は当職が読んだ内容と一致せず |
| diagonal_service.py:375 | `cancel_linked_appointment`関数内、リンク解除UPDATE文（`update_linked_appointment`とは
  別関数）。過去2断面と同じく、指定line番号は当職が読んだ内容と一致せず |

★対照が外れておってもそのまま報告する（期待値へ寄せない）★。3対照中534以外の2件は、当職が測った3断面
（4a0e9036・ae1d2a99・fd945b3b）すべてでliteral line番号レベルでは成立していない。

### 新設test file（静的grepのみ・実行なし）

`backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py`（新設302行）内の`def test_`数を
grepで数えたところ4件——direct test gate票に記載の「新設file collected=4」と一致（静的カウントであり実行結果ではない）。
`test_appointment_grid_slot_sync.py`（既存fileへの追記129行）は`def test_`が7件。

## 未測・判らぬ点（一行ずつ、判定の語を混ぜず列挙）

- 上記diffの内容が実際にHTTPレベルで意図通り動くか（動的実測）は本工区の境界外（pytest禁）につき未確認——
  direct test gate票（軍師second PASS）が既存の唯一の動的証跡
- `transition_occupancy_status`の5分類（A/B/D/E＋C atomic reassign対象外）のうち、B（claim経路）が
  実際にreactivate_appointmentへ委譲する際のslot claim同一transaction性は、diff直読のみでは検証できず
  （動的実測が要る）
- diff内コメントに引用される「本部長殿02:52:39裁定」の原文（当職は未受領）が、当職の2つの発見（silent-swallow・
  guard-before-write）以外にどこまで言及しているか判らぬ

## 境界の遵守

- 実装fix=0・commit=0・push=0・merge=0・DDL=0・migration=0。入口patch=0。pytest実行=0（指示通り）。
- a1の木（2本、旧新とも）＝終始read only。作業前後で`git status --short`＋HEAD不動を実測確認。
  GIT_NO_LAZY_FETCH=1下で全git操作、tmp_pack=0。
- 自前複製（/tmp/resimg-fd945b3b-5pred-a6-20260807）内のみでdetector実行（detector本体はa4原本をsha256照合の上
  一字も変えず複製）。

## 数の扱い

測時=2026-08-07T06:0x〜06:2x+09:00（JST）。器=`git -C <path> diff/status/rev-parse/show`（GIT_NO_LAZY_FETCH=1）・
`cp -r`／`diff -rq`／`diff -u`／`sha256sum`／`sed`／`awk`／`grep -c`（detectorはpytest経由でなく単体script実行、
pytestそのものは不使用）。判定＝㈡=偽(1件・不変)、㈢=偽(7件・不変、うち534サイトはコード構造から消失し
detector出力自体には元々含まれず)、3陽性対照中534は行の意味自体が消失、残り2/3はline番号不一致（3断面一貫）。
以上（読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
