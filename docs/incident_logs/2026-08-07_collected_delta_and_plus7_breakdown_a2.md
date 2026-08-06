# 第四値㈠㈡ 閉鎖試行票 — 足軽2号

令元: `queue/tasks/ashigaru2.yaml` current_order_20_20260807_045200_CLOSE_FOURTH_VALUES
測時 (本票確定): 2026-08-07T05:01:35+09:00 (date -Iseconds実値)
境界順守: `--collect-only` は base木のみ・一度 (実行済・以後の追加実行 0)／full run 0 (新規に実行せず、既存の
2026-08-07_base_contrast_run_ae1d2a99_a2.md 掲載の実測値のみを引用)／patch 適用 0 (読むのみ)／a1木不触
(`/tmp/resimg-cycle2-f123-clean-*` へ一切接触せず)／fix 0・commit 0・push 0・merge 0・DDL 0／patch改変 0／
`.gitignore` 不触／remote通信 0 (`GIT_NO_LAZY_FETCH=1` 維持)／`git config --set` 0。

各行冒頭に **実測** / **推論** を明記する。線引きの無い行は無い。

---

## ㈡ +7 passed (base 3136 → target 3143) の内訳個別特定

### ⑴ base木 collect-only (一度・本票の為に新規実行)

**実測** command (逐語・cwd込み):
```
export GIT_NO_LAZY_FETCH=1
cd /tmp/resimg-verify2-base-contrast-ae1d2a99-20260807
python3 -m pytest backend/tests -q --collect-only \
  --ignore=backend/tests/test_migration_036_recurrence_guard_probe.py \
  --ignore=backend/tests/test_watchdog_hook.py \
  2>&1 | tee /tmp/ashigaru2_base_collectonly_ae1d2a99_20260807.log
```
(既存の base対照票 `2026-08-07_base_contrast_run_ae1d2a99_a2.md` の full-run commandと、`--collect-only`追加以外は
一字違えず・同一 `--ignore` 集合)

**実測** 結果: `3269 tests collected in 3.51s`
**実測** 実行前後: HEAD = `ae1d2a9932ace06693a02b81e20a15284858826b` 不変・`git status --porcelain` = 0行 (前後とも)。

**実測** 器:
```
path   = /tmp/ashigaru2_base_collectonly_ae1d2a99_20260807.log
行数   = 3295
sha256 = b984f0e4c60eae7e8e0692dabb2000c246983615becfc3592ef0ce70087601f8
```
**実測** `::` を含む行 (＝test id 行) を抽出:
```
path    = /tmp/a2_base_collectonly_ids.txt
行数    = 3269
sort -u 後の行数 = 3269 (重複 0)
sha256  = 13eeb815e71d8c1e713a3b359c0e781275560014a4a1678fa4157d9e5d362f0c
```
**推論**: 本務着手前 (令元・前工区 `2026-08-07_base_contrast_run_ae1d2a99_a2.md` §「参考」) に別session で測られた
「3269 tests collected (8.43s)」と、本票で改めて測り直した「3269 tests collected (3.51s)」が完全一致。
測時が違う二度の独立測定が同数ゆえ、base木のcollect-only件数=3269は再現性が在る値と見てよい。

### ⑵ patch (1,138行・sha256 62107ad2c1ea2951e1d5c3224c9f6eccd25a71bb609917c7732f6af4171fc21) を読んで
   test 函数名を列挙 (patchを当てず・読むのみ)

**実測**: patch内で test file を含む diff は 2 件のみ (他 4 diff は `backend/api/appointment_grid.py` /
`backend/services/appointment_lifecycle.py` / `backend/services/appointment_service.py` /
`backend/services/diagonal_service.py` の実装ファイルであり、`^\+def test_` を機械 grep した結果 **0件** — 実装側に
新規 test 関数は追加されて居らぬ)。

**実測** 既存 test file `backend/tests/test_appointment_grid_slot_sync.py` (index f0150aa..f689777・new file mode 表記
無し＝既存ファイルの改変) の diff hunk 内:

