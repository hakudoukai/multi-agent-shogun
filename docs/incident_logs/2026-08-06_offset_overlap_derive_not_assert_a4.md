# 足軽4号 → 家老second/軍師second: offset overlap RED/GREEN「導出」化 完了報告

下命=17:17:10便（家老second・barrier票の独立機械突合結果 ㈠㈡㈢）②「検めを足すな。導出せよ」
（worker対をhelper一本に畳み、(db_path fixture, 期待値)を引数で受けよ／㈠-bの27/26も揃えよ、
揃えぬなら理由を票に書け）に応じた。指示どおり②を先に完了し、本便で報告する（⑤の⑶台帳4欄は次便）。

## §0 三sha+worktree欄

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 測定対象=当職独自実装（test fileのみの変更・productionコード不触）
- 修正前HEAD=`990e5ad4dfde5ad513e64767d051415dc44837bd`（家老second殿が機械突合した対象そのもの）
- 提出直前HEAD確認=`git rev-parse HEAD`実測=下記（★測定対象と一致しない=一致は求めていない、
  本便は990e5adへの修正であり新HEADが成果物★）

```
$ date -Iseconds
2026-08-06T17:22:37+09:00
$ git rev-parse HEAD
51f644f30aab22f67ef344fdff49209dc060e95c
```
機械path+sha:
```
97d1be8843b6e0f98c045019961d0fd6ea966dd1b97ce7e518c28757c98f0867  backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py
```
★注記=本worktreeはshallow clone（`git rev-parse --is-shallow-repository`=true）。
`git rev-list --count HEAD`=17は本体repoの646等とは母集団が異なる（shallow由来・断面が違う木を
比べての「数の相違」ではない）。混同を避ける為ここに明記する。

## §1 家老second殿の独立機械突合の3指摘への対応

家老second殿17:17:10便（RED=260-315行／GREEN=367-410行、fixture名正規化diff）の実測:
- ㈠-a worker本体（barrier位置・thread構成・connectの別）=差分零 → ★核心は立った★（対応不要）
- ㈠-b `_future(27,9)`(RED)対`_future(26,9)`(GREEN) → 対応済（下記）
- ㈠-c GREENのみ`_claims_count`assert二行 → 対応済（下記・揃えられない理由を明記）

## §2 変更内容（検めを足すのではなく導出へ）

新設helper`_run_offset_overlap_barrier(fixture_path, unit_id, start)`
（`backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py` 新規259-286行）に
RED/GREEN両testのworker_a/worker_b本体を一本化。両testは同helperを呼ぶのみとなり、
「worker本体が同一」は★申し立てでなく構造★になった（同じ関数を呼ぶ以上、乖離し得ない）。

- ㈠-b対応: 両testとも`start = _future(26, 9)`に統一。両fixture(`pre_root_db_path`/`db_path`)は
  `tmp_path`毎に独立DBの為、同日にしても衝突しない（実測=下記pytestで確認）。
- ㈠-c対応: GREEN側の`_claims_count`assertはpre_root側には★揃えられない★。理由=
  `pre_root_db_path`fixtureは`apply_booking_concurrency_root`自体を呼ばない為、
  `appointment_slot_claims` table自体が存在しない（同fixture docstring・実測で既報の事実）。
  ∴ `_claims_count`をこのfixtureへ呼べば例外になる — 揃えられない理由をtest docstringに
  明記した（家老second殿の下命「揃えぬなら理由を票に書け」に従い、本票にも転記する）。

```diff
$ git diff --stat 990e5ad HEAD -- backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py
 backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py | 86 ++++++++++------------
 1 file changed, 39 insertions(+), 47 deletions(-)
```
（純減8行=worker本体の重複2組がhelper1本に畳まれた分。旧407行→新399行）

## §3 GREEN（改修後・全5シナリオ再走）

```
$ pytest backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py -v -s
test_web_vs_web_barrier_true_concurrent_second_gets_409_or_integrity_error PASSED
test_web_vs_web_barrier_RED_exact_time_blocked_by_independent_guard PASSED
test_offset_overlap_barrier_RED_on_pre_root_schema
  F2BARRIER_OFFSET_RED_SUCCESS=2 F2BARRIER_OFFSET_RED_ACTIVE=2 → PASSED
test_web_vs_staff_barrier_true_concurrent_cross_entry_conflict PASSED
test_offset_overlap_barrier_true_concurrent_partial_conflict
  F2BARRIER_OFFSET_SUCCESS=1 F2BARRIER_OFFSET_CLAIMS=2 → PASSED
============================== 5 passed in 19.51s ==============================
```
改修前後でRED/GREENの成否・値は不変（success=2/active=2 対 success=1/claims=2）——
helper一本化は挙動を変えず、構造のみを変えた。

## §4 下命③（限界の明記・票に一行）

★限界として明記する★= exact-time Web-vs-Web（`test_web_vs_web_barrier_RED_exact_time_blocked_by_independent_guard`）
では、claim_appointment_slots単体の効きは測れない——appointmentsテーブル自体の部分UNIQUE index
（`uq_appointments_active_exact_start`）が独立に競合を止める二重guardの為、片方を無害化しても
RED化しない。∴「RED化できない」は「claim_appointment_slotsに欠陥が無い」の証にならず、
「別のguardが覆っている」事の記録として本testを固定してある（§4は裁定せず記録、が正）。

## §5 次（下命⑤の順）

②完了（本便）。次=⑤「⑶台帳4欄（site ID／reachable cases／委譲先／test）」へ進む
（16:55:06裁で単位が変わった台帳・断面を明記する — 足軽1号のdiagonal 5 site委譲(未commit)・
`cancel_stats.py`の生SQL母集団からの離脱(11→10 file)を含め、断面を秒で凍結して次便で作る）。

## §6 禁則遵守

新設helperを含め本改修はtest fileのみ（`backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py`）。
productionコード不触。push/PR/main/本番=一切なし。commitは`ashigaru4-verify-cycle2-20260806`
（scratch worktree）内のみ。queue/*の行数/sha引用なし。

★札★
```
$ date -Iseconds
2026-08-06T17:22:37+09:00
```