| 種別 | patch行 (逐語行番号) | 函数名 |
|---|---|---|
| 削除 (`-def`) | 685 | `test_change_status_restore_from_cancelled_reclaims_slot` |
| 追加 (`+def`) | 688 | `test_change_status_generic_endpoint_rejects_restore_from_cancelled` |
| 追加 (`+def`) | 726 | `test_reactivate_endpoint_restores_and_reclaims_slot` |
| 追加 (`+def`) | 760 | `test_reactivate_endpoint_rejects_non_terminal_appointment` |
| 追加 (`+def`) | 779 | `test_change_status_booked_from_cancelled_rejected_with_no_phantom_claim` |

**実測**: 削除された函数名と最初に追加された函数名は、diff hunk 内で隣接 (685行→688行) しており、docstring 内に
「旧 `test_change_status_restore_from_cancelled_reclaims_slot`…を置換する」と明記されている (patch 692-698行)。
形は rename ではなく「1関数削除+1関数追加(別名)+2関数純増」。

**実測** 新設 test file `backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py`
(`new file mode 100644`・全302行が新規追加) の diff hunk 内、`^\+def test_` 該当行:

| patch行 (逐語行番号) | 函数名 |
|---|---|
| 953 | `test_move_appointment_slot_rejects_visit_status_completed_even_if_status_column_unchanged` |
| 996 | `test_move_appointment_slot_still_allows_non_completed_visit_status` |
| 1024 | `test_grid_status_done_target_blocks_subsequent_move` |
| 1088 | `test_update_appointment_reports_structured_warning_when_linked_is_inactive` |

**実測**: 同 file 内の他の `+def` 6件 (`_future` / `concurrency_db` / `_get_unit_ids` / `_insert_appointment` /
`_slot_claims` / `_create_diagonal`) は `test_` 接頭辞を持たぬヘルパー/フィクスチャであり、母集団 (test函数) に含めず。
`+class` 行は本 file 内 0件 (クラスベース test 0)。

**実測** 集計: 追加 test 函数 = **8件** (旧ファイル4＋新ファイル4)。削除 test 函数 = **1件** (旧ファイルのみ)。

### ⑶ ⑵の各IDが⑴のbase collect-only listに不在である事を機械確認

**実測** command: `grep -Fxq -- "<id>" /tmp/a2_base_collectonly_ids_sorted.txt` を追加8件・削除1件それぞれに実行。

追加8件の full test id (module::func) を base collect-only list に照合した結果 (**実測**・全件 ABSENT を確認):
```
ABSENT_FROM_BASE: backend/tests/test_appointment_grid_slot_sync.py::test_change_status_generic_endpoint_rejects_restore_from_cancelled
ABSENT_FROM_BASE: backend/tests/test_appointment_grid_slot_sync.py::test_reactivate_endpoint_restores_and_reclaims_slot
ABSENT_FROM_BASE: backend/tests/test_appointment_grid_slot_sync.py::test_reactivate_endpoint_rejects_non_terminal_appointment
ABSENT_FROM_BASE: backend/tests/test_appointment_grid_slot_sync.py::test_change_status_booked_from_cancelled_rejected_with_no_phantom_claim
ABSENT_FROM_BASE: backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py::test_move_appointment_slot_rejects_visit_status_completed_even_if_status_column_unchanged
ABSENT_FROM_BASE: backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py::test_move_appointment_slot_still_allows_non_completed_visit_status
ABSENT_FROM_BASE: backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py::test_grid_status_done_target_blocks_subsequent_move
ABSENT_FROM_BASE: backend/tests/test_visit_status_completed_guard_and_diagonal_warning_a1.py::test_update_appointment_reports_structured_warning_when_linked_is_inactive
```
⇒ **8件全て base collect-only listに不在** ＝ 新規test候補集合として確定 (⑵の追加分と1:1対応)。

削除1件を同 base collect-only list に照合した結果 (**実測**):
```
PRESENT_IN_BASE: backend/tests/test_appointment_grid_slot_sync.py::test_change_status_restore_from_cancelled_reclaims_slot
```
⇒ **base collect-only listに存在** (patch適用前=base木の時点では現に collect される test であった事の機械確認)。

### ⑷ 候補の数と+7が合うか

**実測** 算術: 追加候補8件 − 削除1件 = **7**。
**実測**: 既存票 (`2026-08-07_base_contrast_run_ae1d2a99_a2.md` §「新述語」) の
target導出collection総数3277 − base導出collection総数3270 = **7** と、**完全一致**。

**推論**: 上記は「collection総数の差7」を説明するが、本工区の眼目である「**passed** の差+7 (3136→3143)」を
説明するには、追加8件が target run で悉く passed 側に属し、かつ削除1件が base run で passed 側に属していた事
(＝いずれも failed/error/skipped/xfailed のいずれでも無かった事) が要る。この点は本票の手番 (base木の
collect-only・patchの読取) だけでは直接測れぬ (target側の個別test結果はa1木に属し不触・かつ本工区の境界は
`--collect-only`のみで full run 0)。

**推論** (整合性確認・target実行の直接再測はせず、既存票の集計値からの論理的逆算に留める):
既存票 (`2026-08-07_base_contrast_run_ae1d2a99_a2.md` §⑺) は base/target 間で FAILED+ERROR の id 集合が
**完全一致** (新規F/E=0・解消F/E=0・共通107) である事を機械確認済み。これは「削除1件・追加8件のいずれも
base側/target側それぞれの F/E 集合の中身に含まれて居らぬ」事を意味する (含まれておれば comm -23/-13 が
非0になる)。同票はまた skipped (23=23)・xfailed (4=4) が base/target で**件数**一致である事も示す (但し
id集合までの一致は同票では未検証・本票でも新たに測ってはおらぬ)。

この3点 (F/E集合完全一致・skip件数一致・xfailed件数一致) と、削除1件+追加8件=正味+7という**collection総数**の
一致を組み合わせると、算術上 **唯一** 整合するのは「削除された旧test=base側でpassed・追加された8件=target側で
悉くpassed」の割当てであり (base_passed 3136 − 削除1 + 追加8 = 3143 と正確に一致)、他の割当て
(例=追加8件の一部がskip/xfail側に落ちる等) は skip/xfailed件数の一致 (23=23・4=4) と矛盾する。
∴ **推論として** ㈡の内訳は「削除1件(旧`test_change_status_restore_from_cancelled_reclaims_slot`、base側passed)
＋追加8件(target側で全件passed)＝net+7」で閉じる、と述語のみ言える。
**但し**この「全件passed」は target木のtest実行結果そのものを本票の手番で直接実測した物ではなく、
base/target集計値の算術的整合性からの逆算 (他に矛盾なく説明できる割当てが無い、という消去法) である事を明記する。

**判定**: ㈡は **候補集合の機械確認 (実測) は完了・件数照合 (8−1=7) は実測で+7と一致・内訳の個別特定は
推論で唯一整合する割当てを示せたが target側の直接実行確認は本工区の境界外ゆえ未実施**。

---

## ㈠ collect-only 3269 と実走導出 3270 の差1の因

**実測**: base木 collect-only (本票⑴、新規測定) = **3269**。
**実測**: 既存票 (`2026-08-07_base_contrast_run_ae1d2a99_a2.md`) の base full-run summary逐語
「`102 failed, 3136 passed, 23 skipped, 4 xfailed, 3 warnings, 5 errors in 1161.20s`」からの導出
= 102+3136+23+4+5 = **3270** (己の手で算術し直し・一致)。
**実測**: 差 = 3270 − 3269 = **1**。

### 検めた仮説 (悉く実測・棄却)

1. **実測**: pytest plugin (pytest-rerunfailures / pytest-xdist 等、再実行や並列で1itemが複数outcomeを生む物)
   の有無 → `pip list | grep -i pytest` = `pytest 9.0.3` のみ。該当plugin **不在**。
2. **実測**: `pytest.ini` / `pyproject.toml` / `setup.cfg` / `tox.ini` を base木全体で検索 → **0件**
   (`addopts` 等での doctest収集・xfail_strict等の隠れ設定は **存在せず**)。
3. **実測**: xpassed (xfailで印を付けたが実際にはpassした場合の別カテゴリ) → 既存summary行に
   `xpassed` の記載 **無し** (pytestは非0のカテゴリのみ表示する仕様ゆえ、記載無し=0件と読める)。
4. **実測**: base木の `backend/tests` 配下 `.py` file数 (conftest除く) = 210件 (disk実測) と、
   `git ls-tree -r HEAD -- backend/tests` の追跡ファイル数 = 210件 (git実測) が **完全一致**。
   `git status --porcelain --ignored=matching` では `__pycache__` 3ディレクトリのみが ignored対象で、
   新規/野良の `.py` test file は **0件**。
5. **実測**: 既存 full-run log (`/tmp/ashigaru2_base_contrast_ae1d2a99_pytest_20260807.log`、本票の為に
   新規実行はせず既存artifactを読むのみ) 内を `PytestCollectionWarning` / `collected` / `duplicate` 等で
   検索 → **該当0件** (warnings summaryは PyPDF2/on_event 由来のDeprecationWarning 3件のみ、
   collection関連の警告は無し)。
6. **実測**: 同ログ内の5件のERROR全ての発生フェーズを検めた結果、5件悉く
   `ERROR at setup of TestLayoutSave.<method>` (**setup**フェーズ) であり、`ERROR at teardown` は **0件**。
   ⇒ setupエラーは1 collected item = 1 error outcomeで収支が合う (teardownエラーのように
   「1 test で passed+error の2 outcomeを生む」余地は本ログ内に **存在しない**事を確認。

### 結論

**推論**: 上記6項目は、+1の原因として想定し得る代表的な機構 (再実行系plugin・隠れconfig・xpassedカテゴリ・
野良test file・collection時警告・teardownエラーの二重計上) を悉く棄却する。而して、これらを除外した後に
「では何が+1を生んでおるか」を指す**機械的な証拠は本票の手番の範囲内では得られなんだ**。

**理由 (境界による限界)**: 個々の passed/skipped/xfailed test の id 一覧は、full-run を `-v` 等で再実行するか、
`--collect-only` を full-run と同一プロセス内で照合するかしない限り得られぬ。本工区の境界は
「`--collect-only` は base木のみ・一度」「full run 禁」であり、既に許された一度の collect-only は
⑴で使い切っている (二度目は許されぬ)。∴ **これ以上の追跡は本票の手番では為し得ぬ**。

**∴ ㈠は 第四値のまま残す (UNMEASURED)**。指せぬ理由 = 代表的仮説6件を実測で棄却した上で、残る手段
(再度のcollect-onlyまたはfull run) が境界で禁じられて居る為。合わせに行かず、合わぬ (指せぬ) まま報告する。

---

## 判らぬ・第四値 (本票終了時点)

- **㈠**: 未特定のまま (UNMEASURED)。仮説6件棄却済・残る手段は境界外。次の手番で `--collect-only` 追加1回
  または `-v` full run が許されれば、passed/skipped/xfailedの id 単位一覧を base/実走間で機械比較すれば
  特定し得ると見る (**推論**・次の手の提案に過ぎず、本票内の実測ではない)。
- **㈡**: 候補集合 (8件追加・1件削除・正味+7) は実測で確定。内訳が「削除1件=base側passed・追加8件=target側
  全件passed」である事は、base/target集計値からの論理的整合による**推論**であり、target側実行結果の直接実測
  ではない (境界=a1木不触・full run禁ゆえ)。

## 監査発注 (三行・令⑥準拠)

・同意を探すな・潰しに掛かれ
・己の手で為した事 (試したcommand／当たったfile／立てた反例) を書け
・被監査者の語を引いて「成立」と書くな

軍師second へ本票を監査提出する。
